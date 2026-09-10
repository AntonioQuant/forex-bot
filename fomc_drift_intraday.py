"""
fomc_drift_intraday.py
Versión con la ventana EXACTA del paper original de Lucca y Moench:
desde el cierre del día anterior hasta las 14:00 ET del día del
anuncio (no cierre-a-cierre del día completo, como en la primera
versión). Requiere datos intradía, que yfinance solo ofrece para
~730 días hacia atrás — la muestra será más pequeña que la de
fomc_drift_analysis.py, pero metodológicamente más fiel al estudio
original.

Uso:
    python3 fomc_drift_intraday.py
"""

import pandas as pd
import numpy as np
from fomc_dates import FOMC_ANNOUNCEMENT_DATES
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"


def cargar_precio_intradia(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="730d", interval="1h")
    df = df.reset_index()
    col_fecha = "Datetime" if "Datetime" in df.columns else df.columns[0]
    df = df.rename(columns={col_fecha: "Datetime"})
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    if df["Datetime"].dt.tz is not None:
        df["Datetime"] = df["Datetime"].dt.tz_convert("US/Eastern")
    return df[["Datetime", "Close"]]


def calcular_drift_intradia(precio_df: pd.DataFrame, fechas_fomc: list) -> pd.DataFrame:
    precio_df = precio_df.sort_values("Datetime").reset_index(drop=True)
    precio_df["fecha"] = precio_df["Datetime"].dt.date

    resultados = []
    fechas_fomc_dt = pd.to_datetime(fechas_fomc).date

    for fecha_anuncio in fechas_fomc_dt:
        velas_del_dia = precio_df[precio_df["fecha"] == fecha_anuncio]
        if velas_del_dia.empty:
            continue
        velas_del_dia = velas_del_dia.copy()
        velas_del_dia["dist_a_14h"] = (velas_del_dia["Datetime"].dt.hour - 14).abs()
        vela_14h = velas_del_dia.sort_values("dist_a_14h").iloc[0]
        precio_14h = vela_14h["Close"]

        dias_anteriores = precio_df[precio_df["fecha"] < fecha_anuncio]
        if dias_anteriores.empty:
            continue
        ultimo_dia_anterior = dias_anteriores["fecha"].max()
        cierre_dia_anterior = dias_anteriores[dias_anteriores["fecha"] == ultimo_dia_anterior]["Close"].iloc[-1]

        retorno = (precio_14h - cierre_dia_anterior) / cierre_dia_anterior
        resultados.append({
            "fecha_anuncio": fecha_anuncio,
            "cierre_dia_anterior": cierre_dia_anterior,
            "precio_14h_anuncio": precio_14h,
            "retorno_ventana_exacta": retorno,
        })

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    print(f"Descargando histórico intradía de {TICKER} (máximo ~730 días, límite de yfinance)...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio_intradia(TICKER)
    print(f"{len(precio_df)} velas horarias. "
          f"{precio_df['Datetime'].min()} -> {precio_df['Datetime'].max()}\n")

    drift_df = calcular_drift_intradia(precio_df, FOMC_ANNOUNCEMENT_DATES)
    print(f"{len(drift_df)} de {len(FOMC_ANNOUNCEMENT_DATES)} reuniones FOMC dentro del rango intradía disponible.\n")

    if drift_df.empty or len(drift_df) < 5:
        print(f"Muestra demasiado pequeña ({len(drift_df)} reuniones) para un test fiable — "
              f"esto es justo la limitación de datos intradía que avisamos de antemano.")
        if not drift_df.empty:
            print(drift_df.to_string(index=False))
        raise SystemExit

    retornos = drift_df["retorno_ventana_exacta"].values

    print("=== RETORNO EN LA VENTANA EXACTA (cierre de ayer -> 14:00 del anuncio) ===")
    print(f"Retorno medio: {retornos.mean()*100:.4f}%")
    print(f"% de veces positivo: {(retornos > 0).mean()*100:.1f}%")
    print(f"Desviación típica: {retornos.std()*100:.4f}%")

    print("\n=== SIGNIFICANCIA ===")
    resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=2.0,
                                                     n_bootstrap=3000, random_state=1)
    ic_low, ic_high = resultado["intervalo_confianza"]
    print(f"Intervalo de confianza 95%: [{ic_low*100:.4f}%, {ic_high*100:.4f}%]")
    print(f"¿Significativamente distinto de cero?: {resultado['significativo']}")
    print(f"\n(Con solo {len(drift_df)} observaciones, un intervalo amplio o no significativo puede")
    print(f"deberse tanto a que el efecto no existe como a que la muestra es demasiado pequeña para")
    print(f"detectarlo — con esto solo no podemos distinguir las dos cosas con confianza.)")

    print("\n--- Detalle por reunión ---")
    print(drift_df.to_string(index=False))
