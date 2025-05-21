# 🤖 Assistente de Estudos Inteligente com IA Gemini (Imersão IA Alura)

## ✨ Visão Geral do Projeto
Este projeto, originado na Imersão de Inteligência Artificial da Alura, evoluiu para um Assistente de Estudos personalizado, agora com uma interface de usuário web interativa desenvolvida com Streamlit e deployado no Streamlit Community Cloud. O objetivo central é auxiliar estudantes na preparação para vestibulares e concursos, otimizando o estudo através da aplicação da lógica de agentes de IA e do princípio de Pareto (80/20).

O assistente foca nos tópicos mais relevantes e no estilo de questões da prova e matéria escolhidas pelo usuário. Utilizando a API Gemini do Google e o Agent Development Kit (ADK), ele analisa o perfil da prova, identifica os conteúdos mais cobrados, gera questões personalizadas e oferece feedback detalhado. Uma característica notável deste projeto é que grande parte da sua lógica de agentes e a interface de usuário foram desenvolvidas e refinadas com o auxílio de modelos de Inteligência Artificial, incluindo o próprio Google Gemini.

## 🚀 Experimente Online!

Você pode interagir com o Assistente de Estudos diretamente no seu navegador:

[*Assistente de Estudos Inteligente*](https://assistentedeestudos.streamlit.app/)

*(Observação: Pode levar alguns instantes para o aplicativo carregar pela primeira vez, especialmente se estiver hibernando.)*

## ⚙️ Como Executar Localmente (Para Desenvolvimento)

Siga estes passos para executar o projeto em seu ambiente local:

1.  **Pré-requisitos:**
    *   Python 3.9 ou superior instalado.
    *   Git instalado.
    *   Uma chave da API do Google Gemini.

2.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/nataliabrunelli/assistente-de-estudos-ia.git
    cd assistente-de-estudos-is
    ```

3.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    python -m venv venv
    # Windows (PowerShell): .\venv\Scripts\Activate.ps1
    # Windows (CMD): venv\Scripts\activate.bat
    # macOS/Linux: source venv/bin/activate
    ```

4.  **Instale as Dependências:**
    O arquivo `requirements.txt` contém todas as bibliotecas necessárias. 
    ```bash
    pip install -r api/requirements.txt
    ```

5.  **Configure sua Chave da API do Google para Desenvolvimento Local:**
    *   Na pasta onde o `streamlit_app.py` está localizado ( `api/`), crie uma subpasta chamada `.streamlit`.
    *   Dentro de `api/.streamlit/`, crie um arquivo chamado `secrets.toml`.
    *   Adicione sua chave da API ao arquivo `secrets.toml`:
        ```toml
        GOOGLE_API_KEY = "SUA_CHAVE_API_AQUI"
        ```

6.  **Execute o Aplicativo Streamlit:**
    ```bash
    streamlit run api/streamlit_app.py
    ```

## 🎯 Funcionalidades Principais

1.  **Interface Web Interativa:** Desenvolvida com Streamlit para uma experiência de usuário amigável.
2.  **Configuração Personalizada:** O usuário informa a prova e a matéria de estudo.
3.  **Análise de Estilo da Prova:** O `agente_buscador` investiga o formato, complexidade e tendências das questões da prova.
4.  **Identificação de Tópicos Relevantes (Pareto):** O `agente_buscador2` aplica o Princípio de Pareto para focar nos 20% dos tópicos que historicamente trazem 80% dos resultados.
5.  **Geração de Questões Contextualizadas:** O `agente_professor` cria questões desafiadoras alinhadas ao estilo da prova e aos tópicos relevantes.
6.  **Correção e Feedback Construtivo:** O `agente_professor2` analisa as respostas do aluno, fornece a resolução passo a passo e dicas personalizadas.
7.  **Fluxo de Estudo Adaptável:** Permite solicitar mais questões ou mudar de matéria.

## 🛠️ Tecnologias Utilizadas

*   **Python:** Linguagem de programação principal.
*   **Streamlit:** Framework para a interface de usuário web.
*   **Google Gemini API:** Modelo de linguagem para as capacidades de IA dos agentes.
*   **Google ADK (Agent Development Kit):** Framework para a criação e orquestração dos agentes.
*   **Google Search (via ADK tools):** Para pesquisa web dos agentes.
*   **Streamlit Community Cloud:** Plataforma para deploy gratuito do aplicativo.
*   **Git & GitHub:** Para versionamento de código.
*   **Docker:** Para conteinerização da aplicação e deploy alternativo.

## ⚙️ Como Funciona (Arquitetura dos Agentes)

O sistema é orquestrado por um aplicativo Streamlit que gerencia o estado da sessão e interage com quatro agentes de IA especializados:

*   **`agente_buscador`:** Investiga e descreve o estilo das questões da prova.
*   **`agente_buscador2`:** Identifica os tópicos mais relevantes da matéria para a prova, aplicando Pareto.
*   **`agente_professor`:** Cria 3 questões por tópico relevante, no formato e estilo da prova.
*   **`agente_professor2`:** Corrige as respostas do aluno, explica a resolução e oferece dicas.

A lógica principal no `streamlit_app.py` guia o usuário através das etapas, chamando os agentes apropriados e exibindo suas saídas.

## 🚀 Próximos Passos e Melhorias Futuras

*   Permitir que o usuário responda a cada questão individualmente abaixo dela.
*   Se as questões forem de múltipla escolha, permitir que o usuário clique na alternativa.
*   Implementar a capacidade de analisar diretamente editais e provas em formato PDF.
*   Permitir que o usuário escolha o nível de dificuldade das questões geradas.
*   Implementar um sistema para salvar e acompanhar o desempenho do aluno (exigiria persistência de dados).
*   Integrar a busca por materiais de estudo complementares para tópicos com dificuldade.
*   Aprimorar o tratamento de erros e o feedback ao usuário.

## 💡 Processo de Desenvolvimento e o Papel da IA
Este projeto é um exemplo prático da colaboração homem-máquina. A ideia inicial e a estrutura básica dos agentes surgiram da Imersão IA da Alura. Subsequentemente, modelos de linguagem como o Google Gemini foram amplamente utilizados para:
*   Gerar e refinar os prompts dos agentes.
*   Desenvolver a lógica da interface de usuário com Streamlit.
*   Auxiliar na depuração de código Python e configurações de deploy.
*   Gerar documentação, como este README.
A jornada de deploy, em particular, foi um intenso processo iterativo de tentativa, erro e aprendizado, onde a capacidade de diagnóstico da IA foi crucial para superar os desafios de compatibilidade de ambientes e dependências.

## 🙏 Agradecimentos
*   À Alura e ao Google pela Imersão de Inteligência Artificial, que inspirou este projeto.
*   À comunidade de desenvolvedores e às ferramentas de IA que tornaram este projeto possível.

---
*Este README foi gerado e refinado com o auxílio de IA, espelhando a natureza do próprio projeto.*
