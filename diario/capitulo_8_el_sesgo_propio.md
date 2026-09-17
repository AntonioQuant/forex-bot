# Diario de a bordo: construyendo (y desmontando) un bot de trading

## Capítulo 8 — Cuando el sesgo estaba en nuestro propio código

### Una alarma que sonó por lo limpio del resultado, no por lo sucio

Seguí probando afirmaciones. La siguiente: cuando el precio hace un nuevo máximo con menos volumen que el máximo anterior, es señal de debilidad — el "volumen anticipa el precio", según el manual.

El resultado salió demasiado bueno. En Bitcoin: significativo en los tres horizontes, con excesos de entre -7% y -11% — mayor que cualquier otro hallazgo de todo el proyecto, incluido Fibonacci. Debería haberme alegrado. En vez de eso, desconfié, por la misma regla que llevamos aplicando desde el principio: los resultados demasiado limpios merecen más sospecha, no menos.

Y encontré algo real, esta vez en nuestro propio diseño, no en el manual que estábamos verificando.

### El fallo, explicado sin rodeos

Para saber si un día fue un "pico" de precio, el método que veníamos usando miraba una ventana de tiempo centrada — días antes **y días después**. Eso significa que, para confirmar que un día fue un máximo, el algoritmo ya necesitaba saber que el precio había bajado en los días siguientes. Medir el retorno desde ese mismo día, como estábamos haciendo, era circular: usábamos información del futuro para predecir el futuro.

No es un error sutil de matemáticas — es el tipo de fallo que, sin darte cuenta, puede inflar un resultado hasta hacerlo parecer un descubrimiento cuando en realidad es la propia definición dándose la razón a sí misma.

### La corrección, y lo que cambió al aplicarla

Construí una forma distinta de confirmar un extremo: un día solo cuenta como "pico confirmado" una vez han pasado los días suficientes **sin que nadie lo haya superado** — y la señal se marca en ese día de confirmación, no en el día del propio pico. Lo comprobé de la forma más exigente posible: alterando el futuro por completo y confirmando que una decisión ya tomada no cambiaba ni un poco.

Con esto corregido, volví a correr la prueba de volumen. **El hallazgo se desvaneció casi por completo** en Bitcoin — de -7%/-11% significativos a nada, en ningún horizonte. Era, en su mayor parte, el propio sesgo, no un fenómeno real.

### Revisando todo lo demás con la misma vara

No podía quedarme ahí. Revisé cada script construido antes de encontrar el fallo — y encontré que **Soporte/Resistencia, Doble Cima/Fondo, y el propio hallazgo de Fibonacci** se habían construido con el mismo método antiguo, sin que lo supiéramos entonces.

Doble Cima/Fondo: sin cambios, seguía sin ninguna ventaja. Bien.

Soporte/Resistencia: perdió parte de la poca significancia que tenía, pero la conclusión de fondo —sostenido por la crisis de 2008, no un patrón estable— se mantuvo igual.

Fibonacci, el hallazgo del que estaba más orgulloso, fue el más delicado de revisar. **Sobrevivió** — la dirección bajista se mantuvo, y dos de tres horizontes en Bitcoin siguieron siendo significativos tras la corrección. Pero la "decadencia ordenada" que había descrito con tanta limpieza resultó estar sobre-simplificada: el tramo más fuerte no era el más antiguo, como había contado, sino uno intermedio (2018-2020), y uno de los tramos que antes parecía significativo dejó de serlo. El hallazgo seguía siendo real. La historia que le había puesto alrededor era más ordenada de lo que los datos sostenían.

### Cerrando el bloque: rectángulos, cuñas, y una nube ajustada a cripto

Quedaban unas pocas afirmaciones más. Rectángulos —ruptura tras consolidación— dieron una señal real en Bitcoin, pero concentrada en una franja de apenas cuatro años, sin repartirse por el resto de la historia.

Cuñas y triángulos exigieron construir algo nuevo: una utilidad para ajustar líneas de tendencia diagonales, no solo niveles horizontales — la pieza más compleja de todo el proyecto, validada con cinco geometrías distintas antes de confiar en ella. El único resultado con muestra suficiente resultó estar sostenido en un 75% por un solo tramo histórico: la burbuja y el crash de las puntocom, 1998-2004. Fuera de esa ventana, el patrón casi no existía.

Y por último, la nube de Ichimoku, con la configuración de periodos ajustada específicamente al ritmo 24 horas de cripto, distinta de la estándar que ya habíamos probado hace semanas. Tampoco sobrevivió.

### El balance final del bloque

Catorce hipótesis probadas, con el mismo rigor de siempre — y esta vez, con una revisión completa de nuestro propio método en mitad del camino. Diez rechazadas sin matices. Dos con una señal real pero frágil, sostenidas por episodios históricos concretos, no por un fenómeno estable. Una — Fibonacci — con un hallazgo genuino, en dirección contraria a la que enseña el propio manual, más irregular de lo que conté al principio pero real de todas formas.

Lo más valioso de este bloque, sospecho, no fue ninguno de los catorce resultados por separado. Fue encontrar el sesgo en nuestro propio código, corregirlo en público, y descubrir que la mayoría de lo que habíamos construido antes de eso seguía en pie. La misma disciplina que hemos aplicado a cada libro, cada newsletter, cada afirmación ajena, aplicada esta vez a nosotros mismos.

---

*Continuará.*
