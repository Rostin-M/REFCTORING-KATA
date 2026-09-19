# Análisis de code smells — `trivia.py` (versión original)

Catálogo de referencia: Fowler, *Refactoring* (2006) / Refactoring Guru.

## 1. Método largo
- `roll()` (líneas 45-75): mezcla impresión de estado, lógica de caja de penalización, movimiento en el tablero, cálculo de categoría y disparo de la pregunta, todo en un solo método con anidación profunda de `if`.
- `was_correctly_answered()` (líneas 96-131): mezcla lógica de caja de penalización, acumulación de monedas, verificación de victoria y rotación de turno.

## 2. Código duplicado
- En `roll()`, el bloque "sumar `roll` a `places[current_player]`, envolver si pasa de 11, imprimir nueva ubicación, imprimir categoría, preguntar" (líneas 54-62 y 67-75) está duplicado casi textualmente entre la rama "sale de la caja de penalización" y la rama "no está en penalización".
- En `was_correctly_answered()`, el bloque "imprimir 'Answer was correct', sumar moneda, imprimir monedas, calcular ganador, avanzar turno" (líneas 99-110 y 120-131) está duplicado entre la rama de penalización (cuando sí sale) y la rama normal — con el agravante de que en una copia dice `"corrent"` en vez de `"correct"` (línea 120), evidencia de que el duplicado se mantiene a mano y ya se desincronizó.

## 3. Declaraciones switch (cadenas de `if` que deberían ser polimorfismo/datos)
- `_current_category` (líneas 84-94): 9 comparaciones `if self.places[...] == N` para mapear posición → categoría, cuando es aritmética modular simple.
- `_ask_question()` (líneas 78-81): 4 comparaciones `if self._current_category == '...'` para elegir de qué mazo sacar pregunta.
- Cada categoría nueva obliga a tocar ambos lugares — riesgo de inconsistencia.

## 4. Envidia de características (Feature Envy)
- `Game` constantemente indexa `self.places[self.current_player]`, `self.purses[self.current_player]`, `self.in_penalty_box[self.current_player]` para leer/mutar el estado de **un** jugador. Esa lógica "le pertenece" a un objeto `Player`, no a `Game`.

## 5. Cambio divergente (Divergent Change)
- `Game` cambia por razones no relacionadas entre sí:
  - Agregar una categoría nueva → tocar `__init__`, `_current_category` y `_ask_question`.
  - Cambiar la regla de la caja de penalización → tocar `roll` y `was_correctly_answered`.
  - Cambiar la condición de victoria → tocar `_did_player_win`.
  - Cambiar cómo se representa un jugador → tocar `add`, `roll`, `was_correctly_answered`, `wrong_answer`.
- Una sola clase concentra demasiados motivos de cambio distintos.

## 6. Obsesión primitiva (Primitive Obsession)
- El estado de cada jugador se modela con `int`/`bool` sueltos repartidos en tres arreglos paralelos (`places[i]`, `purses[i]`, `in_penalty_box[i]`) en vez de un objeto `Player` con esos tres atributos.
- La categoría es un `str` comparado por igualdad en vez de, por ejemplo, un `Enum`.

## 7. Grupos de datos (Data Clumps)
- `places`, `purses`, `in_penalty_box`, siempre indexados por el mismo índice de jugador, viajan juntos por todo el código — es la marca clásica de un grupo de datos que debería agruparse en una clase.

## 8. Generalidad especulativa / código muerto
- `is_playable()` (línea 27-28) nunca se invoca ni en `roll`, ni en `add`, ni en el bucle de `__main__` — se puede jugar con 0 o 1 jugadores sin que nada lo impida. Es una regla de negocio declarada pero no aplicada.

## 9. Defecto funcional (no es un code smell de Fowler, pero se documenta)
- Línea 120 (original): `print("Answer was corrent!!!!")` — typo que hacía que el mensaje fuera inconsistente con la línea 99 (`'Answer was correct!!!!'`).
- **Resuelto** en el paso 6 del refactoring como una corrección de comportamiento explícita y separada (cambia el output observable, por eso no se mezcló con los pasos de refactoring puro). El test que documentaba el defecto se actualizó en el mismo commit para reflejar el texto correcto.

## Resumen para el video
| Code smell | Ubicación principal |
|---|---|
| Método largo | `roll()`, `was_correctly_answered()` |
| Código duplicado | `roll()`, `was_correctly_answered()` |
| Declaraciones switch | `_current_category()`, `_ask_question()` |
| Envidia de características | Todo `Game` sobre `places/purses/in_penalty_box` |
| Cambio divergente | Clase `Game` completa |
| Obsesión primitiva | `places`, `purses`, `in_penalty_box` como arrays paralelos |
| Grupos de datos | `places[i]` + `purses[i]` + `in_penalty_box[i]` |
| Generalidad especulativa | `is_playable()` sin usar |
