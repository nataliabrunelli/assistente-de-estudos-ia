import streamlit as st
import os
from google import genai 
from google.genai import types

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

from datetime import date
import warnings

warnings.filterwarnings("ignore")

# --- Configuração da Página Streamlit ---
st.set_page_config(page_title="Assistente de Estudos AI", layout="wide")

# --- Configuração da API Key ---
api_key_to_use = None
google_api_key_found = False

# 1. PRIMEIRO, tentar carregar das variáveis de ambiente do sistema
#    (Isso é como o Render e outros provedores de PaaS disponibilizam segredos)
api_key_env_var = os.getenv('GOOGLE_API_KEY')
if api_key_env_var:
    api_key_to_use = api_key_env_var
    google_api_key_found = True
   # st.info("API Key carregada a partir das variáveis de ambiente do sistema.") # Opcional para debug
else:
   # st.info("Chave GOOGLE_API_KEY não encontrada nas variáveis de ambiente do sistema. Tentando Segredos do Streamlit...") # Opcional
    pass

# 2. SE NÃO ENCONTRADA nas variáveis de ambiente, TENTAR carregar dos Segredos do Streamlit
#    (Isso é para desenvolvimento local com secrets.toml)
if not google_api_key_found:
    try:
        if 'GOOGLE_API_KEY' in st.secrets: # Esta linha causava o erro se secrets.toml não existisse
            api_key_to_use = st.secrets['GOOGLE_API_KEY']
            google_api_key_found = True
            st.info("API Key carregada a partir dos Segredos do Streamlit.") # Opcional
        else: # Opcional: para debug se a chave não estiver no secrets.toml
            st.info("Chave GOOGLE_API_KEY não encontrada nos Segredos do Streamlit.")
    except FileNotFoundError: # Especificamente para o caso de secrets.toml não existir
        st.info("Arquivo secrets.toml não encontrado (normal em produção).") # Opcional
        pass # É normal o secrets.toml não existir em produção, então apenas continue
    except Exception as e_secrets: # Captura outras exceções de st.secrets, mas não interrompe
        st.warning(f"Erro ao tentar ler os segredos do Streamlit: {e_secrets}. Isso pode ser ignorado em produção se a chave estiver nas variáveis de ambiente.") # Opcional
        pass

# 3. Configurar a API Key se encontrada e definir no os.environ
if google_api_key_found and api_key_to_use:
    os.environ["GOOGLE_API_KEY"] = api_key_to_use
    
else:
    # Esta mensagem de erro agora é mais genérica, pois tentamos os dois métodos
    st.error("ERRO CRÍTICO: GOOGLE_API_KEY não configurada!")
    st.markdown("""
        Verifique se a `GOOGLE_API_KEY` está definida:
        - **No Render (ou similar):** Como uma variável de ambiente nas configurações do seu serviço.
        - **Para desenvolvimento local:** Em um arquivo `.streamlit/secrets.toml`.
    """)
    st.stop()

# -------------------------- TESTE/DEBBUGING DE DEPLOY ---------------
# ... (após a configuração da API Key e genai.configure) ...

st.subheader("--- INÍCIO DO BLOCO DE TESTE DIRETO DA API (VERSÃO DETALHADA) ---")
api_key_para_teste = os.getenv('GOOGLE_API_KEY')

