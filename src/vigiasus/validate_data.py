
import pandas as pd
import requests


# Códigos oficiais das 27 Unidades da Federação
UFS_VALIDAS = {
    "11", "12", "13", "14", "15", "16", "17",
    "21", "22", "23", "24", "25", "26", "27", "28", "29",
    "31", "32", "33", "35",
    "41", "42", "43",
    "50", "51", "52", "53",
}

COLUNAS_OBRIGATORIAS = [
    "DT_NOTIFIC",
    "ID_MUNICIP",
    "SG_UF_NOT",
]


def validate_data(df: pd.DataFrame) -> None:
    """
    Executa verificações locais de qualidade dos dados.
    Não modifica nem exclui registros.
    """

    print("\n=== VALIDAÇÃO DA QUALIDADE DOS DADOS ===")

    # 1. Verificar estrutura
    colunas_ausentes = set(COLUNAS_OBRIGATORIAS) - set(df.columns)

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {sorted(colunas_ausentes)}"
        )

    print(f"\nTotal de registros: {len(df):,}")
    print(f"Total de colunas: {len(df.columns)}")

    # 2. Verificar valores ausentes
    print("\n1. Valores ausentes:")
    print(df[COLUNAS_OBRIGATORIAS].isna().sum())

    # 3. Verificar tipos de dados
    print("\n2. Tipos das colunas:")
    print(df[COLUNAS_OBRIGATORIAS].dtypes)

    # 4. Verificar período das notificações
    print("\n3. Período das notificações:")

    datas = df["DT_NOTIFIC"]

    if not pd.api.types.is_datetime64_any_dtype(datas):
        raise TypeError(
            "DT_NOTIFIC precisa estar em formato datetime. "
            "Verifique o parse_dates em read_data.py."
        )

    datas_validas = datas.dropna()

    if datas_validas.empty:
        print("Nenhuma data válida encontrada.")
    else:
        print(f"Data inicial: {datas_validas.min()}")
        print(f"Data final: {datas_validas.max()}")

    # 5. Investigar datas fora de 2023
    print("\n4. Notificações fora de 2023:")

    mascara_fora_2023 = (
        datas.notna()
        & datas.dt.year.ne(2023)
    )

    registros_fora_2023 = df.loc[mascara_fora_2023]
    quantidade_fora_2023 = len(registros_fora_2023)

    total_registros = len(df)

    percentual_fora_2023 = (
        quantidade_fora_2023 / total_registros * 100
        if total_registros > 0
        else 0
    )

    print(f"Registros fora de 2023: {quantidade_fora_2023}")
    print(f"Percentual fora de 2023: {percentual_fora_2023:.2f}%")

    if not registros_fora_2023.empty:
        print("Datas fora de 2023 mais frequentes:")
        print(
            registros_fora_2023["DT_NOTIFIC"]
            .value_counts()
            .head(10)
        )

    # 6. Validar códigos de UF
    print("\n5. Códigos de UF:")

    ufs_encontradas = set(
        df["SG_UF_NOT"].dropna().astype(str).unique()
    )

    ufs_invalidas = ufs_encontradas - UFS_VALIDAS

    print(f"UFs distintas encontradas: {len(ufs_encontradas)}")
    print(f"Códigos inválidos: {sorted(ufs_invalidas)}")

    # 7. Verificar formato dos códigos municipais
    print("\n6. Formato dos códigos municipais:")

    codigos = df["ID_MUNICIP"]

    mascara_tamanho_invalido = (
        codigos.notna()
        & codigos.astype("string").str.len().ne(6)
    )

    quantidade_tamanho_invalido = int(
        mascara_tamanho_invalido.sum()
    )

    print(
        "Códigos com tamanho diferente de 6 caracteres: "
        f"{quantidade_tamanho_invalido}"
    )

    print("\n=== FIM DA VALIDAÇÃO LOCAL ===")


