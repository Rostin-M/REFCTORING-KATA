# Refactoring Kata — Juego de Trivia

Refactoring del juego de Trivia (Legacy Code Retreat, jbrains) en Python 3, aplicando el ciclo de refactoring y el catálogo de code smells de Fowler visto en el curso.

## Qué se hizo

- Se analizó el código original (`trivia.py`), que no tenía pruebas ni documentación, para identificar sus code smells.
- Se escribió una suite de pruebas de caracterización (`tests/test_trivia.py`) con **100% de cobertura**, para poder refactorizar con una red de seguridad.
- Se refactorizó el código en **pasos pequeños**, cada uno como un commit independiente, corriendo las pruebas después de cada cambio.
- Se analizó el proyecto con **SonarQube** antes y después del refactoring, como segunda validación independiente de la calidad del código.

El detalle completo (code smells encontrados, defectos descubiertos, resultado de SonarQube y el paso a paso del refactoring) está en [`docs/01-analisis-code-smells.md`](docs/01-analisis-code-smells.md).

## Estructura del repo

```
trivia.py                  # Codigo del juego (ya refactorizado)
tests/test_trivia.py       # Suite de pruebas
.coveragerc                # Configuracion de cobertura
requirements-dev.txt       # Dependencias de desarrollo (pytest, coverage)
docs/01-analisis-code-smells.md   # Analisis completo de code smells y refactoring
docs/capturas/              # Evidencia (cobertura y SonarQube antes/despues)
```

## Cómo correr las pruebas

```bash
python -m venv .venv
./.venv/Scripts/pip install -r requirements-dev.txt
./.venv/Scripts/python -m coverage run -m pytest -v
./.venv/Scripts/python -m coverage report -m
```
