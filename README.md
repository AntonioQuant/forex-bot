# forex_bot — Investigación cuantitativa en mercados tradicionales

Segundo proyecto de una serie de investigación con rigor estadístico real
— continuación de [crypto_bot](https://github.com/AntonioQuant/crypto-bot),
donde se agotó el terreno técnico en criptomonedas y se validó una única
estrategia con ventaja estadística demostrada (funding rate carry).

Aquí se aplica la misma disciplina a acciones, índices y calendario
macroeconómico: walk-forward, corrección por búsqueda múltiple, y la
misma honestidad ante los resultados negativos que ante los positivos.

**El relato completo, capítulo a capítulo, está en [`/diario`](./diario)**
— documenta tanto el proceso de cripto como el de aquí, incluyendo los
errores de cálculo encontrados por el camino, no solo los resultados finales.

## Hipótesis probadas

| Hipótesis | Resultado | Detalle |
|---|---|---|
| Pre-FOMC announcement drift (Lucca & Moench) | Rechazada | Sin significancia en dos metodologías distintas (ventana de día completo, 60 reuniones; ventana intradía exacta, 23 reuniones) — y en la segunda, el efecto se invierte a mitad de la propia muestra |
| Continuación tras movimientos bruscos alcistas | Interesante, no desplegable | Significativa en agregado (~1 siglo de S&P 500, 171 shocks), pero el patrón vive solo en la franja 1961-2010 — ausente o invertido en el tramo más reciente (2010-2026) |
| Continuación/reversión tras movimientos bruscos bajistas | Sin patrón consistente | Ningún horizonte sobrevivió con solidez |
| Compresión de volatilidad antes de un shock ("calma antes de la tormenta") | **Validada** | Significativa con ~470 shocks y un siglo de datos — aunque con un matiz metodológico: hay solape parcial entre cómo se define el shock y cómo se mide la compresión previa, así que es una confirmación de algo ya conocido (agrupamiento de volatilidad, tipo GARCH), no un hallazgo nuevo |

## Estructura

- `fomc_dates.py` / `fomc_drift_analysis.py` / `fomc_drift_intraday.py` — el drift pre-FOMC, dos metodologías
- `shock_move_analysis.py` / `shock_continuation_stability.py` / `shock_continuation_recent_breakdown.py` — movimientos bruscos, con el análisis de estabilidad por sub-periodos
- `precursor_volatility_analysis.py` — la compresión de volatilidad previa a un shock
- `reality_check.py` — la misma herramienta de significancia (bootstrap estacionario) reutilizada de crypto_bot, agnóstica a la clase de activo

## Pendiente de explorar

Velas japonesas + confirmación de volumen, PEAD (post-earnings drift),
Índice Arms, compras de insiders, momentum sistemático diversificado.
Ninguna se ha probado todavía con datos reales.
