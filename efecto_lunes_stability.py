"""
efecto_lunes_stability.py
Estabilidad por 6 tramos del retorno de los lunes en SPY -- para ver
si la inversión del "efecto lunes" clásico (negativo en la literatura
de los 80, positivo en nuestro test agregado) es un patrón estable o
un fenómeno reciente.

Uso:
    python3 efecto_lunes_stability.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKER = "SPY"
N_TRAMOS = 6


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    df = df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)
    df["retorno_diario"] = df["Close"].pct_change()
    df["dia_semana"] = df["Date"].dt.dayofweek
    return df


def split_cronologico(df, n):
    size = len(df) // n
    return [df.iloc[i*size:(i+1)*size if i < n-1 else len(df)].reset_index(drop=True) for i in range(n)]


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    df = cargar_precio(TICKER)
    print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}\n")

    tramos = split_cronologico(df, N_TRAMOS)

    print(f"=== ESTABILIDAD: RETORNO DE LOS LUNES (SPY), POR TRAMOS ===\n")
    resumen = []
    for idx, tramo in enumerate(tramos, start=1):
        fecha_ini, fecha_fin = tramo["Date"].min().date(), tramo["Date"].max().date()
        retornos_lunes = tramo[tramo["dia_semana"] == 0]["retorno_diario"].dropna().values

        if len(retornos_lunes) < 30:
            print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
                  f"solo {len(retornos_lunes)} lunes, muestra insuficiente.\n")
            continue

        resultado = bootstrap_mean_confidence_interval(retornos_lunes, mean_block_length=3.0,
                                                         n_bootstrap=1500, random_state=idx)
        ic_low, ic_high = resultado["intervalo_confianza"]

        print(f"Tramo {idx}/{N_TRAMOS} ({fecha_ini} a {fecha_fin}): "
              f"n={len(retornos_lunes)}  media={resultado['media_observada']*100:+.4f}%  "
              f"IC=[{ic_low*100:+.4f}%, {ic_high*100:+.4f}%]  significativo={resultado['significativo']}\n")

        resumen.append({"tramo": idx, "fechas": f"{fecha_ini} a {fecha_fin}",
                         "n": len(retornos_lunes), "media_%": resultado["media_observada"]*100,
                         "significativo": resultado["significativo"]})

    resumen_df = pd.DataFrame(resumen)
    print("=== RESUMEN ===")
    print(resumen_df.to_string(index=False))

    n_positivos = (resumen_df["media_%"] > 0).sum()
    n_significativos = resumen_df["significativo"].sum()
    print(f"\nTramos con media positiva: {n_positivos}/{len(resumen_df)}")
    print(f"Tramos individualmente significativos: {n_significativos}/{len(resumen_df)}")
