import argparse, concurrent.futures, datetime, gzip, hashlib, json, pathlib, urllib.request
KIT = pathlib.Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def fetch(item, target):
    final = target / item['file']
    part = final.with_name(final.name + '.part')
    record = dict(item)
    try:
        if not item['url'].startswith('https://'): raise ValueError('HTTPS required')
        with urllib.request.urlopen(item['url'], timeout=180) as response, part.open('xb') as out:
            record['resolved_url'] = response.geturl()
            for block in iter(lambda: response.read(1024*1024), b''): out.write(block)
        record['actual_sha256'] = digest(part)
        record['bytes'] = part.stat().st_size
        if record['actual_sha256'] != item['sha256']: raise ValueError('SHA-256 mismatch')
        part.rename(final)
        if 'unpack' in item:
            unpacked = target / item['unpack']
            temporary = unpacked.with_name(unpacked.name + '.part')
            with gzip.open(final, 'rb') as src, temporary.open('xb') as out:
                for block in iter(lambda: src.read(1024*1024), b''): out.write(block)
            record['unpacked_sha256'] = digest(temporary)
            if record['unpacked_sha256'] != item['unpacked_sha256']: raise ValueError('Unpacked SHA-256 mismatch')
            temporary.rename(unpacked)
        record['status'] = 'verified'
    except Exception as exc:
        record['status'] = 'failed'
        record['error'] = str(exc)
    return record

def main():
    p = argparse.ArgumentParser(description='Download exact public inputs; never use a local cache or substitute versions.')
    p.add_argument('kind', choices=['packages','data','runtime'])
    p.add_argument('--output', required=True, type=pathlib.Path)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    items = json.loads((KIT / {'packages':'windows-packages.json','data':'data-downloads.json','runtime':'r-runtime.json'}[args.kind]).read_text(encoding='utf-8-sig'))
    receipt = {'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'kind':args.kind, 'status':'running', 'cache_used':False, 'files':[]}
    path = args.output / 'download-receipt.json'
    def save(): path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding='utf-8')
    save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4 if args.kind == 'packages' else 2) as pool:
        jobs = [pool.submit(fetch, item, args.output) for item in items]
        for job in concurrent.futures.as_completed(jobs):
            record = job.result(); receipt['files'].append(record); save()
            print(record['status'], record['file'], record.get('error',''), flush=True)
    receipt['status'] = 'verified' if all(x['status']=='verified' for x in receipt['files']) else 'failed'
    receipt['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat(); save()
    return 0 if receipt['status'] == 'verified' else 1

if __name__ == '__main__': raise SystemExit(main())