if api_key_para_teste:
    st.info(f"Usando API Key (parcial): {api_key_para_teste[:5]}...{api_key_para_teste[-5:]} para teste direto.")
    try:
        # <<--- MUDE O MODELO AQUI PARA TESTE TAMBÉM --- >>
        MODEL_NAME_FOR_TEST = "gemini-1.0-pro" # TENTE ESTE MODELO
        st.info(f"Modelo para teste direto: {MODEL_NAME_FOR_TEST}")

        # Verifique se a biblioteca genai foi importada e configurada
        if 'genai' not in globals():
            st.error("'genai' (google.generativeai) não foi importado ou configurado globalmente para o teste.")
        else:
            model_test = genai.models(MODEL_NAME_FOR_TEST)
            prompt_de_teste = "Olá, Gemini! Qual é a capital da França? Responda de forma concisa."
            st.info(f"Enviando prompt de teste direto: '{prompt_de_teste}'")

            # Configurações de segurança mais permissivas para depuração
            from google.genai.types import HarmCategory, HarmBlockThreshold
            safety_settings_for_test = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            st.info(f"Usando safety_settings para teste direto: {safety_settings_for_test}")

            response_test = model_test.generate_content(
                prompt_de_teste,
                safety_settings=safety_settings_for_test
            )

            st.info("Resposta do teste direto recebida. Analisando...")

            response_text = ""
            # Acesso ao texto da resposta pode variar um pouco entre versões/modelos
            try:
                response_text = response_test.text
            except Exception as e_text:
                st.warning(f"Não foi possível acessar response_test.text diretamente: {e_text}")
                if hasattr(response_test, 'parts') and response_test.parts:
                    for part in response_test.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text
            
            if response_text:
                st.text_area("TEXTO DA RESPOSTA DO TESTE DIRETO:", response_text, height=100)
            else:
                st.error("NENHUM TEXTO FOI RETORNADO NO TESTE DIRETO.")

            if hasattr(response_test, 'prompt_feedback') and response_test.prompt_feedback:
                st.write("Prompt Feedback do teste direto:", response_test.prompt_feedback)
                if response_test.prompt_feedback.block_reason:
                    st.error(f"BLOQUEIO DO PROMPT no teste direto! Razão: {response_test.prompt_feedback.block_reason_message or response_test.prompt_feedback.block_reason}")
            else:
                st.info("Sem prompt_feedback (ou prompt_feedback vazio) no teste direto.")

            if hasattr(response_test, 'candidates') and response_test.candidates:
                st.write(f"Candidatos do teste direto: {len(response_test.candidates)}")
                for i, candidate in enumerate(response_test.candidates):
                    st.write(f"--- Candidato {i} ---")
                    if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                        candidate_text = "".join(p.text for p in candidate.content.parts if hasattr(p, 'text'))
                        st.write(f"  Texto do Candidato {i}: {candidate_text if candidate_text else 'Sem texto no candidato.'}")
                    else:
                        st.write(f"  Candidato {i} não tem 'content.parts' com texto.")

                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                        finish_reason_name = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                        st.info(f"  Finish Reason do Candidato {i}: {finish_reason_name}")
                        if finish_reason_name == "SAFETY":
                            st.error(f"  RESPOSTA DO CANDIDATO {i} BLOQUEADA POR SEGURANÇA (SAFETY)!")
                    else:
                        st.warning(f"  Candidato {i} sem 'finish_reason'.")
                    
                    if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                        st.write(f"  Safety Ratings do Candidato {i}:", candidate.safety_ratings)
            else:
                st.warning("Nenhum 'candidates' na resposta do teste direto, ou a estrutura é inesperada.")
            
            st.info("Tentando mostrar a estrutura da resposta_test (pode ser útil para depuração):")
            try:
                st.json(str(response_test)) # Tenta mostrar como string se a serialização direta falhar
            except Exception as e_json:
                st.warning(f"Não foi possível serializar response_test para JSON: {e_json}")


    except Exception as e_test_direct:
        st.error(f"EXCEÇÃO NO TESTE DIRETO DA API GEMINI: {type(e_test_direct).__name__} - {e_test_direct}")
        st.error("Isso sugere um problema com a API Key (permissões, validade), o modelo, cotas, ou conectividade do Render para a API do Google.")
        import traceback
        st.text(f"Traceback completo da exceção no teste direto:\n{traceback.format_exc()}")
else:
    st.error("API Key não encontrada para o teste direto.")
st.subheader("--- FIM DO BLOCO DE TESTE DIRETO DA API ---")

# --------------------------------------

