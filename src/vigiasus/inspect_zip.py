from pathlib import Path

DADOS_ZIPADOS = Path(__file__).resolve().parents[2] / "data" / "raw" / "dengue_2023.csv.zip"

def inspect_zip():
    """
    Inspeciona o arquivo ZIP de dados de dengue e retorna informações sobre seu conteúdo.

    Retorna:
        dict: Um dicionário contendo informações sobre o arquivo ZIP, incluindo:
            - 'nome_arquivo': Nome do arquivo ZIP.
            - 'tamanho_bytes': Tamanho do arquivo em bytes.
            - 'arquivos_internos': Lista de nomes dos arquivos contidos no ZIP.
    """
    import zipfile

    if not DADOS_ZIPADOS.exists():
        raise FileNotFoundError(f"O arquivo {DADOS_ZIPADOS} não foi encontrado.")

    with zipfile.ZipFile(DADOS_ZIPADOS, 'r') as zip_ref:
        arquivos_internos = zip_ref.namelist()
        tamanho_bytes = DADOS_ZIPADOS.stat().st_size

    return {
        "nome_arquivo": DADOS_ZIPADOS.name,
        "tamanho_bytes": tamanho_bytes,
        "arquivos_internos": arquivos_internos
    }

if __name__ == "__main__":
    resultado = inspect_zip()
    print(resultado)