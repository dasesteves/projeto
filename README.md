# Projeto
Repositório criado para a UC Projeto do Mestrado em Bioinformática

## Autores:

- Diogo Esteves & David Henriques

## Tarefas em curso:

- **Revisão da bibliografia e escrita do artigo intercalar** *(prioritário)*
- Protocolo (step-by-step) de como gerar as figuras (R, bioconductor, monocle 3, instalação dos packages, obtenção e carregamento dos datasets, análise estatística e criação das figuras do artigo 2)

### Artigo 2:
[GitHub do Artigo 2, incluindo a pasta "data"](https://github.com/cole-trapnell-lab/sdg-zfish)

#### Para gerar as figuras do artigo 2:  
1. **Obter a pasta "data"** a partir do link do Git supra-mencionado, **colocar a pasta "data" na mesma pasta onde temos o ficheiro R** que vai gerar as figuras (obtido aqui ou no link fornecido antes)
2. Abrir a pasta data e **extrair os ficheiros com terminação .gz**; após este passo, os ficheiros passam a ocupar ***consideravelmente*** mais espaço
3. **Correr código até** obter "erro" e **ser requerido colocar mais datasets**; estes **datasets podem ser obtidos em**: [Zscape Data](https://cole-trapnell-lab.github.io/zscape/)
4. Os datasets após o download precisam ser *extraídos*, e os ficheiros extraídos devem ser colocados na pasta dos ficheiros R (fora da pasta "data") e devem ser renomeados para o nome indicado no comando que deu origem ao erro por falta do dataset (geralmente é só apagar "zscape_" do nome do ficheiro); após este passo, os ficheiros passam a ocupar ***consideravelmente*** mais espaço novamente

**Ps.** este é o método do código funcionar sem fazer grandes alterações; no entanto, pode ser tudo simplificado/otimizado para ser "corrido" mais facilmente.