# --- Função `call_agent`  ---
def call_agent(agent: Agent, message_text: str, context: dict = None) -> str:
    session_service = InMemorySessionService()
    session_id = f"session_{st.session_state.get('user_session_id', 'default')}"
    user_id = "user_streamlit"

    session = session_service.create_session(app_name=agent.name, user_id=user_id, session_id=session_id)
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)

    try:
        content = types.Content(role="user", parts=[types.Part(text=message_text)])

    except AttributeError as e_attr:
        st.error(f"Erro de atributo ao criar Content/Part com google.genai.types: {e_attr}")
        st.error("Verifique se a biblioteca 'google-genai' está instalada corretamente e se a sintaxe está alinhada com a documentação mais recente.")
        return "Erro crítico: Falha ao construir mensagem para o agente."
    except Exception as e_general:
        st.error(f"Erro inesperado ao criar Content/Part: {e_general}")
        return "Erro crítico: Falha ao construir mensagem para o agente."

    final_response = ""
    try:
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part_item in event.content.parts:
                        if part_item.text is not None:
                            final_response += part_item.text
                            final_response += "\n"
            elif event.error_message:
                st.error(f"Erro no agente {agent.name}: {event.error_message}")
                final_response += f"Erro ao processar: {event.error_message}\n"
    except Exception as e_run:
        st.error(f"Exceção ao executar o agente {agent.name}: {e_run}")
        return f"Ocorreu um erro crítico ao contatar o agente {agent.name}."

    if not final_response.strip():
        return "O agente não produziu uma resposta."
    return final_response

# --- Definições dos Agentes (como no seu código original) ---
def agente_buscador(prova, data_de_hoje):
    buscador = Agent(
        name="agente_buscador",
        model="gemini-2.0-flash", # Usando modelo mais recente, ajuste se necessário
        description="Agente que busca o estilo da prova.",
        tools=[google_search],
        instruction="""
        Você é um especialista em análises de provas. Sua tarefa é investigar e descrever o estilo das questões de uma prova específica.
        Use o Google Search para encontrar informações sobre o formato, características e tendências das questões das provas dos últimos 3 anos, a partir da data atual.
        Sua resposta deve ser uma descrição clara e concisa do estilo da prova, mencionando:
        - Tipo de questões predominantes (ex: múltipla escolha, discursivas, verdadeiro/falso).
        - Nível de complexidade (ex: conceitual, aplicação, análise crítica).
        - Presença de interdisciplinaridade.
        - Se há pegadinhas comuns ou padrões de cobrança.
        Este perfil do estilo é crucial para que outros agentes possam gerar questões coerentes e oferecer dicas eficazes.
        """
    )
    entrada_do_agente_buscador = f"Prova: {prova}\nData de hoje: {data_de_hoje}"
    with st.spinner(f"Buscando estilo da prova {prova}..."):
        estilo = call_agent(buscador, entrada_do_agente_buscador)
    return estilo

def agente_buscador2(prova, materia):
    buscador2 = Agent(
        name="agente_buscador2",
        model="gemini-2.0-flash",
        description="Agente que busca os tópicos mais relevantes da prova.",
        tools=[google_search],
        instruction="""
        Você é um analista de conteúdo de provas e especialista no Princípio de Pareto (80/20).
        Sua missão é identificar os tópicos mais relevantes e de alta incidência para uma prova e matéria específicas.
        Use o Google Search para encontrar informações sobre questões e assuntos cobrados com mais frequência nos últimos anos dessa prova e matéria.
        Aplique o Princípio de Pareto para destilar os 20% dos tópicos que, se dominados, trarão 80% dos resultados esperados.
        Além disso, pesquise por assuntos da atualidade que tenham maior probabilidade de serem cobrados na prova, considerando a matéria.
        O resultado deve ser uma lista clara e numerada dos tópicos mais relevantes, pronta para ser usada por um professor para formular questões.
        """
    )
    entrada_do_agente_buscador2 = f"Prova: {prova}\nMatéria: {materia}"
    with st.spinner(f"Buscando tópicos relevantes para {materia} na prova {prova}..."):
        topicos_relevantes = call_agent(buscador2, entrada_do_agente_buscador2)
    return topicos_relevantes

