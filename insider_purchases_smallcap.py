"""
insider_purchases_smallcap.py
Misma metodología exacta que insider_purchases_analysis.py, esta vez
con empresas medianas/pequeñas en vez de megacapitalizaciones -- ahí
es donde la literatura sugiere que las compras de insiders son más
frecuentes y más significativas (los directivos de grandes tecnológicas
cobran sobre todo en acciones ya asignadas, rara vez compran más con
su propio dinero; en empresas más pequeñas, comprar sí es una apuesta
personal real).

Selección: bancos regionales, industriales y consumo de mediana
capitalización, con propiedad a menudo más concentrada en fundadores
o directivos de toda la vida.

Uso:
    python3 insider_purchases_smallcap.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKERS = ["WAL", "PB", "CVBF", "AAON", "CR", "PLXS", "CIEN", "DIOD",
           "CROX", "TECH", "STAG", "WSC", "CALM", "UFPI", "MLI"]
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
        print("\nSin ningún evento detectado en ninguna empresa.")
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
    print("Si esta vez la muestra es suficiente pero sigue sin significancia, es una respuesta")
    print("honesta de verdad, no un problema de diseño. Si la muestra sigue siendo pequeña,")
    print("confirma que el fenómeno es raro incluso ampliando el universo -- también es información.")
