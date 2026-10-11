from pathlib import Path

import requests


URL_DADOS = (
    "https://s3.sa-east-1.amazonaws.com/"
    "ckan.saude.gov.br/SINAN/Dengue/csv/DENGBR23.csv.zip"
)


def baixar_dados():
    raiz_projeto = Path(__file__).resolve().parents[2]

    pasta_destino = raiz_projeto / "data" / "raw"
    pasta_destino.mkdir(parents=True, exist_ok=True)

    arquivo_destino = pasta_destino / "dengue_2023.csv.zip"

    print("Iniciando download dos dados de dengue...")

    with requests.get(
        URL_DADOS,
        stream=True,
        timeout=(10, 120),
    ) as resposta:
        resposta.raise_for_status()

        with open(arquivo_destino, "wb") as arquivo:
            for bloco in resposta.iter_content(
                chunk_size=1024 * 1024
            ):
                if bloco:
                    arquivo.write(bloco)

    print("Download concluído!")
    print(f"Arquivo salvo em: {arquivo_destino}")


if __name__ == "__main__":
    baixar_dados()