def agente_professor(estilo_da_prova, topicos_relevantes):
    professor = Agent(
        name="agente_professor",
        model="gemini-2.0-flash",
        description="Agente professor que formula questões",
        instruction="""
        Você é um professor especialista e mestre na formulação de questões de prova.
        Com base no ESTILO DA PROVA e nos TÓPICOS MAIS RELEVANTES fornecidos, sua tarefa é criar 3 questões desafiadoras e no formato da prova para CADA UM dos tópicos listados.
        Assegure que as questões sejam:
        - Claras, objetivas e sem ambiguidades.
        - Abrangentes, cobrindo diferentes aspectos dos tópicos.
        - Totalmente alinhadas ao nível de complexidade e tipo de raciocínio exigido pelo ESTILO DA PROVA.
        Apresente as questões de forma organizada, numerando-as sequencialmente e indicando a qual tópico cada conjunto de 3 questões se refere.
        **IMPORTANTE PARA FORMATAÇÃO DE MÚLTIPLA ESCOLHA:**
        Se a questão for de múltipla escolha, apresente cada alternativa (por exemplo, a), b), c), d), e)) em uma **NOVA LINHA**.
        Exemplo de formatação desejada para uma questão de múltipla escolha:
       [Nome do Tópico em Negrito]

        1. [Enunciado da Pergunta]?
        a) [Alternativa A] 

        b) [Alternativa B]

        c) [Alternativa C]

        d) [Alternativa D]

        e) [Alternativa E]

        Ainda que sejam 3 questões por tópico, a numareção das questões vai de 1-15.
        """
    )
    entrada_do_agente_professor = f"Estilo da prova: {estilo_da_prova}\nTópicos relevantes: {topicos_relevantes}"
    with st.spinner("Gerando questões..."):
        questoes = call_agent(professor, entrada_do_agente_professor)
    return questoes

def agente_professor2(questoes, respostas_aluno):
    professor2 = Agent(
        name="agente_professor2",
        model="gemini-2.0-flash",
        description="Agente professor2 para corrigir e explicar as questões",
        instruction="""
        Você é um professor especialista e um avaliador perspicaz. Sua função é analisar as RESPOSTAS do aluno às QUESTÕES propostas.
        Para cada questão, você deve seguir este formato rigoroso:

        1.  **Avaliação da Resposta:** Indique claramente se a resposta do aluno está `Correta`, `Incorreta` ou `Parcialmente Correta`. Justifique brevemente essa avaliação.
        2.  **Resolução Passo a Passo:** Apresente a solução completa e detalhada para a questão, explicando cada etapa do raciocínio e os conceitos teóricos envolvidos de forma didática. Imagine que você está ensinando a resolução do zero.
        Na medida do possível, passe 'macetes' conhecidos, populares entre os professóres do ensino médio, para ajudar na memorização. 
        Por exemplo: F=m.a é a fórmula da fama; C=2πr é a fórmula do 'catupyri' (catwopiri)...
        3.  **Análise de Desempenho e Dicas Personalizadas:** Com base na resposta do aluno, identifique onde ele errou (seja conceitual, de cálculo, interpretação, etc.) ou onde ele acertou e poderia ter aprofundado. Ofereça dicas de estudo **direcionadas** para as dificuldades observadas, sugerindo:
            - Tópicos específicos para revisão aprofundada.
            - Estratégias para abordar questões similares no futuro.
            - Pontos de atenção para evitar erros comuns.
            - Recursos adicionais, se aplicável (ex: "Revise o conceito X de Y").
        Seu feedback deve ser construtivo, encorajador e focado em guiar o aluno para a melhoria contínua.
        """
    )
    entrada_do_agente_professor2 = f"Questões:\n{questoes}\n\nRespostas do aluno:\n{respostas_aluno}"
    with st.spinner("Corrigindo e analisando suas respostas..."):
        correcao = call_agent(professor2, entrada_do_agente_professor2)
    return correcao

# --- Inicialização do Estado da Sessão ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = "inicio"
if 'prova' not in st.session_state:
    st.session_state.prova = ""
if 'materia' not in st.session_state:
    st.session_state.materia = ""
