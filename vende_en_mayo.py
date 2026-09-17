"""
vende_en_mayo.py
"Sell in May and go away" / Halloween Indicator: anomalía de calendario
que sugiere que el periodo noviembre-abril rinde sistemáticamente
mejor que mayo-octubre. Documentada académicamente (Bouman y Jacobsen,
2002, "The Halloween Indicator, 'Sell in May and Go Away': Another
Puzzle") en múltiples mercados internacionales.

Se calcula el retorno acumulado de cada periodo (mayo-octubre,
noviembre-abril) para cada año del histórico, y se compara la media
de ambos grupos.

Uso:
    python3 vende_en_mayo.py
"""

import pandas as pd
import numpy as np
from reality_check import bootstrap_mean_confidence_interval

TICKERS = ["SPY", "BTC-USD"]


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Close"]].sort_values("Date").reset_index(drop=True)


def calcular_retornos_por_periodo(df: pd.DataFrame):
    df = df.copy()
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month

    retornos_verano = []  # mayo-octubre
    retornos_invierno = []  # noviembre-abril (cruza año)

    for year in sorted(df["year"].unique()):
        # VERANO: 1 mayo -> 31 octubre del mismo año
        verano = df[(df["year"] == year) & (df["month"] >= 5) & (df["month"] <= 10)]
        if len(verano) > 20:
            ret = verano["Close"].iloc[-1] / verano["Close"].iloc[0] - 1
            retornos_verano.append(ret)

        # INVIERNO: 1 noviembre del año -> 30 abril del año siguiente
        inv_parte1 = df[(df["year"] == year) & (df["month"] >= 11)]
        inv_parte2 = df[(df["year"] == year + 1) & (df["month"] <= 4)]
        invierno = pd.concat([inv_parte1, inv_parte2])
        if len(invierno) > 20:
            ret = invierno["Close"].iloc[-1] / invierno["Close"].iloc[0] - 1
            retornos_invierno.append(ret)

    return np.array(retornos_verano), np.array(retornos_invierno)


if __name__ == "__main__":
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    for ticker in TICKERS:
        print(f"\n{'='*70}\nACTIVO: {ticker}\n{'='*70}")
        df = cargar_precio(ticker)
        print(f"{len(df)} días totales. {df['Date'].min().date()} -> {df['Date'].max().date()}")

        retornos_verano, retornos_invierno = calcular_retornos_por_periodo(df)
        print(f"\nPeriodos de verano (may-oct): n={len(retornos_verano)}")
        print(f"Periodos de invierno (nov-abr): n={len(retornos_invierno)}")

        for nombre, retornos in [("VERANO (mayo-octubre)", retornos_verano),
                                  ("INVIERNO (noviembre-abril)", retornos_invierno)]:
            if len(retornos) < 10:
                print(f"\n{nombre}: muestra insuficiente")
                continue
            resultado = bootstrap_mean_confidence_interval(retornos, mean_block_length=2.0,
                                                             n_bootstrap=2000, random_state=1)
            ic_low, ic_high = resultado["intervalo_confianza"]
            print(f"\n{nombre}: media={resultado['media_observada']*100:+.3f}%  "
                  f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado['significativo']}")

        # diferencia directa invierno - verano, año a año (emparejados donde sea posible)
        n_comparable = min(len(retornos_verano), len(retornos_invierno))
        if n_comparable >= 10:
            diferencia = retornos_invierno[:n_comparable] - retornos_verano[:n_comparable]
            resultado_diff = bootstrap_mean_confidence_interval(diferencia, mean_block_length=2.0,
                                                                  n_bootstrap=2000, random_state=2)
            ic_low, ic_high = resultado_diff["intervalo_confianza"]
            print(f"\nDIFERENCIA (invierno - verano): media={resultado_diff['media_observada']*100:+.3f}%  "
                  f"IC=[{ic_low*100:+.3f}%, {ic_high*100:+.3f}%]  significativo={resultado_diff['significativo']}")

    print("\n--- Aviso ---")
    print("Muestra pequeña por naturaleza (un periodo de verano/invierno por año, no por día).")
    print("Bitcoin no tiene la misma lógica estacional que documenta el estudio original")
    print("(basado en mercados con calendario financiero tradicional) -- incluido como curiosidad.")
