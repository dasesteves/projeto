#!/usr/bin/env bash
# Merge OpenCode baseURL / model / API key into llm-webui/.env without printing secrets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT}/.env"
EXAMPLE="${ROOT}/.env.example"

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$EXAMPLE" "$ENV_FILE"
  echo "Created $ENV_FILE from .env.example"
fi

redact() {
  local v="$1"
  local n=${#v}
  if (( n <= 4 )); then echo "(len=$n)"; else echo "...${v: -4} (len=$n)"; fi
}

BASE_URL=""
MODEL=""
API_KEY=""
SOURCE=""

# 1) Project / user JSON configs
for cand in \
  "${OPENCODE_CONFIG:-}" \
  "$HOME/.config/opencode/opencode.json" \
  "$HOME/.config/opencode/config.json" \
  "$ROOT/../opencode.json" \
  "$PWD/opencode.json"
do
  [[ -n "$cand" && -f "$cand" ]] || continue
  SOURCE="$cand"
  # naive JSON extract via python
  eval "$(python3 - "$cand" <<'PY'
import json,sys,re
p=sys.argv[1]
data=json.load(open(p))
base=model=""
# top-level model like "siu/Qwen..."
m=data.get("model") or ""
if isinstance(m,str) and "/" in m:
    model=m.split("/",1)[1]
elif isinstance(m,str):
    model=m
prov=data.get("provider") or {}
if isinstance(prov,dict):
    for pid,pcfg in prov.items():
        if not isinstance(pcfg,dict): continue
        opts=pcfg.get("options") or {}
        if isinstance(opts,dict) and opts.get("baseURL"):
            base=opts["baseURL"]
        models=pcfg.get("models") or {}
        if isinstance(models,dict) and models and not model:
            model=next(iter(models))
print(f"BASE_URL={base!r}")
print(f"MODEL={model!r}")
PY
)"
  break
done

# 2) Legacy auth.json
AUTH_JSON="${XDG_DATA_HOME:-$HOME/.local/share}/opencode/auth.json"
if [[ -f "$AUTH_JSON" ]]; then
  SOURCE="${SOURCE:+$SOURCE; }$AUTH_JSON"
  eval "$(python3 - "$AUTH_JSON" <<'PY'
import json,sys
data=json.load(open(sys.argv[1]))
key=""
# shapes vary: {provider: {apiKey: ...}} or list
def walk(o):
    global key
    if isinstance(o,dict):
        for k,v in o.items():
            if k.lower() in ("apikey","api_key","key","token") and isinstance(v,str) and len(v)>8:
                key=v; return
            walk(v)
    elif isinstance(o,list):
        for i in o: walk(i)
walk(data)
print(f"API_KEY={key!r}")
PY
)"
fi

# 3) V2 sqlite credentials (best-effort; schema may vary)
DB="${XDG_DATA_HOME:-$HOME/.local/share}/opencode/opencode.db"
if [[ -f "$DB" ]] && command -v sqlite3 >/dev/null 2>&1; then
  SOURCE="${SOURCE:+$SOURCE; }$DB"
  # try common table/column names without failing hard
  ROW="$(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table';" 2>/dev/null || true)"
  if echo "$ROW" | grep -qi credential; then
    CAND="$(sqlite3 "$DB" "SELECT typeof(api_key), length(api_key), substr(api_key,-4) FROM credential LIMIT 1;" 2>/dev/null || \
           sqlite3 "$DB" "SELECT typeof(key), length(key), substr(key,-4) FROM credential LIMIT 1;" 2>/dev/null || true)"
    # Prefer dumping via python for actual value into env only
    VAL="$(python3 - "$DB" <<'PY' 2>/dev/null || true
import sqlite3,sys
con=sqlite3.connect(sys.argv[1])
cur=con.cursor()
tabs=[r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
for t in tabs:
    if 'cred' not in t.lower(): continue
    cols=[r[1] for r in cur.execute(f'PRAGMA table_info({t})')]
    for c in cols:
        if c.lower() in ('api_key','apikey','key','token','secret','value'):
            try:
                row=cur.execute(f'SELECT {c} FROM {t} LIMIT 5').fetchall()
            except Exception:
                continue
            for (v,) in row:
                if isinstance(v,str) and len(v)>8:
                    print(v); raise SystemExit
                if isinstance(v,(bytes,bytearray)) and len(v)>8:
                    print(v.decode('utf-8','ignore')); raise SystemExit
print('')
PY
)"
    if [[ -n "${VAL:-}" ]]; then API_KEY="$VAL"; fi
  fi
fi

upsert() {
  local key="$1" val="$2"
  [[ -n "$val" ]] || return 0
  if grep -qE "^${key}=" "$ENV_FILE"; then
    # replace in place
    python3 - "$ENV_FILE" "$key" "$val" <<'PY'
import sys
path,key,val=sys.argv[1],sys.argv[2],sys.argv[3]
lines=open(path).read().splitlines()
out=[]; found=False
for line in lines:
    if line.startswith(key+"="):
        out.append(f"{key}={val}"); found=True
    else:
        out.append(line)
if not found: out.append(f"{key}={val}")
open(path,"w").write("\n".join(out)+"\n")
PY
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

upsert OPENAI_API_BASE_URL "$BASE_URL"
upsert OPENAI_API_MODEL "$MODEL"
upsert OPENAI_API_KEY "$API_KEY"

echo "OpenCode import summary (secrets redacted):"
echo "  sources: ${SOURCE:-none found}"
echo "  OPENAI_API_BASE_URL: ${BASE_URL:-"(unchanged/empty)"}"
echo "  OPENAI_API_MODEL: ${MODEL:-"(unchanged/empty)"}"
if [[ -n "$API_KEY" ]]; then
  echo "  OPENAI_API_KEY: present $(redact "$API_KEY")"
else
  echo "  OPENAI_API_KEY: not found — paste into .env manually"
fi
echo "Wrote updates to $ENV_FILE"
