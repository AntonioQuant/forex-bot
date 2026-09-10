"""
reality_check.py
White's Reality Check (White, 2000) + test de significancia con
bootstrap estacionario. Reconstruido igual que en crypto_bot/ —
el mecanismo es agnóstico a la clase de activo, por eso se reutiliza
tal cual para el proyecto de forex/acciones.
"""

import numpy as np


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


def white_reality_check(returns_matrix: np.ndarray, mean_block_length: float = 5.0,
                         n_bootstrap: int = 1000, random_state: int = 0):
    rng = np.random.RandomState(random_state)
    T, L = returns_matrix.shape
    medias = returns_matrix.mean(axis=0)
    mejor_idx = int(np.argmax(medias))
    v_observado = np.sqrt(T) * medias[mejor_idx]

    v_bootstrap = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        idx = _stationary_bootstrap_indices(T, mean_block_length, rng)
        resampled = returns_matrix[idx, :]
        medias_resampled = resampled.mean(axis=0)
        stat = np.sqrt(T) * (medias_resampled - medias)
        v_bootstrap[b] = stat.max()

    p_valor = (v_bootstrap >= v_observado).mean()
    return {"mejor_estrategia_idx": mejor_idx, "estadistico_observado": v_observado,
            "p_valor": p_valor, "medias_por_estrategia": medias, "distribucion_bootstrap": v_bootstrap}


def bootstrap_mean_confidence_interval(returns: np.ndarray, mean_block_length: float = 5.0,
                                        n_bootstrap: int = 2000, random_state: int = 0,
                                        confidence: float = 0.95):
    """
    Test de significancia para UNA sola serie (sin corrección por
    búsqueda múltiple). Bootstrap estacionario directo sobre los
    retornos: construye el intervalo de confianza percentil de la
    media muestral, respetando la dependencia temporal de los datos.
    """
    rng = np.random.RandomState(random_state)
    n = len(returns)
    means = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        idx = _stationary_bootstrap_indices(n, mean_block_length, rng)
        means[b] = returns[idx].mean()

    alpha = 1 - confidence
    lower = np.percentile(means, alpha / 2 * 100)
    upper = np.percentile(means, (1 - alpha / 2) * 100)
    media_observada = returns.mean()

    return {
        "media_observada": media_observada,
        "intervalo_confianza": (lower, upper),
        "significativo": not (lower <= 0 <= upper),
        "distribucion_bootstrap": means,
    }