if 'estilo_prova' not in st.session_state:
    st.session_state.estilo_prova = ""
if 'topicos_relevantes' not in st.session_state:
    st.session_state.topicos_relevantes = ""
if 'questoes_geradas' not in st.session_state:
    st.session_state.questoes_geradas = ""
if 'respostas_usuario' not in st.session_state:
    st.session_state.respostas_usuario = ""
if 'correcao_exercicios' not in st.session_state:
    st.session_state.correcao_exercicios = ""
if 'user_session_id' not in st.session_state: # Para diferenciar chamadas de API
    st.session_state.user_session_id = os.urandom(12).hex()


# --- Lógica da Aplicação UI ---
st.title("🚀 Assistente de Estudos Personalizado 🚀")

data_de_hoje_str = date.today().strftime("%d/%m/%Y")

# ETAPA 1: Escolher Prova e Matéria
if st.session_state.etapa == "inicio":
    st.header("Olá! Vamos configurar seus estudos.")
    st.write(f"Data de hoje: {data_de_hoje_str}")

    prova_input = st.text_input("Para qual prova você quer estudar?", value=st.session_state.get("prova_temp", ""))
    materia_input = st.text_input("Qual matéria você quer estudar primeiro?", value=st.session_state.get("materia_temp", ""))

    if st.button("Iniciar Estudos ✨"):
        if prova_input and materia_input:
            st.session_state.prova = prova_input
            st.session_state.materia = materia_input
            st.session_state.prova_temp = prova_input # Salva para preencher se voltar
            st.session_state.materia_temp = materia_input

            st.session_state.estilo_prova = agente_buscador(st.session_state.prova, data_de_hoje_str)
            if "erro ao processar" in st.session_state.estilo_prova.lower() or "não produziu uma resposta" in st.session_state.estilo_prova.lower() :
                 st.error(f"Não foi possível obter o estilo da prova. Verifique o nome da prova ou tente novamente. Detalhe: {st.session_state.estilo_prova}")
                 st.stop() # Interrompe se o primeiro agente falhar criticamente

            st.session_state.topicos_relevantes = agente_buscador2(st.session_state.prova, st.session_state.materia)
            if "erro ao processar" in st.session_state.topicos_relevantes.lower() or "não produziu uma resposta" in st.session_state.topicos_relevantes.lower():
                 st.error(f"Não foi possível obter os tópicos relevantes. Verifique a matéria ou tente novamente. Detalhe: {st.session_state.topicos_relevantes}")
                 st.stop()

            st.session_state.questoes_geradas = agente_professor(st.session_state.estilo_prova, st.session_state.topicos_relevantes)
            if "erro ao processar" in st.session_state.questoes_geradas.lower() or "não produziu uma resposta" in st.session_state.questoes_geradas.lower():
                 st.error(f"Não foi possível gerar as questões. Tente novamente. Detalhe: {st.session_state.questoes_geradas}")
                 st.stop()

            st.session_state.respostas_usuario = "" # Limpa respostas anteriores
            st.session_state.correcao_exercicios = "" # Limpa correções anteriores
            st.session_state.etapa = "responder_questoes"
            st.rerun()
        else:
            st.warning("Por favor, preencha os campos de prova e matéria.")

# ETAPA 2: Mostrar Informações, Questões e Coletar Respostas
elif st.session_state.etapa == "responder_questoes":
    st.header(f"Estudando para: {st.session_state.prova} - Matéria: {st.session_state.materia}")
    
    with st.expander("Ver Estilo da Prova e Tópicos Relevantes", expanded=False):
        st.subheader("Estilo da Prova:")
        st.markdown(st.session_state.estilo_prova)
        st.subheader("Tópicos Mais Relevantes:")
        st.markdown(st.session_state.topicos_relevantes)

    st.subheader("✍️ Questões Geradas:")
    st.markdown(st.session_state.questoes_geradas)

    st.session_state.respostas_usuario = st.text_area(
        "Digite suas respostas aqui. Procure numerá-las de acordo com as questões.",
        height=300,
        value=st.session_state.respostas_usuario
    )

    if st.button("Enviar Respostas e Corrigir 🧐"):
        if st.session_state.respostas_usuario.strip():
            st.session_state.correcao_exercicios = agente_professor2(
                st.session_state.questoes_geradas,
                st.session_state.respostas_usuario
            )
            st.session_state.etapa = "ver_correcao"
            st.rerun()
        else:
            st.warning("Por favor, escreva suas respostas antes de enviar.")

