from extract import extract_all

from transform import (
    transform_paciente,
    transform_medico,
    transform_especialidade,
    transformar_fato_consulta,
    transformar_fato_cirurgia,
    transformar_fato_internamento,
    criar_dim_tempo,
    criar_dim_leito,
    criar_dim_tipo_cirurgia,
    criar_dim_motivo_internamento,
)

from load import load_all
from export import exportar_sql, exportar_csv, exportar_excel
from logs import logging


def _mostrar_erro_para_utilizador(error):
    """Mostra erros no CLI com orientação para disponibilizar o MySQL."""
    mensagem = str(error)
    print(f"❌ {mensagem}")

    if (
        "MySQL indisponível" in mensagem
        or "Can't connect to MySQL server" in mensagem
        or "Connection refused" in mensagem
    ):
        print(
            "ℹ️ O banco MySQL não está disponível. "
            "Disponibilize o serviço MySQL e valide host/porta/credenciais no .env."
        )


def montar_dataframes_transformados():
    """Executa Extract e Transform retornando dataframes prontos para carga/exportação."""
    dados = extract_all()

    paciente = transform_paciente(dados.get("paciente"))
    medico = transform_medico(dados.get("medico"))
    especialidade = transform_especialidade(dados.get("especialidade"))

    dim_leito = criar_dim_leito(dados.get("internamento"))
    dim_tipo_cirurgia = criar_dim_tipo_cirurgia(dados.get("cirurgia"))
    dim_motivo_internamento = criar_dim_motivo_internamento(dados.get("internamento"))

    fato_consulta = transformar_fato_consulta(dados.get("consulta"))
    fato_cirurgia = transformar_fato_cirurgia(dados.get("cirurgia"), dim_tipo_cirurgia)
    fato_internamento = transformar_fato_internamento(dados.get("internamento"), dim_motivo_internamento)
    dim_tempo = criar_dim_tempo(fato_consulta, fato_cirurgia, fato_internamento)

    total_transformado = sum(
        len(df)
        for df in [
            paciente,
            medico,
            especialidade,
            dim_leito,
            dim_tipo_cirurgia if dim_tipo_cirurgia is not None else None,
            dim_motivo_internamento if dim_motivo_internamento is not None else None,
            dim_tempo,
            fato_consulta,
            fato_cirurgia,
            fato_internamento,
        ]
        if df is not None
    )
    logging.info(f"✅ Transform concluído — {total_transformado} registros limpos")

    return {
        "dim_paciente": paciente,
        "dim_medico": medico,
        "dim_especialidade": especialidade,
        "dim_leito": dim_leito,
        "dim_tipo_cirurgia": dim_tipo_cirurgia,
        "dim_motivo_internamento": dim_motivo_internamento,
        "dim_tempo": dim_tempo,
        "fato_consulta": fato_consulta,
        "fato_cirurgia": fato_cirurgia,
        "fato_internamento": fato_internamento,
    }


def executar_pipeline_completo(dataframes):
    """Executa a carga no MySQL para todas as dimensões e fatos."""
    total = load_all(
        dataframes["dim_paciente"],
        dataframes["dim_medico"],
        dataframes["dim_especialidade"],
        dataframes["dim_leito"],
        dataframes["dim_tipo_cirurgia"],
        dataframes["dim_motivo_internamento"],
        dataframes["dim_tempo"],
        dataframes["fato_consulta"],
        dataframes["fato_cirurgia"],
        dataframes["fato_internamento"],
    )
    logging.info(f"✅ Pipeline ETL concluído — {total} registros carregados")


def menu():
    """Exibe menu interativo e aciona as operações do pipeline."""
    while True:
        print("\n┌─────────────────────────────────┐")
        print("│  Pipeline ETL — IONA Hospital   │")
        print("├─────────────────────────────────┤")
        print("│  [1] Executar pipeline completo │")
        print("│  [2] Exportar como SQL          │")
        print("│  [3] Exportar como CSV          │")
        print("│  [4] Exportar como Excel        │")
        print("│  [5] Executar tudo              │")
        print("│  [0] Sair                       │")
        print("└─────────────────────────────────┘")

        opcao = input("Escolha: ").strip()

        if opcao == "0":
            print("Encerrado.")
            break

        dataframes = montar_dataframes_transformados()

        try:
            if opcao == "1":
                executar_pipeline_completo(dataframes)
            elif opcao == "2":
                exportar_sql(dataframes)
            elif opcao == "3":
                exportar_csv(dataframes)
            elif opcao == "4":
                exportar_excel(dataframes)
            elif opcao == "5":
                executar_pipeline_completo(dataframes)
                exportar_sql(dataframes)
                exportar_csv(dataframes)
                exportar_excel(dataframes)
            else:
                print("Opção inválida.")
        except Exception as error:
            _mostrar_erro_para_utilizador(error)


if __name__ == "__main__":
    menu()
