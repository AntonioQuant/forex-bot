# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 1 — La pared del Reality Check

### Por qué empecé esto

Hace unas semanas decidí retomar una idea que llevaba años dándome vueltas: si aprendía a programar y le sumaba lo que ya sabía de trading, ¿podría construir un bot que gestionara mi capital mejor de lo que lo haría yo solo, sin el cansancio ni los sesgos que arrastra cualquier humano frente a una pantalla?

Con ayuda de IA, decidí que este era el momento. La idea de partida era sencilla: buscar un patrón real en el precio de Bitcoin, programarlo, comprobar que funcionaba, y dejarlo operando. Pensaba que me llevaría semanas de prueba y error. No sabía que la parte más valiosa de todo esto no iba a ser encontrar una estrategia — iba a ser aprender, con datos propios, por qué es tan difícil que exista una.

Este es el registro honesto de ese camino, empezando por donde empezó de verdad: análisis técnico clásico, sobre el precio de Bitcoin, con la disciplina que fuimos construyendo sobre la marcha.

### La primera piedra: cruces de medias

Lo primero que probamos fue lo más obvio — un cruce de medias móviles exponenciales (EMA), la estrategia con la que casi todo el mundo empieza. En 15 minutos, el resultado fue brutal: **-97% de capital, profit factor de 0.32**. No fue mala suerte de un parámetro mal elegido — era la naturaleza del terreno. En ese timeframe, los costes de comisión y slippage se comen cualquier ventaja antes de que la estrategia tenga ocasión de demostrar nada.

Pasamos a un timeframe de 4 horas, con un filtro de tendencia basado en el ADX (Average Directional Index), que mide si el mercado se mueve con dirección clara o está lateral. Mejor, pero no bueno: 0 de 6 tramos rentables en un test walk-forward sobre 6 años de historial. El patrón se repetiría una y otra vez en las semanas siguientes.

### La lista de rechazos, uno a uno

Lo que siguió fue una sucesión ordenada de hipótesis, cada una probada con el mismo rigor: walk-forward sobre varios tramos temporales, nunca un solo backtest sobre todo el histórico de una vez.

- **Estrategia de Jaime/Trading Latino** (ADX + MACD + confirmación de volumen): 123 operaciones, profit factor 0.76. Rechazada.
- **Breakout de Donchian**: la muestra más grande de toda la investigación, 594 operaciones — profit factor 0.78. El rechazo más contundente, con la mayor confianza estadística posible.
- **Métricas on-chain** (SOPR, NUPL, MVRV, Reserve Risk): un filtro compuesto mejoraba el retorno agregado, pero destrozaba consistentemente el tramo más reciente de los seis. Rechazada.
- **TD Sequential** (Setup 9 y Countdown 13, de Tom DeMark): de las menos frágiles — 95 operaciones, profit factor 1.15, ningún tramo catastrófico. La primera candidata seria.
- **Ichimoku Cloud**, con las señales de entrada limpias y, después, con las señales de salida anticipada que el propio método describe: pasó de -4.93% a +8.64% de retorno agregado al añadir la salida anticipada. La segunda candidata seria.

Con dos estrategias que sobrevivían razonablemente bien por separado, hicimos lo que parecía el siguiente paso lógico: combinarlas en una cartera, junto con el sistema adaptativo original, cada una con un tercio del capital.

### El espejismo de la cartera

El resultado de la cartera de tres patas parecía, por fin, sólido: **+2.94% de retorno agregado, con el peor tramo individual nunca por debajo de -1.19%**, y un drawdown máximo contenido en -3.23%. Ningún tramo aislado, en ninguna de las tres estrategias por separado, se acercaba a esa estabilidad. Era, con diferencia, el mejor resultado de toda la investigación hasta ese momento.

Estábamos listos para pasar a papel — simular la cartera en tiempo real, sin dinero de por medio, como último paso antes de plantearnos capital real.

### El Reality Check

Antes de dar ese paso, decidimos hacer algo que no habíamos hecho todavía: preguntarnos si el resultado era real, o si era exactamente lo que cabría esperar por puro azar después de haber probado tantas estrategias distintas.

La herramienta se llama **White's Reality Check** — un test estadístico diseñado específicamente para esto: cuando pruebas muchas hipótesis y te quedas con la que mejor sale, necesitas corregir por el propio hecho de haber buscado tanto, no solo evaluar a la ganadora como si fuera la única candidata que existió jamás. Lo construimos desde cero (bootstrap estacionario, para respetar la dependencia temporal de los datos financieros) y lo aplicamos a las siete estrategias que habíamos probado con datos reales, no solo a la que había ganado.

El resultado: **p = 0.50.**

Es decir: si las siete estrategias hubieran sido puro ruido sin ninguna ventaja real, la probabilidad de que la mejor de ellas hubiera dado, por puro azar, un resultado igual de bueno que el que obtuvimos, era del 50%. Una moneda al aire. No había forma honesta de afirmar que Ichimoku, la ganadora, tuviera una ventaja real más allá de la que produciría el simple hecho de haber buscado entre siete candidatas.

Y por si quedaba alguna duda, aplicamos un segundo test — más simple, sin necesidad de corrección por búsqueda múltiple, directamente sobre el retorno diario de la propia cartera de tres patas. El intervalo de confianza del 95%: **[-0.0022%, +0.0046%] diario.** El cero cabía cómodamente dentro.

Ni la mejor estrategia individual, ni la cartera que las combinaba, lograban distinguirse de ruido con el rigor que exige un test formal.

### Lo que este momento significó de verdad

No fue un fallo del proceso — fue exactamente lo que el proceso estaba diseñado para descubrir. Llevábamos semanas aplicando la misma disciplina que finalmente nos dio esta respuesta: walk-forward por tramos, desconfianza ante resultados "demasiado buenos", verificación de cada afirmación antes de construir encima de ella. El Reality Check no fue una anomalía dentro de ese proceso — fue su conclusión más rigurosa.

Y tiene sentido, visto con perspectiva: el análisis técnico clásico —indicadores calculados sobre precio público, al alcance de cualquiera con Python— es terreno extensamente cazado, tanto en cripto como en mercados tradicionales, por gente con más capital, más infraestructura y más años estudiando exactamente lo mismo que nosotros. Si una ventaja así de simple y así de visible existiera de verdad, ya la habría arbitrado alguien antes que nosotros.

No fue el final del proyecto. Fue el final de una hipótesis concreta — y el principio de preguntarnos por qué tipo de ventaja *sí* podría sobrevivir a este mismo nivel de escrutinio.

---

*En el próximo capítulo: la única estrategia que sí pasó el test — no por predecir mejor el precio, sino por dejar de intentarlo.*
