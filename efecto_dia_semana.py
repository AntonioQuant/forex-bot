"""
efecto_dia_semana.py
Anomalía clásica documentada académicamente desde los años 80 (French,
1980; Gibbons y Hess, 1981): el retorno medio de las acciones varía
según el día de la semana, con los lunes destacando negativamente en
los estudios originales.

Se comprueba el retorno medio de cada día de la semana por separado,
con significancia respecto a cero para cada uno.

Uso:
    python3 efecto_dia_semana.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKERS = ["SPY", "BTC-USD"]
COSTE_IDA_Y_VUELTA = {"SPY": 0.0005, "BTC-USD": 0.0011}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    df = df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)
    df["retorno_diario"] = df["Close"].pct_change()
    df["dia_semana"] = df["Date"].dt.dayofweek  # 0=Lunes ... 6=Domingo
    return df


def analizar_por_dia(df: pd.DataFrame, coste: float):
    for i, nombre_dia in enumerate(DIAS_SEMANA):
        retornos = df[df["dia_semana"] == i]["retorno_diario"].dropna().values
        if len(retornos) < 30:
            print(f"  {nombre_dia}: muestra insuficiente ({len(retornos)})")
            continue
        retornos_netos = retornos  # sin coste aquí: es retorno de UN día, no de una operación completa
        resultado = bootstrap_mean_confidence_interval(retornos_netos, mean_block_length=3.0,
                                                         n_bootstrap=2000, random_state=i)
        ic_low, ic_high = resultado["intervalo_confianza"]
        print(f"  {nombre_dia}: n={len(retornos)}  media={resultado['media_observada']*100:+.4f}%  "
              f"IC=[{ic_low*100:+.4f}%, {ic_high*100:+.4f}%]  significativo={resultado['significativo']}")


if __name__ == "__main__":
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    for ticker in TICKERS:
        print(f"\n{'='*70}\nACTIVO: {ticker}\n{'='*70}")
        df = cargar_precio(ticker)
        print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")
        coste = COSTE_IDA_Y_VUELTA[ticker]
        analizar_por_dia(df, coste)

    print("\n--- Aviso ---")
    print("5 días x 2 activos = 10 tests. Esperaríamos ~0.5 significativos por azar al 5%.")
    print("Bitcoin opera 24/7 -- no tiene fines de semana reales, así que este test es más")
    print("relevante para SPY; se incluye BTC como curiosidad/control, no como hipótesis fuerte.")
