"""
Actividad Final (Act04) - SEND + MORE = MONEY como CSP
Programacion III - Grupo 1
Autor: Dharen Tabares

Modelo:
  Variables : S,E,N,D,M,O,R,Y (letras)  +  C1,C2,C3,C4 (acarreos por columna)
  Dominios  : letras 0..9 (S y M: 1..9), acarreos 0..1
  Restricciones:
    - Todas las letras distintas (AllDifferent, como restricciones binarias)
    - Columna 1:      D + E        = Y + 10*C1
    - Columna 2: C1 + N + R        = E + 10*C2
    - Columna 3: C2 + E + O        = N + 10*C3
    - Columna 4: C3 + S + M        = O + 10*C4
    - Columna 5: C4                = M

Mejoras sobre el codigo base:
  1. Restricciones coherentes con el ejercicio (columnas con acarreo + S,M != 0).
  2. Consistencia: AC-3 generalizado (GAC) se ejecuta al inicio y se
     MANTIENE tras cada asignacion (algoritmo MAC) -> el CSP sigue siendo
     consistente durante toda la busqueda.
  3. Backtracking valida cada asignacion parcial (restricciones con scope
     completamente asignado) y valida la solucion final aritmeticamente.
  4. Heuristica de seleccion de variables: MRV (menor dominio) con
     desempate por grado (variable con mas restricciones sobre no asignadas).
"""

import itertools
import time
from collections import deque


# ----------------------------------------------------------------------
# Modelo CSP
# ----------------------------------------------------------------------
class Constraint:
    def __init__(self, scope, fn, name=""):
        self.scope = tuple(scope)
        self.fn = fn
        self.name = name

    def holds(self, asg):
        """Evalua la restriccion; asg debe tener todas las variables del scope."""
        return self.fn(*[asg[v] for v in self.scope])


class CSP:
    def __init__(self, domains, constraints):
        self.domains = {v: set(d) for v, d in domains.items()}
        self.constraints = constraints
        self.by_var = {v: [] for v in domains}
        for c in constraints:
            for v in c.scope:
                self.by_var[v].append(c)
        self.nodes = 0  # nodos visitados (para comparar eficiencia)

    # ---------------- consistencia (AC-3 generalizado) ----------------
    def revise(self, doms, c, x):
        """Elimina de doms[x] los valores sin soporte en la restriccion c."""
        others = [v for v in c.scope if v != x]
        removed = False
        for a in list(doms[x]):
            supported = False
            for combo in itertools.product(*(doms[v] for v in others)):
                asg = dict(zip(others, combo))
                asg[x] = a
                if c.holds(asg):
                    supported = True
                    break
            if not supported:
                doms[x].discard(a)
                removed = True
        return removed

    def ac3(self, doms, queue=None):
        """Propaga consistencia. Devuelve False si algun dominio queda vacio."""
        if queue is None:
            queue = deque((c, x) for c in self.constraints for x in c.scope)
        while queue:
            c, x = queue.popleft()
            if self.revise(doms, c, x):
                if not doms[x]:
                    return False
                for c2 in self.by_var[x]:
                    for y in c2.scope:
                        if y != x and (c2, y) not in queue:
                            queue.append((c2, y))
        return True

    # ---------------- validaciones ----------------
    def partial_consistent(self, asg):
        """Toda restriccion cuyo scope este asignado por completo debe cumplirse."""
        for c in self.constraints:
            if all(v in asg for v in c.scope) and not c.holds(asg):
                return False
        return True

    # ---------------- heuristica de seleccion ----------------
    def select_var(self, doms, asg, use_mrv=True):
        unassigned = [v for v in doms if v not in asg]
        if not use_mrv:
            return unassigned[0]

        def degree(v):
            return sum(1 for c in self.by_var[v]
                       if any(u not in asg for u in c.scope if u != v))

        # MRV: menor dominio; desempate: mayor grado
        return min(unassigned, key=lambda v: (len(doms[v]), -degree(v)))

    # ---------------- backtracking ----------------
    def backtrack(self, asg, doms, use_mrv, use_ac):
        self.nodes += 1
        if len(asg) == len(doms):
            return dict(asg)
        var = self.select_var(doms, asg, use_mrv)
        for val in sorted(doms[var]):
            asg[var] = val
            if self.partial_consistent(asg):
                new = {v: set(d) for v, d in doms.items()}
                new[var] = {val}
                ok = True
                if use_ac:  # mantener consistencia tras la asignacion (MAC)
                    q = deque((c, y) for c in self.by_var[var]
                              for y in c.scope if y != var)
                    ok = self.ac3(new, q)
                if ok:
                    res = self.backtrack(asg, new, use_mrv, use_ac)
                    if res:
                        return res
            del asg[var]
        return None

    def solve(self, use_mrv=True, use_ac=True):
        self.nodes = 0
        doms = {v: set(d) for v, d in self.domains.items()}
        if use_ac and not self.ac3(doms):
            return None
        return self.backtrack({}, doms, use_mrv, use_ac)