def validate_municipalities(df: pd.DataFrame) -> None:
    """
    Compara códigos municipais e UFs com a referência do IBGE.

    O código municipal de seis dígitos é comparado com os
    seis primeiros dígitos do código oficial de sete dígitos.
    """

    print("\n=== VALIDAÇÃO MUNICIPAL PELO IBGE ===")

    url = (
        "https://servicodados.ibge.gov.br/"
        "api/v1/localidades/municipios"
    )

    # 1. Consultar a API com tratamento de erros
    try:
        resposta = requests.get(url, timeout=(10, 30))
        resposta.raise_for_status()
        municipios_ibge = resposta.json()

    except requests.Timeout as erro:
        print(f"ERRO: tempo limite excedido ao consultar o IBGE: {erro}")
        print("Validação municipal não concluída.")
        return

    except requests.RequestException as erro:
        print(f"ERRO de comunicação com o IBGE: {erro}")
        print("Validação municipal não concluída.")
        return

    except ValueError as erro:
        print(f"ERRO: a resposta do IBGE não contém JSON válido: {erro}")
        print("Validação municipal não concluída.")
        return

    # 2. Conferir o formato da resposta
    if not isinstance(municipios_ibge, list):
        print("ERRO: a API retornou um formato inesperado.")
        print("Validação municipal não concluída.")
        return

    if not municipios_ibge:
        print("ERRO: a API não retornou municípios.")
        print("Validação municipal não concluída.")
        return

    # 3. Construir a referência municipal.
    # Não dependemos de microrregião ou mesorregião,
    # que podem ser None na resposta da API.
    referencia = {}

    try:
        for municipio in municipios_ibge:
            codigo_ibge = str(municipio["id"])

            if (
                not codigo_ibge.isdigit()
                or len(codigo_ibge) != 7
            ):
                raise ValueError(
                    f"Código IBGE inesperado: {codigo_ibge}"
                )

            codigo_municipal = codigo_ibge[:6]
            codigo_uf = codigo_ibge[:2]

            referencia[codigo_municipal] = codigo_uf

    except (KeyError, TypeError, ValueError) as erro:
        print(f"ERRO ao interpretar a resposta do IBGE: {erro}")
        print("Validação municipal não concluída.")
        return

    # 4. Selecionar combinações distintas e completas
    combinacoes = (
        df[["ID_MUNICIP", "SG_UF_NOT"]]
        .dropna()
        .drop_duplicates()
    )

    combinacoes["ID_MUNICIP"] = (
        combinacoes["ID_MUNICIP"].astype(str)
    )

    combinacoes["SG_UF_NOT"] = (
        combinacoes["SG_UF_NOT"].astype(str)
    )

    # 5. Comparar códigos municipais com o IBGE
    codigos_invalidos = []
    ufs_incompativeis = []

    for codigo, uf_informada in combinacoes.itertuples(
        index=False, name=None
    ):
        uf_esperada = referencia.get(codigo)

        if uf_esperada is None:
            codigos_invalidos.append(codigo)

        elif uf_esperada != uf_informada:
            ufs_incompativeis.append(
                (codigo, uf_informada, uf_esperada)
            )

    # 6. Apresentar resultados
    print(f"Municípios na referência do IBGE: {len(referencia)}")
    print(
        "Códigos municipais distintos não encontrados: "
        f"{len(set(codigos_invalidos))}"
    )
    print(
        "Combinações município/UF incompatíveis: "
        f"{len(ufs_incompativeis)}"
    )

    if codigos_invalidos:
        print(
            "Exemplos de códigos não encontrados:",
            sorted(set(codigos_invalidos))[:10],
        )

    if ufs_incompativeis:
        print(
            "Exemplos (código, UF informada, UF esperada):",
            ufs_incompativeis[:10],
        )

    print("\n=== FIM DA VALIDAÇÃO MUNICIPAL ===")


if __name__ == "__main__":
    from vigiasus.read_data import read_data

    try:
        df = read_data()
        validate_data(df)
        validate_municipalities(df)

    except FileNotFoundError as erro:
        print(f"ERRO: arquivo não encontrado: {erro}")

    except (ValueError, TypeError) as erro:
        print(f"ERRO de validação: {erro}")
