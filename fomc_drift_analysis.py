"""
fomc_drift_analysis.py
¿Sube el S&P 500 de forma sistemática en el día de trading previo a
cada reunión programada de la Fed, antes incluso de saber qué va a
decir? Es un efecto documentado académicamente (Lucca y Moench,
"The Pre-FOMC Announcement Drift", Journal of Finance) — lo probamos
con nuestros propios datos y nuestra propia herramienta de
significancia, no nos fiamos del paper sin comprobarlo.

Requiere: pip install yfinance --break-system-packages

Uso:
    python3 fomc_drift_analysis.py
"""

import pandas as pd
import numpy as np
from fomc_dates import FOMC_ANNOUNCEMENT_DATES
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"  # ETF del S&P 500, con histórico largo y líquido


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="10y")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]]


def calcular_drift(precio_df: pd.DataFrame, fechas_fomc: list) -> pd.DataFrame:
    fechas_fomc_dt = pd.to_datetime(fechas_fomc)
    resultados = []

    for fecha_anuncio in fechas_fomc_dt:
        idx_candidatos = precio_df.index[precio_df["Date"] == fecha_anuncio]
        if len(idx_candidatos) == 0:
            continue
        idx = idx_candidatos[0]
        if idx == 0:
            continue

        retorno_dia_anuncio = precio_df.loc[idx, "retorno_diario"]
        resultados.append({
            "fecha_anuncio": fecha_anuncio.date(),
            "retorno_dia_previo_al_anuncio": retorno_dia_anuncio,
        })

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER} (10 años)...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    print(f"{len(precio_df)} días de trading descargados. "
          f"{precio_df['Date'].min().date()} -> {precio_df['Date'].max().date()}\n")

    precio_df = precio_df.sort_values("Date").reset_index(drop=True)
    precio_df["retorno_diario"] = precio_df["Close"].pct_change()

    drift_df = calcular_drift(precio_df, FOMC_ANNOUNCEMENT_DATES)
    print(f"{len(drift_df)} de {len(FOMC_ANNOUNCEMENT_DATES)} reuniones FOMC encontradas "
          f"dentro del histórico descargado.\n")

    if drift_df.empty:
        print("Sin datos suficientes para el análisis — revisa el rango de fechas.")
        raise SystemExit

    retornos = drift_df["retorno_dia_previo_al_anuncio"].values

    print("=== RETORNO DEL S&P 500 EN EL DÍA PREVIO AL ANUNCIO DEL FOMC ===")
    print(f"Retorno medio: {retornos.mean()*100:.4f}%")
    print(f"% de veces positivo: {(retornos > 0).mean()*100:.1f}%")
    print(f"Desviación típica: {retornos.std()*100:.4f}%")

    print("\n=== SIGNIFICANCIA (bootstrap estacionario, mismo test que usamos con el funding rate) ===")
    resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=2.0,
                                                     n_bootstrap=3000, random_state=1)
    ic_low, ic_high = resultado["intervalo_confianza"]
    print(f"Media: {resultado['media_observada']*100:.4f}%")
    print(f"Intervalo de confianza 95%: [{ic_low*100:.4f}%, {ic_high*100:.4f}%]")
    print(f"¿Significativamente distinto de cero?: {resultado['significativo']}")

    print("\n--- Comparación: ¿es mejor que un día cualquiera? ---")
    todos_los_retornos = precio_df["retorno_diario"].dropna().values
    print(f"Retorno medio en CUALQUIER día de trading (10 años): {todos_los_retornos.mean()*100:.4f}%")
    print(f"Retorno medio en el día previo al FOMC: {retornos.mean()*100:.4f}%")

    print("\n--- Detalle por reunión ---")
    print(drift_df.to_string(index=False))
