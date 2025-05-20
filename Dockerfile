# 1. Use uma imagem base Python "slim"
# Imagens "slim" são menores que as padrão porque omitem alguns pacotes e ferramentas
# que geralmente não são necessários em produção. Alpine é ainda menor, mas pode ter
# problemas de compatibilidade com algumas bibliotecas Python que dependem de C.
# python:3.11-slim-bullseye ou python:3.10-slim-bullseye são boas escolhas.
FROM python:3.11-slim-bullseye

# 2. Defina variáveis de ambiente para otimizar o pip e Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# 3. Crie um usuário não-root para rodar a aplicação (melhor prática de segurança)
RUN addgroup --system app && adduser --system --ingroup app app
USER app

# 4. Defina o diretório de trabalho
WORKDIR /app

# 5. Copie APENAS o arquivo de dependências primeiro
# Isso aproveita o cache do Docker. Se requirements.txt não mudar,
# a camada de instalação de dependências não será reconstruída.
# Assumindo que seu requirements.txt está em api/
COPY --chown=app:app api/requirements.txt /app/api/

# 6. Instale as dependências
# O RUN é executado como root temporariamente para instalar pacotes do sistema se necessário,
# mas o pip install será feito com as permissões do usuário 'app' se possível,
# ou você pode precisar instalar como root e depois mudar a propriedade.
# Para simplicidade aqui, vamos instalar como root e depois garantir que 'app' pode executar.
# Se precisar de pacotes do sistema (ex: para compilar algo), instale-os ANTES do pip install.
# Ex: RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
# (O exemplo acima é se você precisasse de gcc e postgresql dev headers)

# A instalação das dependências Python
RUN pip install -r /app/api/requirements.txt

# 7. Copie o restante do código da sua aplicação
# --chown garante que o usuário 'app' seja o proprietário dos arquivos
COPY --chown=app:app api/ /app/api/

# 8. Exponha a porta que o Streamlit usa
EXPOSE 8501

# 9. Comando para rodar o aplicativo Streamlit
# O usuário 'app' executará este comando.
# Escuta em todas as interfaces (0.0.0.0) e na porta correta.
CMD ["streamlit", "run", "/app/api/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]