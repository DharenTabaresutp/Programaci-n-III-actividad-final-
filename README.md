# Actividad Final - SEND + MORE = MONEY como CSP

**Autor:** Dharen Tabares
**Curso:** Programación III - Grupo 1

Modelado y solución del problema criptoaritmético SEND + MORE = MONEY como un CSP (Constraint Satisfaction Problem).

## Contenido
- `ProgIIIG1-Act04-DharenTabares.py`: código fuente (Python 3, sin dependencias externas).
- `Guion_Video_ActividadFinal.pdf`: guion del video expositivo (~4 min).

## Ejecución
```bash
python3 ProgIIIG1-Act04-DharenTabares.py
```

## Qué incluye
- Restricciones coherentes con el ejercicio (AllDifferent, ecuaciones por columna con acarreos, S y M distintos de 0).
- AC-3 generalizado, mantenido tras cada asignación (MAC), para conservar la consistencia.
- Backtracking con validación de asignaciones parciales y verificación aritmética final.
- Heurística MRV con desempate por grado.

## Resultados
| Configuración | Nodos |
|---|---|
| Básico (sin MRV ni AC-3) | 2.144.960 (~109 s) |
| MRV | 22.511 |
| MRV + AC-3 | 14 |

**Solución:** 9567 + 1085 = 10652
