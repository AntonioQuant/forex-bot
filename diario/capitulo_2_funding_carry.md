# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 2 — La estrategia que ganó por dejar de predecir

### El giro

Tras el Reality Check, la pregunta cambió. Ya no era "¿qué indicador técnico funciona?" — era "¿qué tipo de ventaja podría sobrevivir a este mismo nivel de escrutinio?".

La respuesta vino, en parte, de fuera: H me pasó una lista de categorías de bots institucionales reales — market making, arbitraje de funding rate, basis trade, cascadas de liquidación. Ninguna de ellas intenta predecir hacia dónde va el precio. Todas cobran una prima estructural, del mismo modo que una aseguradora cobra una prima sin necesitar adivinar si va a llover.

De esa lista, una encajaba perfectamente con la infraestructura que ya teníamos construida: **el funding rate de los perpetuos**.

### La idea, en una frase

En Bybit, como en cualquier exchange de futuros perpetuos, cada 8 horas se liquida un pago entre quienes están en largo y quienes están en corto — el *funding rate*. Cuando el mercado está sesgado al alza (lo habitual en cripto, por el apalancamiento retail), los largos pagan a los cortos.

La estrategia: comprar el activo en spot (exposición larga real) y, al mismo tiempo, abrir un corto del mismo tamaño en el perpetuo. El precio sube o baja — da igual, las dos patas se cancelan entre sí. Lo único que queda es el cobro del funding cada 8 horas, sin depender de acertar ninguna dirección.

Antes de construir nada, medimos el dato de fondo con datos reales de Bybit desde 2020: **funding medio de +0.0118% cada 8 horas, ~12.9% anualizado, positivo de forma sostenida.** No una corazonada — un número verificable.

### El resultado, y el primer test de significancia que sí pasó

El backtest sobre el histórico completo (2020-2026): **+128.25% de retorno acumulado, ~20% anualizado, con un drawdown máximo de apenas -1.62%.** Para comparar: cualquiera de las estrategias técnicas del capítulo anterior, en su mejor tramo, tenía drawdowns varias veces mayores.

Y, sobre todo, pasó la prueba que ninguna estrategia técnica había superado: aplicamos el mismo test de significancia con bootstrap estacionario, esta vez sin necesidad de corregir por búsqueda múltiple (no era la mejor de varias candidatas — era una única hipótesis, con fundamento económico previo). El intervalo de confianza del 95% sobre el retorno diario: **[+0.0277%, +0.0435%].** El cero quedaba fuera, con margen.

Fue el primer resultado de todo el proyecto que se sostuvo con rigor formal.

### El riesgo que casi se nos pasa

Antes de darlo por bueno, hicimos la pregunta que separa una simulación de una estrategia operable de verdad: ¿qué pasa con el margen de la pata corta si el precio sube mucho?

El motor de liquidación de un exchange no sabe que tienes spot cubriendo tu corto — solo mira el margen depositado en esa posición. Calculamos, con la fórmula oficial de Bybit, qué habría pasado si hubiéramos abierto la posición el primer día de nuestro histórico (marzo de 2020, BTC en ~$6.700) y nunca hubiéramos tocado el margen: **hasta el apalancamiento 1x —el mínimo posible— se habría liquidado, en octubre de 2020, a los siete meses.** Para sobrevivir sin reponer margen ni una sola vez durante los seis años completos, habríamos necesitado depositar **casi 11 veces el valor de la posición** en margen quieto — inviable en la práctica.

La solución no fue abandonar la estrategia, fue construir gestión de margen activa: reponer margen cuando el buffer de seguridad se estrecha, con reglas fijadas antes de entrar, no reevaluadas sobre la marcha. Probado contra el precio real de los seis años: en el peor momento, el apalancamiento efectivo necesario bajó a **~0.18-0.2x** (margen de unas 5 veces el nocional) — varias veces más eficiente que el "abre y olvida", y sin liquidarse nunca.

De paso, comprobamos otro riesgo que podría haber estado escondido: la diferencia entre el precio del spot y el del perpetuo (el *basis*), que en teoría podría dispararse en momentos de estrés y adelantar una liquidación. Medido con datos reales: máximo histórico de apenas 0.96% en cinco años — no era el riesgo oculto que temíamos.

### El límite honesto: no son muchas apuestas, es una sola

Con el resultado validado en BTC, la pregunta natural era diversificar — ¿funciona igual en ETH? ¿Y repartido entre exchanges?

Ambas respuestas fueron parcialmente sí, con un matiz importante. El funding de ETH también resultó significativo por separado, con un retorno casi idéntico al de BTC (~13% anual). Pero la correlación entre ambos era de **0.81** — demasiado alta para que combinarlos reduzca el riesgo de forma real. Y al comparar el funding de BTC entre Bybit y Binance, la correlación fue de **0.78** — tampoco ayudaba gran cosa, porque hay arbitraje entre exchanges que iguala el funding de uno y otro.

La conclusión, con la misma honestidad de siempre: **el funding rate no es una cartera de muchas primas independientes — es esencialmente una única exposición macro** al sesgo estructural alcista y apalancado de todo el mercado cripto. Da igual cómo la cortes (por activo, por exchange), sigues expuesto a la misma fuente de riesgo de fondo. No invalida la estrategia — sigue siendo la única con ventaja demostrada de todo el proyecto — pero cambia cómo hay que pensar el tamaño del capital que se le dedica: como una apuesta grande y bien entendida, no como una cartera diversificada.

### Lo que este capítulo enseñó de verdad

La diferencia entre esta estrategia y las siete del capítulo anterior no fue una cuestión de mejor indicador, ni de más pruebas, ni de más suerte. Fue una diferencia de naturaleza: unas intentaban **predecir** algo que miles de participantes, muchos con más capital e infraestructura que nosotros, llevan años intentando predecir también. Esta se limitó a **cobrar** algo que ya existía, con una explicación económica verificable de antemano.

No es una lección abstracta — es, con datos propios, la razón concreta por la que un único enfoque de los ocho que probamos sobrevivió el mismo nivel de exigencia.

---

*En el próximo capítulo: agotado el terreno técnico en cripto, llevamos la misma disciplina a mercados que llevan siglo probando exactamente lo mismo — con un método más severo aún desde el primer test.*