# ETAPA 3: Mostrar Correção e Opções de Continuação
elif st.session_state.etapa == "ver_correcao":
    st.header("Feedback e Correção 🧑‍🏫")
    st.markdown(st.session_state.correcao_exercicios)

    st.subheader("O que você gostaria de fazer agora?")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Mais Questões (mesma matéria) 🔁"):
            # Gera novas questões para a mesma matéria e prova
            st.session_state.questoes_geradas = agente_professor(
                st.session_state.estilo_prova,
                st.session_state.topicos_relevantes
            )
            st.session_state.respostas_usuario = ""
            st.session_state.correcao_exercicios = ""
            st.session_state.etapa = "responder_questoes"
            st.rerun()
    with col2:
        if st.button("Estudar Outra Matéria 📚"):
            st.session_state.etapa = "nova_materia"
            st.session_state.materia = "" # Limpa matéria anterior
            st.session_state.topicos_relevantes = ""
            st.session_state.questoes_geradas = ""
            st.session_state.respostas_usuario = ""
            st.session_state.correcao_exercicios = ""
            st.rerun()
    with col3:
        if st.button("Encerrar Sessão 👋"):
            st.session_state.etapa = "inicio" # Volta para o início
            st.session_state.prova = ""
            st.session_state.materia = ""
            # Limpa campos temporários para não repopular
            st.session_state.prova_temp = ""
            st.session_state.materia_temp = ""
            st.success("Obrigado por estudar conosco! Até a próxima!")
            st.rerun()


# ETAPA 4: Escolher Nova Matéria (mantendo a prova)
elif st.session_state.etapa == "nova_materia":
    st.header(f"Continuando seus estudos para: {st.session_state.prova}")
    nova_materia_input = st.text_input("Qual nova matéria você quer estudar agora?", value=st.session_state.get("materia_temp_nova",""))

    if st.button("Estudar esta Nova Matéria 🚀"):
        if nova_materia_input:
            st.session_state.materia = nova_materia_input
            st.session_state.materia_temp_nova = nova_materia_input # Salva para preencher

            # Estilo da prova já foi buscado e é o mesmo
            st.session_state.topicos_relevantes = agente_buscador2(st.session_state.prova, st.session_state.materia)
            if "erro ao processar" in st.session_state.topicos_relevantes.lower() or "não produziu uma resposta" in st.session_state.topicos_relevantes.lower():
                 st.error(f"Não foi possível obter os tópicos para a nova matéria. Detalhe: {st.session_state.topicos_relevantes}")
                 # Não para, permite tentar de novo ou voltar
            else:
                st.session_state.questoes_geradas = agente_professor(st.session_state.estilo_prova, st.session_state.topicos_relevantes)
                if "erro ao processar" in st.session_state.questoes_geradas.lower() or "não produziu uma resposta" in st.session_state.questoes_geradas.lower():
                    st.error(f"Não foi possível gerar questões para a nova matéria. Detalhe: {st.session_state.questoes_geradas}")
                else:
                    st.session_state.respostas_usuario = ""
                    st.session_state.correcao_exercicios = ""
                    st.session_state.etapa = "responder_questoes"
                    st.rerun()
        else:
            st.warning("Por favor, insira o nome da nova matéria.")

    if st.button("↩️ Voltar para opções anteriores"):
        st.session_state.etapa = "ver_correcao" # Ou para onde fizer mais sentido
        st.rerun()

# Adiciona um rodapé simples ou informações
st.markdown("---")
st.markdown("Assistente de Estudos v1.0 - Potencializado por Google Gemini e Streamlit.")