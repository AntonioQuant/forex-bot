"""
ema_pullback_stability.py
El único horizonte significativo (+20d) de la vuelta a tendencia EMA,
comprobado por sub-periodos -- mismo método de 6 tramos que ya hemos
aplicado a los shocks del S&P 500 y a Harami/Piercing.

Uso:
    python3 ema_pullback_stability.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
EMA_FAST = 21
EMA_SLOW = 55
HORIZONTE = 20
N_TRAMOS = 6
COSTE_IDA_Y_VUELTA = 0.0005


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def detectar_pullback(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = df["Close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["Close"].ewm(span=EMA_SLOW, adjust=False).mean()

    tendencia_alcista = df["ema_fast"] > df["ema_slow"]
    ayer_bajo_ema_fast = df["Close"].shift(1) < df["ema_fast"].shift(1)
    hoy_sobre_ema_fast = df["Close"] > df["ema_fast"]

    df["es_pullback_entry"] = tendencia_alcista & ayer_bajo_ema_fast & hoy_sobre_ema_fast
    df[f"fwd_{HORIZONTE}d"] = df["Close"].shift(-HORIZONTE) / df["Close"] - 1
    return df


def split_cronologico(df: pd.DataFrame, n: int):
    size = len(df) // n
    chunks = []
    for i in range(n):
        start = i * size
        end = (i + 1) * size if i < n - 1 else len(df)
        chunks.append(df.iloc[start:end].reset_index(drop=True))
    return chunks


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_pullback(precio_df)
    print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")

    tramos = split_cronologico(df, N_TRAMOS)

    print(f"=== ESTABILIDAD: VUELTA A TENDENCIA EMA, +{HORIZONTE}D, POR TRAMOS ===\n")
    resumen = []
    for idx, tramo in enumerate(tramos, start=1):
        fecha_ini, fecha_fin = tramo["Date"].min().date(), tramo["Date"].max().date()
        eventos = tramo[tramo["es_pullback_entry"]].dropna(subset=[f"fwd_{HORIZONTE}d"])

        if len(eventos) < 5:
            print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
                  f"solo {len(eventos)} eventos, muestra insuficiente.\n")
            continue

        retornos_brutos = eventos[f"fwd_{HORIZONTE}d"].values
        retornos_netos = retornos_brutos - COSTE_IDA_Y_VUELTA
        resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                         n_bootstrap=1500, random_state=idx)
        ic_low, ic_high = resultado["intervalo_confianza"]

        print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
              f"n={len(eventos)}  media_neta={resultado['media_observada']*100:+.3f}%  "
              f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado['significativo']}\n")

        resumen.append({"tramo": idx, "fechas": f"{fecha_ini} a {fecha_fin}",
                         "n": len(eventos), "media_%": resultado["media_observada"]*100,
                         "significativo": resultado["significativo"]})

    resumen_df = pd.DataFrame(resumen)
    print("=== RESUMEN ===")
    print(resumen_df.to_string(index=False))

    n_positivos = (resumen_df["media_%"] > 0).sum()
    n_significativos = resumen_df["significativo"].sum()
    print(f"\nTramos con media positiva: {n_positivos}/{len(resumen_df)}")
    print(f"Tramos individualmente significativos: {n_significativos}/{len(resumen_df)}")
