DASHBOARD DE VENDAS 2020

Aluna: Raffaela Forasteira
Modalidade: trabalho individual (1 aluna)

EXECUCAO LOCAL:
1. Instalar Python 3.10+.
2. pip install -r requirements.txt
3. python app.py
4. Abrir http://127.0.0.1:8050

PUBLICACAO RENDER:
1. Subir estes arquivos em repositorio GitHub.
2. No Render, criar Web Service a partir do repositorio.
3. Build: pip install -r requirements.txt
4. Start: gunicorn app:server --bind 0.0.0.0:$PORT
5. Aguardar deploy e testar todos os filtros.

LINK PUBLICO: https://dashboard-vendas-2020-29iv.onrender.com/

OBSERVACOES:
- Dados de 2020 da planilha original fornecida.
- O estado MINAS e normalizado para MG apenas na exibicao.
- Estado e cidade sao filtros encadeados; cidade atualiza ao escolher estado.
- Os filtros globais afetam cinco visualizacoes e indicadores.
- O deploy e o link publico NAO foram realizados automaticamente.
