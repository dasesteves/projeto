**Português** · [English](README.en.md)

# Resultados e visualizações

Figuras do projeto de transcriptómica de células de pigmentação de peixe-zebra. Para os métodos, contexto e interpretação, consulta o [artigo final](../Artigo%20Final.pdf).

Para gerar novas saídas numa pasta separada, segue o [percurso de reprodução](../reproduction/README.md). As imagens desta galeria são históricas e não são substituídas por essas saídas.

Os UMAPs por tempo são projeções independentes: posições e distâncias entre mapas não representam trajetórias celulares. A reprodução atual verifica o cálculo, não acrescenta conclusões biológicas.

Para as estimativas e a variabilidade da abundância celular, o [módulo de quatro gráficos e tabelas](../reproduction/README.md#gráficos-das-estimativas-e-da-abundância-celular) explica a execução e a interpretação. Os novos PNG e CSV são gerados na pasta escolhida no teu computador; não estão nesta galeria histórica.

As [contagens e mapas da referência](../reproduction/README.md#contagens-e-mapas-da-referência) têm um percurso próprio: os seis PNG e três CSV são gerados localmente em `reference-maps/figures-tables`, usando o destino dos exemplos. Desenham coordenadas pré-calculadas num fundo comum, ao contrário dos UMAPs recalculados separadamente por tempo. Não substituem as imagens abaixo, não reproduzem o boxplot por `Oligo` e não demonstram equivalência com as figuras históricas.

## Uma visualização histórica

[![Estimativas de um modelo para grupos celulares pigmentares, por gene e tempo](expression_of_genes_in_pigment_cells_over_time.png)](expression_of_genes_in_pigment_cells_over_time.png)

Figura original do trabalho, preservada com o título e os eixos da entrega académica. Abre a imagem para ampliar as legendas e consulta a nota abaixo para distinguir o cálculo realizado da interpretação original.

## Origem e limites desta figura

O [notebook Saunders_rep.Rmd](https://github.com/dasesteves/projeto/blob/ce928997ab677c6ab3442ca9221aebfedb1f158b/Scripts/Saunders%20Rep/Saunders_rep.Rmd#L223) permite seguir o cálculo:

1. **Entrada:** `zperturb_beta_bin_results_broadtype_clean.csv`. A cópia comprimida guardada no projeto é idêntica à [fonte do estudo de Saunders e colaboradores](https://github.com/cole-trapnell-lab/sdg-zfish/blob/4fa0bf88dc642b58f1b2a3b7789143e3f44a824a/data/zperturb_beta-bin_results_broadtype_clean.csv.gz). Contém resultados de modelos de abundância celular diferencial, não uma matriz de contagens de RNA.
2. **Seleção e cálculo:** grupos em `cell_group` cujo nome contém `phore` ou `pigmented`, sem distinguir maiúsculas; média de `estimate` por `gene1` e `timepoint`. Este bloco não aplica um filtro explícito de fatores de transcrição.
3. **Saída:** gráfico de linhas e pontos, com tempo ordenado numericamente e uma cor por `gene1`. O código grava `output/expression_of_genes_in_pigment_cells_over_time.png` com 10 × 10 polegadas e 1200 dpi. O nome e a resolução correspondem à figura publicada; as cópias em `Results` e nas fontes do artigo são idênticas.

**Como ler:** o eixo original diz “Mean Expression”, mas o valor calculado é a média de estimativas beta-binomiais. Não equivale a expressão génica média calculada diretamente das contagens de RNA. O [código de origem do estudo](https://github.com/cole-trapnell-lab/sdg-zfish/blob/4fa0bf88dc642b58f1b2a3b7789143e3f44a824a/figure_code/Saunders_Srivatsan_2023_Fig3.R#L69) identifica estes dados como resultados de abundância celular diferencial.

**Contribuição e limites:** o projeto de Diogo Esteves utiliza dados e código do estudo de Saunders e colaboradores; o [artigo final é assinado por Diogo Esteves e David Henriques](https://github.com/dasesteves/projeto/blob/ce928997ab677c6ab3442ca9221aebfedb1f158b/LateX%20files/Artigo%20Final.tex#L18). Esta nota documenta a cadeia encontrada nas fontes. A agregação foi entretanto reexecutada no percurso separado e comparada com o cálculo original. Não há registo do ambiente da execução académica original nem foi validada a interpretação biológica da agregação destas estimativas. A imagem e o artigo históricos permanecem inalterados.

## Consultar todas as figuras

- **Outras consultas das visualizações históricas:** [gráfico temporal](expression_of_genes_in_pigment_cells_over_time.png), [gráfico de barras](top_10_genes_expressed_in_pigment_cells.png) e [animação](gene_expression_evolution.gif).
- **UMAP das células de pigmentação:** [18 h](umap_pigment_cells_18h.png), [24 h](umap_pigment_cells_24h.png), [36 h](umap_pigment_cells_36h.png), [48 h](umap_pigment_cells_48h.png) e [72 h](umap_pigment_cells_72h.png).
- **Outras projeções UMAP:** [24 h](fig_umap_24h.png), [48 h](fig_umap_48h.png) e [72 h](fig_umap_72h.png).
- **Células de referência:** [gráfico de barras](fig1_reference_cells_barplot.png) e [boxplot](fig2_reference_cells_boxplot.png).
- **Variância:** [comparação entre tempos](variancia_tempos.png) e [boxplot global](varianciatotal_boxplot.png).

Os ficheiros mantêm-se tal como foram publicados no projeto. Algumas figuras têm texto e pontos pequenos à escala do navegador; a imagem original permite ampliar. Esta galeria facilita a consulta e não acrescenta resultados ou validação científica.

[Voltar ao projeto](../README.md) · [Scripts e condições de reprodução](../Scripts/)
