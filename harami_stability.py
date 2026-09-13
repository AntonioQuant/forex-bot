"""
harami_stability.py
El Bullish Harami sin volumen alto salió significativo en los tres
horizontes probados (+5d, +10d, +20d) sobre el agregado completo de
SPY (1993-2026). Antes de creérnoslo, la misma comprobación que ya
nos salvó una vez con los shocks del S&P 500: ¿se mantiene estable
por sub-periodos, o vive solo en una franja concreta del histórico?

Se usa el horizonte +10d (punto medio de los tres significativos) y
se divide el histórico en 6 tramos cronológicos de tamaño similar.

Uso:
    python3 harami_stability.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
VOLUME_MA_PERIOD = 20
VOLUME_THRESHOLD = 1.2
HORIZONTE = 10
N_TRAMOS = 6


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].sort_values("Date").reset_index(drop=True)


def detectar_harami_sin_volumen(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ayer_open = df["Open"].shift(1)
    ayer_close = df["Close"].shift(1)
    ayer_bajista = ayer_close < ayer_open
    hoy_alcista = df["Close"] > df["Open"]

    df["es_harami"] = (
        ayer_bajista & hoy_alcista &
        (df["Open"] >= ayer_close) & (df["Close"] <= ayer_open)
    )

    df["vol_ma"] = df["Volume"].rolling(VOLUME_MA_PERIOD).mean()
    df["volumen_alto"] = df["Volume"] > (VOLUME_THRESHOLD * df["vol_ma"])
    df["es_harami_sin_volumen"] = df["es_harami"] & (~df["volumen_alto"])

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
    df = detectar_harami_sin_volumen(precio_df)
    print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")

    tramos = split_cronologico(df, N_TRAMOS)

    print(f"=== ESTABILIDAD: BULLISH HARAMI SIN VOLUMEN ALTO, +{HORIZONTE}D, POR TRAMOS ===\n")
    resumen = []
    for idx, tramo in enumerate(tramos, start=1):
        fecha_ini, fecha_fin = tramo["Date"].min().date(), tramo["Date"].max().date()
        eventos = tramo[tramo["es_harami_sin_volumen"]].dropna(subset=[f"fwd_{HORIZONTE}d"])

        if len(eventos) < 5:
            print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
                  f"solo {len(eventos)} eventos, muestra insuficiente.\n")
            continue

        retornos = eventos[f"fwd_{HORIZONTE}d"].values
        resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=3.0,
                                                         n_bootstrap=1500, random_state=idx)
        ic_low, ic_high = resultado["intervalo_confianza"]

        print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
              f"n={len(eventos)}  media={resultado['media_observada']*100:+.3f}%  "
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
    print("\nBuscamos: consistencia entre tramos, sobre todo en los más recientes -- no solo")
    print("un promedio agregado sostenido por una franja histórica que ya no existe.")
