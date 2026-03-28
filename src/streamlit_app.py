import streamlit as st
from pathlib import Path

from config import LOG_PATH
from export import exportar_csv, exportar_excel, exportar_sql
from main import executar_pipeline_completo, montar_dataframes_transformados

st.set_page_config(page_title="Pipeline ETL — IONA Hospital", layout="wide")

NOMES_AMIGAVEIS = {
    "dim_paciente": "Pacientes",
    "dim_medico": "Médicos",
    "dim_especialidade": "Especialidades",
    "dim_leito": "Leitos",
    "dim_tipo_cirurgia": "Tipos de Cirurgia",
    "dim_motivo_internamento": "Motivos de Internamento",
    "dim_tempo": "Calendário (Tempo)",
    "fato_consulta": "Consultas",
    "fato_cirurgia": "Cirurgias",
    "fato_internamento": "Internamentos",
}


def nome_amigavel(nome_tabela):
    """Retorna nome amigável para exibição na interface."""
    return NOMES_AMIGAVEIS.get(nome_tabela, nome_tabela.replace("_", " ").title())


def obter_logs_recentes(linhas=50):
    """Lê os logs recentes do arquivo de log."""
    try:
        if not LOG_PATH.exists():
            return "Nenhum log disponível."

        with open(LOG_PATH, "r", encoding="utf-8") as file:
            conteudo = file.readlines()

        ultimos_logs = conteudo[-linhas:] if len(conteudo) > linhas else conteudo
        return "".join(ultimos_logs)
    except Exception:
        return "Erro ao ler logs."


@st.cache_data(show_spinner=False)
def _obter_resumo(dataframes):
    """Retorna resumo com total de linhas por dataframe."""
    return {
        nome: (0 if df is None else len(df))
        for nome, df in dataframes.items()
    }


def carregar_dataframes():
    """Executa extract+transform e guarda resultado na sessão."""
    try:
        with st.spinner("Executando Extract + Transform..."):
            dataframes = montar_dataframes_transformados()

        st.session_state["dataframes"] = dataframes
        st.success("✅ Transform concluído")

        with st.expander("📋 Detalhes do Transform", expanded=False):
            logs = obter_logs_recentes(100)
            st.code(logs, language="plaintext")
    except Exception as error:
        st.error(f"Erro ao montar dataframes: {error}")


def obter_dataframes_sessao():
    """Retorna os dataframes em sessão, carregando quando necessário."""
    if "dataframes" not in st.session_state:
        carregar_dataframes()
    return st.session_state.get("dataframes", {})


def render_resumo(dataframes):
    """Renderiza métricas e pré-visualização das tabelas."""
    if not dataframes:
        st.info("Nenhum dataframe disponível.")
        return

    resumo = _obter_resumo(dataframes)

    st.subheader("Resumo dos DataFrames")
    colunas = st.columns(3)
    for index, (nome, total) in enumerate(resumo.items()):
        colunas[index % 3].metric(label=nome_amigavel(nome), value=int(total))

    st.subheader("Pré-visualização")
    opcoes_tabelas = list(dataframes.keys())
    opcoes_exibicao = {nome_amigavel(nome): nome for nome in opcoes_tabelas}

    tabela_exibicao = st.selectbox(
        "Selecione a tabela",
        list(opcoes_exibicao.keys())
    )
    tabela = opcoes_exibicao[tabela_exibicao]
    dataframe = dataframes.get(tabela)

    if dataframe is None or dataframe.empty:
        st.warning(f"{nome_amigavel(tabela)} está vazia.")
    else:
        st.dataframe(dataframe.head(50), use_container_width=True)


def mostrar_erro_para_utilizador(error):
    """Exibe erro na interface com orientação para disponibilizar o MySQL."""
    mensagem = str(error)
    st.error(f"❌ {mensagem}")

    if (
        "MySQL indisponível" in mensagem
        or "Can't connect to MySQL server" in mensagem
        or "Connection refused" in mensagem
    ):
        st.warning(
            "MySQL não está disponível. Disponibilize o serviço do banco MySQL "
            "e verifique as credenciais/host/porta no arquivo .env."
        )


st.title("Pipeline ETL — IONA Hospital")
st.caption("Interface Streamlit para execução do ETL, carga no MySQL e exportações.")

with st.sidebar:
    st.header("Operações")

    if st.button("[1] Executar pipeline completo", use_container_width=True):
        dataframes = obter_dataframes_sessao()
        try:
            with st.spinner("Carregando dados no MySQL..."):
                executar_pipeline_completo(dataframes)
            st.success("✅ Load concluído no MySQL")
        except Exception as error:
            mostrar_erro_para_utilizador(error)

    if st.button("[2] Exportar como SQL", use_container_width=True):
        dataframes = obter_dataframes_sessao()
        try:
            exportar_sql(dataframes)
            st.success("✅ SQL exportado")
        except Exception as error:
            st.error(f"Erro ao exportar SQL: {error}")

    if st.button("[3] Exportar como CSV", use_container_width=True):
        dataframes = obter_dataframes_sessao()
        try:
            exportar_csv(dataframes)
            st.success("✅ CSV exportado")
        except Exception as error:
            st.error(f"Erro ao exportar CSV: {error}")

    if st.button("[4] Exportar como Excel", use_container_width=True):
        dataframes = obter_dataframes_sessao()
        try:
            exportar_excel(dataframes)
            st.success("✅ Excel exportado")
        except Exception as error:
            st.error(f"Erro ao exportar Excel: {error}")

    if st.button("[5] Executar tudo", use_container_width=True):
        dataframes = obter_dataframes_sessao()
        try:
            with st.spinner("Executando ETL completo + exportações..."):
                executar_pipeline_completo(dataframes)
                exportar_sql(dataframes)
                exportar_csv(dataframes)
                exportar_excel(dataframes)
            st.success("✅ ETL e exportações concluídos")
        except Exception as error:
            mostrar_erro_para_utilizador(error)

    if st.button("Atualizar dados (Extract + Transform)", use_container_width=True):
        carregar_dataframes()

    st.divider()
    with st.expander("📊 Logs em Tempo Real", expanded=False):
        st.caption("Últimos eventos do pipeline")
        logs = obter_logs_recentes(50)
        st.code(logs, language="plaintext")

render_resumo(obter_dataframes_sessao())
