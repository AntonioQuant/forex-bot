# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 5 — Confirmando lo ya sabido, y las señales frágiles

### Un tipo de dato completamente nuevo

Todo lo investigado hasta ahora en mercados tradicionales —FOMC, shocks, velas japonesas— partía de la misma materia prima: precio y volumen. Para la siguiente hipótesis, decidimos tocar algo distinto: datos fundamentales de verdad. Sorpresas de beneficios trimestrales, y el fenómeno que llevan documentando las finanzas académicas desde 1968 — el *Post-Earnings Announcement Drift* (PEAD).

La idea es sencilla de enunciar: cuando una empresa bate o falla las expectativas de los analistas, el mercado no incorpora esa sorpresa de golpe — el precio sigue derivando en la misma dirección durante semanas. Es una de las anomalías mejor replicadas que existen, y todavía viva según buena parte de la literatura actual.

### La confirmación más limpia de todo el proyecto

Con una sola empresa, la muestra habría sido demasiado pequeña (unos 46 trimestres). Agrupamos diez empresas grandes y líquidas de sectores distintos —tecnología, banca, consumo, energía, salud— para tener potencia estadística real: 934 eventos de resultados en total.

Las sorpresas positivas confirmaron el patrón de manual, con una progresión que crecía exactamente como predice la literatura: +1.28% a 5 días, +2.25% a 20 días, **+6.40% a 60 días**. Cinco de seis tests resultaron significativos — el resultado más limpio de toda la investigación en mercados tradicionales.

Pero hubo un matiz que la mayoría de resúmenes simplificados del PEAD no destaca: las sorpresas negativas fueron significativas a 5 y 20 días, con una caída de en torno al -1.8% en ambos casos — pero **desaparecieron por completo a 60 días** (+0.11%, sin siquiera mantener el signo). El mercado castiga la sorpresa negativa de inmediato, y luego el precio se estabiliza, en vez de seguir cayendo como predeciría un PEAD simétrico. Y un detalle de contexto real, no un sesgo nuestro: hubo casi cinco veces más sorpresas positivas que negativas (773 frente a 161) — las grandes empresas gestionan activamente las expectativas de los analistas a la baja para "batirlas" con más frecuencia de la que baten por puro azar.

### Vuelta a tendencia: una señal real, pero sin potencia suficiente

Mi propia idea original —comprar el retroceso sobre la EMA corta, con la EMA larga confirmando que la tendencia de fondo sigue intacta— dio un resultado con matices genuinos. Solo uno de tres horizontes (+20 días) salió significativo, apenas por encima de lo que esperaríamos por azar.

Pero dentro del propio resultado había una progresión ordenada, no un pico aislado: win rate subiendo de 55.0% a 57.7% a 63.9% según el horizonte, profit factor de 1.04 a 1.25 a 1.53 — coherente con la idea de que "comprar el retroceso dentro de una tendencia" necesita tiempo para notarse. Al comprobar estabilidad por sub-periodos en el único horizonte significativo, el patrón se mantuvo **positivo en los 6 tramos de 33 años**, pero solo significativo individualmente en uno — un efecto probablemente real, modesto, sin la potencia estadística por tramo para confirmarlo del todo.

### Compras de insiders: el error estaba en dónde buscábamos, no en la idea

La última hipótesis de la lista original — cuando un directivo compra acciones de su propia empresa con su propio dinero, ¿precede a un buen comportamiento del valor? El primer intento, con las mismas diez megacapitalizaciones que usamos en PEAD, dio solo 4 eventos en total — muestra inservible.

La razón, una vez la pensamos con calma: los directivos de grandes tecnológicas cobran la mayor parte de su compensación ya en acciones asignadas — rara vez tienen motivo para comprar más con dinero propio. Repetimos el análisis con quince empresas medianas y pequeñas, de sectores con propiedad más concentrada en fundadores y directivos de toda la vida (bancos regionales, industriales, consumo). El resultado saltó a 31 eventos — todavía la muestra más pequeña de las que hemos tomado en serio, pero suficiente para ver algo: **+10 días significativo (+4.24%)**, un efecto notablemente grande, aunque +20 y +60 días no llegaron a significancia pese a mantener la misma dirección positiva y creciente. El mismo patrón de "intervalo que se ensancha más rápido que el efecto crece" que ya habíamos visto con Piercing Line en su primera pasada — probablemente una cuestión de potencia estadística, no de que el fenómeno se apague.

### Lo que estos dos capítulos enseñaron de verdad

El PEAD es la confirmación de que el rigor que hemos aplicado todo este tiempo también sirve para reproducir, no solo para rechazar — cuando la literatura académica está bien fundamentada, nuestros propios datos lo confirman con la misma claridad con la que hemos rechazado tantas otras cosas.

Y EMA pullback y compras de insiders comparten una lección distinta, igual de importante: **un resultado no significativo no siempre significa "no hay efecto"** — a veces significa "la muestra es demasiado pequeña para verlo con la confianza que exigimos". Es una distinción que hemos aprendido a respetar en vez de simplificar, incluso cuando complica la historia que nos gustaría contar.

---

*En el próximo capítulo: cerramos la lista de diez hipótesis sin cerrar la investigación — y una lectura inesperada nos regala un lenguaje nuevo para pensar en todo lo que hemos venido haciendo estas semanas.*
