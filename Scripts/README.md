**Português** · [English](README.en.md)

# Scripts

Notebooks e código para processamento, análise e visualização de dados de transcriptómica de célula única de células de pigmentação de peixe-zebra.

Para executar a agregação, a PCA global e os cinco UMAPs, começa pelo [percurso de reprodução verificado](../reproduction/README.md). Esta pasta conserva os notebooks académicos; não é o ponto de partida desse percurso.

## Conteúdo

- **analise_remota_scripts.Rmd:** análise remota de dados de transcriptómica de célula única.
- **memory_optimization_scripts.Rmd:** técnicas de otimização de memória para conjuntos de dados de RNA-seq de célula única de grande dimensão.
- **UMAP_simple.Rmd:** redução de dimensionalidade com UMAP.
- **[Saunders Rep](Saunders%20Rep/):** notebook, saída HTML guardada e ficheiros de apoio à análise baseada no estudo de Saunders e colaboradores.

## Condições de reprodução

São notebooks de análise; não está documentada uma ordem única de execução para toda a pasta. Lê as secções de configuração e carregamento de dados do notebook que pretendes utilizar.

- `UMAP_simple.Rmd` instala pacotes R e Python, descarrega dados do GEO e usa o documento ativo do RStudio para definir a pasta de trabalho. Referencia `raw_counts` sem carregar esse objeto e inspeciona `cell_metadata` antes da respetiva secção de carregamento. Exige, por isso, preparação antes de executar numa sessão nova.
- O [notebook Saunders](Saunders%20Rep/) usa caminhos relativos `data/` e `output/`. O respetivo README documenta a pasta de trabalho e as dependências necessárias.
- As versões históricas destes notebooks não estão estabelecidas. O percurso separado fixa as suas próprias [versões de reprodução](../reproduction/versions.csv); não são uma reconstrução do ambiente académico original.

O percurso separado foi executado e comparado com a reprodução moderna anterior; isso não valida todos os notebooks desta pasta nem demonstra equivalência numérica com os resultados históricos. Alguns scripts podem exigir memória e capacidade de processamento consideráveis; consulta também os cabeçalhos de cada script.

[Voltar ao projeto](../README.md) · [Resultados e limitações](../Results/)