# ----------------------------------------------------------------------
# Construccion del problema SEND + MORE = MONEY
# ----------------------------------------------------------------------
LETTERS = ["S", "E", "N", "D", "M", "O", "R", "Y"]
CARRIES = ["C1", "C2", "C3", "C4"]


def build_send_more_money():
    domains = {v: range(10) for v in LETTERS}
    domains["S"] = range(1, 10)   # letra inicial no puede ser 0
    domains["M"] = range(1, 10)
    for c in CARRIES:
        domains[c] = range(2)     # acarreos 0 o 1

    cons = []
    # AllDifferent como restricciones binarias
    for a, b in itertools.combinations(LETTERS, 2):
        cons.append(Constraint((a, b), lambda x, y: x != y, f"{a}!={b}"))

    # Columnas de la suma
    cons.append(Constraint(("D", "E", "Y", "C1"),
                           lambda D, E, Y, C1: D + E == Y + 10 * C1, "col1"))
    cons.append(Constraint(("C1", "N", "R", "E", "C2"),
                           lambda C1, N, R, E, C2: C1 + N + R == E + 10 * C2, "col2"))
    cons.append(Constraint(("C2", "E", "O", "N", "C3"),
                           lambda C2, E, O, N, C3: C2 + E + O == N + 10 * C3, "col3"))
    cons.append(Constraint(("C3", "S", "M", "O", "C4"),
                           lambda C3, S, M, O, C4: C3 + S + M == O + 10 * C4, "col4"))
    cons.append(Constraint(("C4", "M"), lambda C4, M: C4 == M, "col5"))
    return CSP(domains, cons)


def word(sol, w):
    return int("".join(str(sol[ch]) for ch in w))


def validate_solution(sol):
    """Validacion final independiente del CSP: SEND + MORE == MONEY."""
    return (word(sol, "SEND") + word(sol, "MORE") == word(sol, "MONEY")
            and len({sol[l] for l in LETTERS}) == len(LETTERS)
            and sol["S"] != 0 and sol["M"] != 0)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    COMPARAR_BASICO = False  # True: corre tambien el backtracking basico (~2 min)
    configs = [
        ("Backtracking + MRV", True, False),
        ("Backtracking + MRV + AC-3 (MAC)", True, True),
    ]
    if COMPARAR_BASICO:
        configs.insert(0, ("Backtracking basico (sin MRV, sin AC-3)", False, False))
    final = None
    for name, mrv, ac in configs:
        csp = build_send_more_money()
        t0 = time.time()
        sol = csp.solve(use_mrv=mrv, use_ac=ac)
        dt = time.time() - t0
        print(f"{name}")
        print(f"  nodos visitados: {csp.nodes} | tiempo: {dt:.3f}s")
        if sol:
            print(f"  valida: {validate_solution(sol)}")
            final = sol
        else:
            print("  sin solucion")

    print("\nSolucion:")
    print({l: final[l] for l in LETTERS})
    print(f"  {word(final, 'SEND')} + {word(final, 'MORE')} = {word(final, 'MONEY')}")
