# Usa uma imagem leve do Python 3.10
FROM python:3.10-slim

# Define /app como diretório de trabalho
WORKDIR /app

# Copia só o requirements primeiro (cache de layer)
COPY app/requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da sua pasta app
COPY app/ .

# Expõe a porta 80 (o FastAPI vai rodar nela)
EXPOSE 80

# Comando padrão usando o Uvicorn para rodar o FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]