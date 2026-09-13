"""
multiple_testing_correction_velas.py
Probamos 3 patrones (Engulfing, Harami, Piercing) x 2 grupos de volumen
(alto/no alto) = 6 candidatos, y nos quedamos con el mejor (Harami sin
volumen). Antes de creérnoslo, hay que corregir por el propio hecho de
haber buscado entre 6 candidatos — el mismo principio del Reality
Check, adaptado aquí con Bonferroni porque estos son eventos dispersos
(cada patrón dispara en días distintos), no series continuas de
retorno diario como las estrategias de cripto que sí usaban el
Reality Check completo.

Bonferroni es más simple y más conservador: exige que el p-valor de
cada candidato supere 0.05/6 (no 0.05) para considerarse significativo
tras la corrección — un candidato "casi seguro" real sobrevive esto
sin problema; uno al límite, no.

Uso:
    python3 multiple_testing_correction_velas.py
"""

import pandas as pd
import numpy as np

TICKER = "SPY"
VOLUME_MA_PERIOD = 20
VOLUME_THRESHOLD = 1.2
HORIZONTE = 10
N_BOOTSTRAP = 3000
MEAN_BLOCK_LENGTH = 3.0


def cargar_precio(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].sort_values("Date").reset_index(drop=True)


def detectar_todos_los_patrones(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ayer_open = df["Open"].shift(1)
    ayer_close = df["Close"].shift(1)
    ayer_bajista = ayer_close < ayer_open
    hoy_alcista = df["Close"] > df["Open"]

    envuelve = (df["Open"] < ayer_close) & (df["Close"] > ayer_open)
    df["es_engulfing"] = hoy_alcista & ayer_bajista & envuelve

    df["es_harami"] = (
        ayer_bajista & hoy_alcista &
        (df["Open"] >= ayer_close) & (df["Close"] <= ayer_open)
    )

    punto_medio_ayer = (ayer_open + ayer_close) / 2
    df["es_piercing"] = (
        ayer_bajista & hoy_alcista &
        (df["Open"] < ayer_close) &
        (df["Close"] > punto_medio_ayer) &
        (df["Close"] < ayer_open)
    )

    df["vol_ma"] = df["Volume"].rolling(VOLUME_MA_PERIOD).mean()
    df["volumen_alto"] = df["Volume"] > (VOLUME_THRESHOLD * df["vol_ma"])

    df[f"fwd_{HORIZONTE}d"] = df["Close"].shift(-HORIZONTE) / df["Close"] - 1
    return df


def _stationary_bootstrap_indices(n: int, mean_block_length: float, rng: np.random.RandomState) -> np.ndarray:
    p = 1.0 / mean_block_length
    indices = np.empty(n, dtype=int)
    idx = rng.randint(0, n)
    for t in range(n):
        indices[t] = idx
        if rng.random() < p:
            idx = rng.randint(0, n)
        else:
            idx = (idx + 1) % n
    return indices


def p_valor_bootstrap(retornos: np.ndarray, random_state: int) -> float:
    """
    P-valor a una cola (H0: media <= 0) vía bootstrap estacionario:
    proporción de medias remuestreadas que caen en el lado <= 0,
    centrando la distribución en torno a la media observada para
    simular la hipótesis nula correctamente.
    """
    rng = np.random.RandomState(random_state)
    n = len(retornos)
    media_observada = retornos.mean()
    retornos_centrados = retornos - media_observada  # forzar media 0 (H0)

    medias_bootstrap = np.empty(N_BOOTSTRAP)
    for b in range(N_BOOTSTRAP):
        idx = _stationary_bootstrap_indices(n, MEAN_BLOCK_LENGTH, rng)
        medias_bootstrap[b] = retornos_centrados[idx].mean()

    p_valor = (medias_bootstrap >= media_observada).mean()
    return p_valor


if __name__ == "__main__":
    print(f"Descargando histórico de {TICKER}...")
    try:
        import yfinance  # noqa: F401
    except ImportError:
        print("Falta yfinance. Corre: pip install yfinance --break-system-packages")
        raise SystemExit

    precio_df = cargar_precio(TICKER)
    df = detectar_todos_los_patrones(precio_df)
    print(f"{len(df)} días totales.\n")

    candidatos = []
    for patron in ["es_engulfing", "es_harami", "es_piercing"]:
        for volumen_alto, etiqueta_vol in [(True, "con volumen alto"), (False, "sin volumen alto")]:
            mask = df[patron] & (df["volumen_alto"] == volumen_alto)
            eventos = df[mask].dropna(subset=[f"fwd_{HORIZONTE}d"])
            nombre = f"{patron.replace('es_', '')} {etiqueta_vol}"
            candidatos.append((nombre, eventos[f"fwd_{HORIZONTE}d"].values))

    print(f"=== P-VALORES INDIVIDUALES (antes de corrección), horizonte +{HORIZONTE}d ===\n")
    resultados = []
    for i, (nombre, retornos) in enumerate(candidatos):
        if len(retornos) < 10:
            print(f"{nombre}: muestra insuficiente ({len(retornos)})")
            continue
        p = p_valor_bootstrap(retornos, random_state=i)
        resultados.append({"candidato": nombre, "n": len(retornos),
                            "media_%": retornos.mean()*100, "p_valor": p})
        print(f"{nombre}: n={len(retornos)}  media={retornos.mean()*100:+.3f}%  p-valor={p:.4f}")

    resultados_df = pd.DataFrame(resultados).sort_values("p_valor")
    n_candidatos = len(resultados_df)
    umbral_bonferroni = 0.05 / n_candidatos

    print(f"\n=== CORRECCIÓN DE BONFERRONI ===")
    print(f"Candidatos probados: {n_candidatos}")
    print(f"Umbral ajustado: 0.05 / {n_candidatos} = {umbral_bonferroni:.4f} (en vez de 0.05)\n")

    resultados_df["sobrevive_bonferroni"] = resultados_df["p_valor"] < umbral_bonferroni
    print(resultados_df.to_string(index=False))

    n_sobreviven = resultados_df["sobrevive_bonferroni"].sum()
    print(f"\nCandidatos que sobreviven la corrección: {n_sobreviven}/{n_candidatos}")
    if n_sobreviven > 0:
        print("EUREKA confirmado con rigor -- hay al menos un candidato cuya ventaja no se explica")
        print("por el simple hecho de haber probado varios patrones a la vez.")
    else:
        print("Ningún candidato sobrevive la corrección -- el mejor resultado aislado es")
        print("indistinguible de lo que produciría buscar entre 6 candidatos por puro azar.")
