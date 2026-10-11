from pathlib import Path
import pandas as pd
import zipfile

DADOS_ZIPADOS = Path(__file__).resolve().parents[2] / "data" / "raw" / "dengue_2023.csv.zip"

if not DADOS_ZIPADOS.exists():
    raise FileNotFoundError(f'Arquivo {__file__} não foi encontrado !')


def read_data() -> pd.DataFrame:
    """
    função que lê a variável que abre o arquivo csv
    dentro da pasta zipada e copia pra uma variavel em dataframe
    """
    with zipfile.ZipFile(file=DADOS_ZIPADOS, mode="r") as zip_ref:
        data = zip_ref.open("DENGBR23.csv")
        df = pd.read_csv(
            data, sep=",",
            usecols=["DT_NOTIFIC", "ID_MUNICIP", "SG_UF_NOT"], 
            parse_dates=["DT_NOTIFIC"],
            dtype={
                "ID_MUNICIP": str,
                "SG_UF_NOT": str}
                )
            
    return df

if __name__ == "__main__":
    df = read_data()
    print("\nExibindo o DataFrame\n")
    print(df.head())
    print("\n  Leitura Completa ✅")

