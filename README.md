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
| Pre-FOMC announcement drift (Lucca & Moench) | Rechazada | Sin significancia en dos metodologías distintas — y en la ventana intradía, el efecto se invierte a mitad de la propia muestra |
| Continuación tras movimientos bruscos alcistas | Interesante, no desplegable | Significativa en agregado (~1 siglo de S&P 500), pero vive solo en la franja 1961-2010 — ausente o invertida en el tramo más reciente, sin un punto de quiebre limpio |
| Compresión de volatilidad antes de un shock | **Validada** | Confirmación de algo ya conocido (agrupamiento de volatilidad, tipo GARCH), con un matiz metodológico de solape parcial en la definición |
| Bullish Engulfing + volumen alto | Rechazada, e invertida | Ningún grupo con volumen alto significativo; el único resultado significativo apareció sin volumen alto — lo contrario de la sabiduría popular del trading retail |
| Bullish Harami sin volumen alto | **Validada** | Significativa en 3/3 horizontes, sobrevive Bonferroni (p=0.006), estable en 5/6 tramos de 33 años, rentable neta de costes, replicada en SPY/GLD/AAPL (BTC: misma dirección, sin potencia suficiente) |
| Piercing Line sin volumen alto | **Validada en renta variable** | Sobrevive Bonferroni (p=0.0000), estable en 6/6 tramos, rentable neta de costes — pero se invierte en GLD (oro), sugiriendo un fenómeno específico de la psicología de acciones, no universal |
| PEAD (Post-Earnings Announcement Drift) | **Validada** | Sorpresas positivas: progresión significativa en 3/3 horizontes (hasta +6.40% a 60d). Sorpresas negativas: significativas a corto plazo, se disuelven a 60d — asimetría no siempre destacada en la literatura |
| Vuelta a tendencia (retroceso sobre EMA corta) | Real, señal frágil | Solo +20d significativo, pero con progresión ordenada de win rate y profit factor — probable falta de potencia estadística, no ausencia de efecto |
| Compras de insiders (megacaps) | Diseño insuficiente | Solo 4 eventos en 10 empresas — los directivos de grandes tecnológicas rara vez compran en mercado abierto |
| Compras de insiders (empresas medianas/pequeñas) | Real, señal frágil | +10d significativo (+4.24%), dirección positiva sostenida a +20d/+60d sin llegar a significancia — muestra pequeña (31 eventos) |
| Índice Arms (TRIN) | Descartada por impracticable | Sin ticker pre-calculado disponible; construirlo a mano exige datos de amplitud de cientos de componentes — desproporcionado frente al resto de la investigación |

## Estructura

- `fomc_dates.py` / `fomc_drift_analysis.py` / `fomc_drift_intraday.py` — el drift pre-FOMC
- `shock_move_analysis.py` / `shock_continuation_stability.py` / `shock_continuation_recent_breakdown.py` — movimientos bruscos y su declive
- `precursor_volatility_analysis.py` — compresión de volatilidad previa a un shock
- `bullish_engulfing_volume.py` / `harami_piercing_volume.py` — velas japonesas con confirmación de volumen
- `multiple_testing_correction_velas.py` — corrección de Bonferroni sobre los 6 candidatos de velas
- `harami_stability.py` / `piercing_stability.py` — estabilidad por sub-periodos
- `costs_simulation_velas.py` — simulación con costes de transacción reales
- `btc_candlestick_replication.py` / `gld_candlestick_replication.py` / `aapl_candlestick_replication.py` — réplica en activos distintos
- `pead_reconnaissance.py` / `pead_analysis.py` — sorpresas de beneficios
- `ema_pullback_trend.py` / `ema_pullback_stability.py` — vuelta a tendencia
- `insider_reconnaissance.py` / `insider_purchases_analysis.py` / `insider_purchases_smallcap.py` — compras de insiders
- `arms_index_reconnaissance.py` — sonda del Índice Arms
- `reality_check.py` — herramienta de significancia (bootstrap estacionario), reutilizada de crypto_bot

## Pendiente de explorar

Las diez hipótesis originales de esta lista están agotadas. La investigación
sigue abierta — el próximo hilo se documentará en `/diario` cuando tenga
resultados que mostrar.
