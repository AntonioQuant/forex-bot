"""
pead_analysis.py
Post-Earnings Announcement Drift: cuando una empresa bate (o falla)
las expectativas de beneficios de los analistas, el precio no lo
incorpora de golpe -- sigue derivando en la misma dirección durante
semanas. Una de las anomalías mejor replicadas de las finanzas,
documentada desde 1968.

Agrupamos varias empresas grandes y líquidas de sectores distintos
para tener potencia estadística real -- una sola acción da solo
~46 trimestres de histórico, insuficiente por sí sola.

Metodología: para cada sorpresa de beneficios, se mide el retorno
desde el cierre del día de la publicación (o el siguiente día de
trading disponible) hasta H días después. Se separan sorpresas
positivas de negativas.

Uso:
    python3 pead_analysis.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "JPM", "JNJ", "PG", "XOM"]
HORIZONTES = [5, 20, 60]
COSTE_IDA_Y_VUELTA = 0.0005


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def cargar_sorpresas(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    earnings = yf.Ticker(ticker).get_earnings_dates(limit=60)
    earnings = earnings.dropna(subset=["Surprise(%)"]).copy()
    earnings = earnings.reset_index()
    earnings["Earnings Date"] = pd.to_datetime(earnings["Earnings Date"]).dt.tz_localize(None).dt.normalize()
    earnings["ticker"] = ticker
    return earnings[["ticker", "Earnings Date", "Surprise(%)"]]


def alinear_con_precio(sorpresas: pd.DataFrame, precio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Empareja cada fecha de resultados con el siguiente día de trading
    disponible en el precio (los resultados suelen publicarse fuera de
    horario de mercado, así que la reacción se ve en la sesión
    siguiente, no necesariamente ese mismo día).
    """
    precio_df = precio_df.sort_values("Date").reset_index(drop=True)
    resultados = []
    for _, fila in sorpresas.iterrows():
        candidatos = precio_df[precio_df["Date"] >= fila["Earnings Date"]]
        if candidatos.empty:
            continue
        idx = candidatos.index[0]
        resultados.append({
            "ticker": fila["ticker"],
            "fecha_resultados": fila["Earnings Date"],
            "sorpresa_pct": fila["Surprise(%)"],
            "idx_precio": idx,
        })
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
            sorpresas = cargar_sorpresas(ticker)
            alineado = alinear_con_precio(sorpresas, precio_df)

            for h in HORIZONTES:
                alineado[f"fwd_{h}d"] = alineado["idx_precio"].apply(
                    lambda i: (precio_df["Close"].iloc[i + h] / precio_df["Close"].iloc[i] - 1)
                    if i + h < len(precio_df) else np.nan
                )

            todos_los_eventos.append(alineado)
        except Exception as e:
            print(f"  Error con {ticker}: {type(e).__name__}: {e}")

    df = pd.concat(todos_los_eventos, ignore_index=True)
    print(f"\n{len(df)} eventos de resultados en total, {len(TICKERS)} empresas.\n")

    sorpresa_positiva = df[df["sorpresa_pct"] > 0]
    sorpresa_negativa = df[df["sorpresa_pct"] < 0]
    print(f"Sorpresas positivas: {len(sorpresa_positiva)}  |  Sorpresas negativas: {len(sorpresa_negativa)}\n")

    for nombre, subset in [("SORPRESA POSITIVA (batió expectativas)", sorpresa_positiva),
                            ("SORPRESA NEGATIVA (falló expectativas)", sorpresa_negativa)]:
        print(f"=== {nombre} ===")
        for h in HORIZONTES:
            datos = subset.dropna(subset=[f"fwd_{h}d"])
            if len(datos) < 15:
                print(f"  +{h}d: muestra insuficiente ({len(datos)})")
                continue
            retornos_brutos = datos[f"fwd_{h}d"].values
            retornos_netos = retornos_brutos - COSTE_IDA_Y_VUELTA
            resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                             n_bootstrap=2000, random_state=h)
            ic_low, ic_high = resultado["intervalo_confianza"]
            print(f"  +{h}d: n={len(datos)}  neto={resultado['media_observada']*100:+.3f}%  "
                  f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado['significativo']}")
        print()

    print("--- Cómo leer esto ---")
    print("PEAD predice: sorpresa positiva -> deriva alcista continuada; sorpresa negativa ->")
    print("deriva bajista continuada, ambas más marcadas con el tiempo (60d > 20d > 5d).")
    print("6 tests en total (3 horizontes x 2 grupos) -- misma cautela de siempre ante resultados aislados.")
