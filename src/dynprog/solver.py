from collections.abc import Callable
from functools import lru_cache
from math import inf


def solve(D, h, M, B, i0, cost: Callable[[int], int]) -> None:
    """Печатает таблицы динамического программирования и оптимальный план."""
    D = tuple(D)
    N = len(D)

    @lru_cache(None)
    def f(t, i):
        if t == N:
            return (0, None) if i == 0 else (inf, None)

        best = (inf, None)
        for x in range(B + 1):
            j = i + x - D[t]
            if 0 <= j <= M:
                value = cost(x) + h * j + f(t + 1, j)[0]
                if value < best[0]:
                    best = (value, x)
        return best

    def cell(t, i, x):
        j = i + x - D[t]
        if not 0 <= j <= M:
            return None
        following = f(t + 1, j)[0]
        if following == inf:
            return None
        current = cost(x) + h * j + following
        return current, f"{cost(x)}+{h * j}+{following}={current}"

    width = 14
    for n in range(1, N + 1):
        t = N - n
        print(f"\nТаблица {n} - расчет f{n}(i), спрос d{n} = {D[t]}")
        print(
            "i\\x".ljust(6)
            + "".join(str(x).ljust(width) for x in range(B + 1))
            + "x%d(i)".ljust(8) % n
            + f"f{n}(i)"
        )
        rows = [i0] if n == N else range(M + 1)
        for i in rows:
            cells = {x: cell(t, i, x) for x in range(B + 1)}
            valid = {x: value for x, value in cells.items() if value is not None}
            if not valid:
                continue
            minimum = min(value[0] for value in valid.values())
            choices = "/".join(
                str(x) for x, value in valid.items() if value[0] == minimum
            )
            label = f"i0={i}" if n == N else str(i)
            line = label.ljust(6)
            for x in range(B + 1):
                value = cells[x]
                line += (value[1] if value is not None else "").ljust(width)
            print(line + choices.ljust(8) + str(minimum))

    initial_cost, _ = f(0, i0)
    if initial_cost == inf:
        raise ValueError("Для заданных параметров допустимого плана нет")

    inventory, plan = i0, []
    for t in range(N):
        production = f(t, inventory)[1]
        if production is None:
            raise ValueError("Для заданных параметров допустимого плана нет")
        plan.append(production)
        inventory += production - D[t]

    print("\nПлан по месяцам:", plan)
    print("Минимальные затраты:", initial_cost)
