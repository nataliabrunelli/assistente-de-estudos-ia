# 1. Use uma imagem base Python "slim"
FROM python:3.11-slim-bullseye

# 2. Defina variáveis de ambiente para otimizar o pip e Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Adiciona o diretório de scripts do usuário ao PATH
    # Isso é crucial se o pip instalar scripts em ~/.local/bin
    PATH="/home/app/.local/bin:${PATH}"

# 3. Crie um usuário não-root e defina o diretório de trabalho
# É melhor criar o WORKDIR antes de mudar o USER para que o WORKDIR pertença ao root inicialmente
# e depois o USER app possa escrever nele se necessário, ou usamos --chown no COPY.
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app

# 4. Copie APENAS o arquivo de dependências primeiro
# Copie para um local temporário ou direto para /app, mas o WORKDIR é /app
COPY api/requirements.txt /app/api/requirements.txt

# 5. Instale as dependências COMO ROOT
# Isso garante que os pacotes e seus scripts sejam instalados em locais do sistema
# que estão no PATH por padrão (ex: /usr/local/bin), evitando os warnings e
# problemas de "comando não encontrado".
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# 6. Copie o restante do código da sua aplicação e mude a propriedade para o usuário 'app'
COPY --chown=app:app api/ /app/api/

# 7. Mude para o usuário não-root para executar a aplicação
USER app

# 8. Exponha a porta que o Streamlit usa
EXPOSE 8501

# 9. Comando para rodar o aplicativo Streamlit
# O usuário 'app' executará este comando.
CMD ["streamlit", "run", "/app/api/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]