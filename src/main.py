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


def main():
    # ==================================================
    # EXTRACT
    # ==================================================
    dados = extract_all()

    # ==================================================
    # TRANSFORM – DIMENSÕES BASE
    # ==================================================
    paciente = transform_paciente(dados.get("paciente"))
    medico = transform_medico(dados.get("medico"))
    especialidade = transform_especialidade(dados.get("especialidade"))

    # ==================================================
    # DIMENSÕES DERIVADAS
    # ==================================================
    dim_leito = criar_dim_leito(dados.get("internamento"))
    dim_tipo_cirurgia = criar_dim_tipo_cirurgia(dados.get("cirurgia"))
    dim_motivo_internamento = criar_dim_motivo_internamento(dados.get("internamento"))

    # Verificação preventiva
    if dim_tipo_cirurgia is None:
        print("Aviso: dim_tipo_cirurgia não foi criada.")
    if dim_motivo_internamento is None:
        print("Aviso: dim_motivo_internamento não foi criada.")

    # ==================================================
    # TRANSFORM – TABELAS FATO
    # ==================================================
    fato_consulta = transformar_fato_consulta(dados.get("consulta"))

    fato_cirurgia = None
    if dim_tipo_cirurgia is not None:
        fato_cirurgia = transformar_fato_cirurgia(
            dados.get("cirurgia"), dim_tipo_cirurgia
        )
    else:
        print("Fato cirurgia não criada por ausência de dimensão.")

    fato_internamento = None
    if dim_motivo_internamento is not None:
        fato_internamento = transformar_fato_internamento(
            dados.get("internamento"), dim_motivo_internamento
        )
    else:
        print("Fato internamento não criada por ausência de dimensão.")

    # ==================================================
    # DIMENSÃO TEMPO
    # ==================================================
    dim_tempo = criar_dim_tempo(fato_consulta, fato_cirurgia, fato_internamento)

    print("Transformações concluídas.")
    print(f"Dimensão tempo criada com {len(dim_tempo)} registos.")

    # ==================================================
    # LOAD
    # ==================================================
    load_all(
        paciente,
        medico,
        especialidade,
        dim_leito,
        dim_tipo_cirurgia,
        dim_motivo_internamento,
        dim_tempo,
        fato_consulta,
        fato_cirurgia,
        fato_internamento,
    )

    print("Pipeline ETL completo executado com sucesso.")


if __name__ == "__main__":
    main()
