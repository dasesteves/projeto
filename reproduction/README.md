# Reproduzir a agregação, os gráficos das tabelas, a PCA e os UMAPs

Este percurso separado executa uma parte delimitada da análise: agregação de
estimativas do modelo, gráficos das tabelas, normalização, PCA global e UMAPs
para 18, 24, 36, 48 e 72h.
Não substitui o artigo, os notebooks ou as figuras académicas, nem reproduz todos
os métodos do projeto (por exemplo, Monocle e Slingshot).

## Escolher o percurso

- **Só os quatro gráficos e as tabelas:** seguir [esta secção](#gráficos-das-estimativas-e-da-abundância-celular).
  Não exige a matriz de contagens, a PCA nem os UMAPs.
- **Agregação, PCA e UMAPs:** seguir a sequência completa abaixo.

## Antes de começar

- Windows x64 e Python 3.10 ou superior. O Python não é instalado por este conjunto.
- Windows PowerShell (`powershell.exe`), usado para verificar a assinatura do R.
- Internet para obter o instalador R, os pacotes e os dados públicos.
- Memória e disco **do percurso PCA/UMAP**: validado num computador com 32 GB de RAM; o objeto R chega a
  cerca de 6 GB, além de memória temporária. Os downloads e dados descomprimidos
  ocupam cerca de 4 GB; reservar espaço adicional para R, biblioteca e resultados.
  Estes valores não são requisitos mínimos dos gráficos das tabelas; não foi
  medido um mínimo de memória para esse módulo.
- Usar uma consola normal, sem privilégios de administrador. Escolher pastas
  novas fora do repositório. Os comandos recusam destinos existentes.

## Executar

Obter o projeto com Git ou com **Code → Download ZIP** no GitHub e extrair o
arquivo. Abrir o PowerShell na pasta `reproduction` (onde está `run.py`).
Confirmar `python --version`: é necessário Python 3.10 ou superior. Se o comando
não existir ou abrir a Microsoft Store, instalar Python de python.org antes de
prosseguir; se apenas `py -3` funcionar, usá-lo em vez de `python` em todos os comandos.

Os exemplos usam `C:/repro`; substituir esse prefixo por uma pasta com permissão
de escrita, mantendo-o consistente. Colocar caminhos entre aspas se tiverem espaços.
Não usar uma pasta já ocupada por outra execução.

Se já houver R 4.6.1 x64 instalado, podem omitir-se os dois primeiros comandos e
usar o caminho explícito desse `Rscript.exe`. A biblioteca de pacotes continua
separada. Uma segunda instalação pode atualizar o registo de desinstalação da
primeira; não é necessário instalar outra cópia só para executar esta análise.

```powershell
python download_exact.py runtime --output C:/repro/installer
python install_r_windows.py --installer C:/repro/installer/R-4.6.1-win.exe --output C:/repro/runtime
python download_exact.py packages --output C:/repro/packages
python download_exact.py data --output C:/repro/data
python restore_windows.py --rscript C:/repro/runtime/R-4.6.1/bin/Rscript.exe --archives C:/repro/packages --library C:/repro/library
python run.py environment --rscript C:/repro/runtime/R-4.6.1/bin/Rscript.exe --library C:/repro/library --output C:/repro/check
python run.py aggregate --input-dir C:/repro/data --output C:/repro/aggregate
python run.py pca --rscript C:/repro/runtime/R-4.6.1/bin/Rscript.exe --library C:/repro/library --input-dir C:/repro/data --output C:/repro/pca
python run.py umap --rscript C:/repro/runtime/R-4.6.1/bin/Rscript.exe --library C:/repro/library --pca C:/repro/pca/isolated-global-pca.rds --output C:/repro/umap
```

**Executar um comando de cada vez e parar se falhar.** Consultar o recibo e os
logs na pasta de destino; uma pasta parcial não é uma execução válida.
Os downloads exigem os hashes exatos: não substituir versões para ultrapassar
uma indisponibilidade. O instalador R verifica também a assinatura.

R é instalado por utilizador, sem alterar PATH nem criar atalhos; o instalador
regista a desinstalação no Windows e pode atualizar essa entrada de outra cópia
R 4.6.1. Não é uma distribuição portátil sem registo. Não requer RStudio ou
Rtools para o percurso com os binários Windows registados.

## O que consultar no fim

- `aggregate/mean-model-estimates.csv`: médias das estimativas, não expressão medida.
- `pca/`: controlos das células/metadados, normalização e PCA global de 20 componentes.
- `umap/umap-reproduction/`: coordenadas CSV, objetos RDS e cinco figuras PNG.
- `receipt.json`: deve indicar `completed` nas etapas `environment`, `aggregate`,
  `pca` e `umap`. Downloads usam `download-receipt.json`; instalação R usa
  `runtime-receipt.json`, ambos com estado `verified`.
- O restauro de pacotes não produz recibo próprio: só prosseguir após `environment`
  passar e `check/package-check.csv` confirmar as 135 versões.

Se algum comando falhar, parar: consultar o erro e os logs, corrigir a causa e
usar um destino novo apenas para a etapa falhada. Não é necessário repetir
etapas anteriores que terminaram com sucesso. Se faltar uma versão no servidor,
não instalar a mais recente como substituição: o hash tem de coincidir.

## Gráficos das estimativas e da abundância celular

Esta etapa é independente da PCA e dos UMAPs. Usa apenas os dois CSV já
incluídos em `Scripts/Saunders Rep/data`, com hashes verificados; não precisa de
descarregar as matrizes de contagens. Reutiliza o R e a biblioteca preparados
acima. Manter a estrutura do projeto: não copiar apenas a pasta `reproduction`.

**Se ainda não preparou o ambiente**, abrir o PowerShell na pasta `reproduction`
e executar apenas estes comandos, um de cada vez (Python 3.10+ é necessário):

```powershell
python download_exact.py runtime --output C:/repro/installer
python install_r_windows.py --installer C:/repro/installer/R-4.6.1-win.exe --output C:/repro/runtime
python download_exact.py packages --output C:/repro/packages
python restore_windows.py --rscript C:/repro/runtime/R-4.6.1/bin/Rscript.exe --archives C:/repro/packages --library C:/repro/library
```

Substituir `C:/repro` por uma pasta sua. Se R 4.6.1 já existe, omitir os dois
primeiros comandos e usar esse `Rscript.exe`. Se a biblioteca isolada já estiver
restaurada, reutilizá-la; não repetir downloads/restauros. Este módulo verifica
as 135 versões do ambiente partilhado, embora use diretamente apenas uma parte
dos pacotes. Não precisa de executar `download_exact.py data` nem `run.py`.
A instalação do R tem os efeitos no registo do Windows descritos acima.

Na pasta `reproduction`, executar:

```powershell
python estimates_abundance.py --rscript C:/repro/runtime/R-4.6.1/bin/Rscript.exe --library C:/repro/library --output C:/repro/estimates-abundance
```

O comando verifica as versões, gera quatro PNG e as tabelas CSV e confere os
cálculos independentemente com Python. Usar uma pasta de destino nova. Em caso
de falha, consultar os logs; não considerar uma pasta parcial como válida.

- `receipt.json`: deve indicar `completed`.
- `figures-tables/validation.json`: deve indicar `passed`.
- `figures-tables/estimates-by-time.png` e `estimates-ranking.png`: médias do
  campo `estimate`, com tabelas por gene/tempo e ranking verificável.
- `figures-tables/abundance-by-time.png` e `abundance-by-group.png`: CV da
  abundância e distribuição de `cv_test_stat`, com linhas de origem e medianas.

### Encontrar e conferir as saídas

Os PNG e CSV deste módulo **não estão disponíveis para abrir nesta página**:
são criados no teu computador pelo comando acima. Com o exemplo apresentado,
abre `C:/repro/estimates-abundance/figures-tables` no Explorador de Ficheiros.
Os PNG abrem num visualizador de imagens; os CSV podem ser consultados num
editor de texto ou numa folha de cálculo (separador vírgula, decimal ponto).
Preservar `NA` como ausência, não como zero. Não guardar alterações sobre os
CSV usados para a verificação.

| Gráfico PNG | Tabela CSV para conferir | O que representa |
| --- | --- | --- |
| `estimates-by-time.png` | `estimates-by-time.csv` | Média de `estimate` por gene e tempo; 59 combinações observadas e 36 ausentes. |
| `estimates-ranking.png` | `estimates-ranking-top10.csv` e `estimates-ranking-all.csv` | Ordenação pela média de todas as linhas selecionadas de cada gene. |
| `abundance-by-time.png` | `abundance-selected-times.csv` | CV da abundância, ajuste e limites já fornecidos, em quatro tempos. |
| `abundance-by-group.png` | `abundance-all-filtered.csv` e `abundance-group-summary.csv` | Distribuição de `cv_test_stat` e medianas das 64 classes. |

Todos estes ficheiros ficam em `figures-tables`. `estimate-source-rows.csv`
permite rastrear as médias; `source_row` conta as linhas de dados do CSV de
origem a partir de 1, excluindo o cabeçalho. `log-scale-audit.csv` documenta a
validade dos valores para as escalas logarítmicas. Confirma primeiro os estados
`completed` e `passed` indicados acima; uma pasta parcial não é um resultado válido.

**São estimativas e estatísticas fornecidas pelo estudo, não expressão génica
medida nem novos resultados biológicos.** As 36 combinações gene/tempo ausentes
ficam NA. O ranking pondera igualmente as linhas de origem, não os tempos.
A abundância abrange todas as classes elegíveis, não apenas pigmentação.
Nenhum modelo é reajustado; os limites da faixa vêm da tabela e o limiar de p
é nominal. As figuras são novas apresentações, não substituições das académicas.
[Interpretação, rastreabilidade e limites completos](estimates-abundance/LEIA-ME.txt).

## Evidência e limites

O percurso foi executado com R 4.6.1, 135 versões de pacotes fixadas, downloads
novos e uma biblioteca nova. A agregação e as coordenadas coincidiram com a
reprodução moderna anterior no mesmo Windows. **Não se demonstrou equivalência
numérica com as figuras históricas nem portabilidade para outro sistema.**

A PCA preserva 22 757 células, incluindo 1 323 sem tempo. Os cinco UMAPs usam
337, 2 059, 3 926, 4 928 e 3 297 células. São projeções separadas: os eixos não
constituem um sistema temporal comum. Não há imputação dos tempos ausentes.

Dados e código de origem: Saunders e colaboradores, série pública
[GSE202639](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202639).
O percurso deriva de [Saunders_rep.Rmd](../Scripts/Saunders%20Rep/Saunders_rep.Rmd),
na revisão `1f80c994a6cab28ccc108b44fefed76361b1e3a0`. Preservam-se as
[atribuições académicas](../README.md#autoria-e-fontes); nenhuma licença nova
ou autoria dos dados é atribuída por este conjunto.

Detalhes: [instruções completas](LEIA-ME.txt), [validação](VALIDACAO.txt),
[versões](versions.csv), [origens e hashes dos dados](data-downloads.json).
As matrizes grandes descarregadas, os instaladores, as bibliotecas e as saídas
não estão incluídos neste conjunto. Os dois CSV das estimativas e da abundância
já pertencem ao repositório académico e são reutilizados sem alteração.
