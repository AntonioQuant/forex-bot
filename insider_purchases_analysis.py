"""
insider_purchases_analysis.py
Cuando un directivo compra acciones de su propia empresa con su
propio dinero (no ventas, no regalos de acciones, no ejercicio de
opciones), hay literatura que sugiere que precede a un buen
comportamiento del valor -- información privilegiada real, aunque
legal y declarada.

Se filtra por el campo 'Text' de yfinance, buscando "Purchase"
explícito -- excluye "Sale", "Stock Gift", "Conversion of Exercise",
etc. Mismo grupo de empresas que en PEAD, para tener muestra
suficiente (las compras de insiders son mucho más raras que las
ventas, así que hace falta agrupar).

Uso:
    python3 insider_purchases_analysis.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "JPM", "JNJ", "PG", "XOM"]
HORIZONTES = [10, 20, 60]
COSTE_IDA_Y_VUELTA = 0.0005


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def cargar_compras_insiders(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    transacciones = yf.Ticker(ticker).insider_transactions
    if transacciones is None or transacciones.empty:
        return pd.DataFrame(columns=["ticker", "fecha", "shares", "value"])

    es_compra = transacciones["Text"].str.contains("Purchase", case=False, na=False)
    compras = transacciones[es_compra].copy()
    compras["fecha"] = pd.to_datetime(compras["Start Date"]).dt.tz_localize(None).dt.normalize()
    compras["ticker"] = ticker
    return compras[["ticker", "fecha", "Shares", "Value"]].rename(
        columns={"Shares": "shares", "Value": "value"})


def alinear_con_precio(compras: pd.DataFrame, precio_df: pd.DataFrame) -> pd.DataFrame:
    precio_df = precio_df.sort_values("Date").reset_index(drop=True)
    resultados = []
    for _, fila in compras.iterrows():
        candidatos = precio_df[precio_df["Date"] >= fila["fecha"]]
        if candidatos.empty:
            continue
        idx = candidatos.index[0]
        resultados.append({"ticker": fila["ticker"], "fecha": fila["fecha"], "idx_precio": idx})
    return pd.DataFrame(resultados)


if __name__ == "__main__":
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    todos_los_eventos = []

    for ticker in TICKERS:
        print(f"Descargando {ticker}...")
        try:
            precio_df = cargar_precio(ticker)
            compras = cargar_compras_insiders(ticker)
            if compras.empty:
                print(f"  Sin compras de insiders detectadas para {ticker}.")
                continue

            alineado = alinear_con_precio(compras, precio_df)
            for h in HORIZONTES:
                alineado[f"fwd_{h}d"] = alineado["idx_precio"].apply(
                    lambda i: (precio_df["Close"].iloc[i + h] / precio_df["Close"].iloc[i] - 1)
                    if i + h < len(precio_df) else np.nan
                )
            todos_los_eventos.append(alineado)
            print(f"  {len(alineado)} compras de insiders encontradas.")
        except Exception as e:
            print(f"  Error con {ticker}: {type(e).__name__}: {e}")

    if not todos_los_eventos:
        print("\nSin ningún evento detectado en ninguna empresa -- revisa el filtro de 'Text'.")
        raise SystemExit

    df = pd.concat(todos_los_eventos, ignore_index=True)
    print(f"\n{len(df)} compras de insiders en total, {len(TICKERS)} empresas.\n")

    for h in HORIZONTES:
        datos = df.dropna(subset=[f"fwd_{h}d"])
        if len(datos) < 15:
            print(f"+{h}d: muestra insuficiente ({len(datos)})")
            continue
        retornos_brutos = datos[f"fwd_{h}d"].values
        retornos_netos = retornos_brutos - COSTE_IDA_Y_VUELTA
        resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                         n_bootstrap=2000, random_state=h)
        ic_low, ic_high = resultado["intervalo_confianza"]
        print(f"+{h}d: n={len(datos)}  neto={resultado['media_observada']*100:+.3f}%  "
              f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado['significativo']}")

    print("\n--- Aviso ---")
    print("Con una muestra que puede quedarse pequeña (las compras de insiders son raras),")
    print("un resultado no significativo puede deberse tanto a falta de efecto como a falta")
    print("de potencia estadística -- misma cautela que con Piercing Line al principio.")
