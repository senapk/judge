Funcionalidades do indexador
- github.com/senapk/indexer
- rodar no root do repositório
- controlado pelo arquivo config.ini
- pode ser utilizado para alterar os títulos, tags e categorias das questões
- Na primeira linha do arquivo Readme de cada problema estão codificados
    - Nome da questão ©categoria #tags
- O indexador é utilizado para:
    - gerar um readme ordenando as questões por categorias, tags
    - gerar um TOC
    - gerar links simbólicos para busca por título usando Control-P
    - Atualizar os .html usando o `pandoc`
    - Atualizer os .vpl usando o `tk`
    - Gerar um board para
        - overview de todos os headers
        - permitir alterar os headers através do board

