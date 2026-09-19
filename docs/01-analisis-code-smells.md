# Análisis de code smells — `trivia.py`

## 1. Método largo

- `roll()` : mezcla impresión de estado, lógica de caja de penalización, movimiento en el tablero, cálculo de categoría y disparo de la pregunta, todo en un solo método con anidación profunda de `if`.
- `was_correctly_answered()` : mezcla lógica de caja de penalización, acumulación de monedas, verificación de victoria y rotación de turno.

## 2. Código duplicado

- En `roll()`, el bloque "sumar `roll` a `places[current_player]`, envolver si pasa de 11, imprimir nueva ubicación, imprimir categoría, preguntar" está duplicado casi textualmente entre la rama "sale de la caja de penalización" y la rama "no está en penalización".
- En `was_correctly_answered()`, el bloque "imprimir 'Answer was correct', sumar moneda, imprimir monedas, calcular ganador, avanzar turno" está duplicado entre la rama de penalización (cuando sí sale) y la rama normal — con el agravante de que en una copia dice `"corrent"` en vez de `"correct"`, evidencia de que el duplicado se mantiene a mano y ya se desincronizó.

## 3. Declaraciones switch (cadenas de `if` que deberían ser polimorfismo/datos)

- `_current_category` : 9 comparaciones `if self.places[...] == N` para mapear posición → categoría, cuando es aritmética modular simple.
- `_ask_question()` : 4 comparaciones `if self._current_category == '...'` para elegir de qué mazo sacar pregunta.
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

- `is_playable()` nunca se invoca ni en `roll`, ni en `add`, ni en el bucle de `__main__` — se puede jugar con 0 o 1 jugadores sin que nada lo impida. Es una regla de negocio declarada pero no aplicada.

## 9. Defecto funcional (no es un code smell de Fowler, pero se documenta)

- Línea 120 (original): `print("Answer was corrent!!!!")` — typo que hacía que el mensaje fuera inconsistente con la línea 99 (`'Answer was correct!!!!'`).
- **Resuelto** en el paso 6 del refactoring (commit `fix: corregir typo 'corrent' a 'correct'...`) como una corrección de comportamiento explícita y separada (cambia el output observable, por eso no se mezcló con los pasos de refactoring puro).

## 10. Defecto adicional descubierto al escribir los tests: off-by-one en `add()`

- `add()` leía `self.how_many_players` **después** de hacer `self.players.append(...)`, así que el primer jugador quedaba inicializado en el índice 1 de `places`/`purses`/`in_penalty_box`, no en el índice 0. Era invisible en la práctica porque los valores por defecto (`[0]*6`) ya coincidían con los que "se querían" poner.
- **Resuelto** como efecto colateral: al reemplazarlos por `self._players.append(Player(...))`, la indexación pasó a ser un simple `append`, correctamente alineado desde el índice 0.

### Nota sobre `is_playable()`

Se identificó como código muerto / generalidad especulativa desde el análisis inicial. Se decidió **no** invocarlo dentro de `__main__` durante el refactoring porque hacerlo sería agregar una validación nueva al comportamiento del programa (un cambio funcional), no una reestructuración interna — violaría la definición misma de refactoring ("sin cambiar su comportamiento observable"). Queda documentado como mejora funcional pendiente, fuera del alcance de este ejercicio.

### Historial de commits del refactoring

Se puede evidenciar el refactoring realizado en cada uno de los commits realizados.

## 11. Resultado en SonarQube "después"

Con el proyecto completo (código refactorizado + tests) y la cobertura real cargada, SonarQube reporta: **0 code smells, 0 bugs, 0% duplicación, 100% de cobertura**.

Sí aparecen **2 "vulnerabilities"**, que marca cualquier uso de `random.randrange` como "sensible a seguridad" por si se usara para generar tokens o contraseñas. En este caso solo simula el dado de un juego de mesa, así que es un **falso positivo revisado**: ya estaba presente en el código original y no representa un riesgo real para este uso. No se remedia porque está fuera del alcance del ejercicio y cambiar a `secrets`/`SystemRandom` sería una sobreingeniería injustificada para simular un dado.
