import math
from fractions import Fraction

import numpy as np

# Симплекс-таблица T — список строк вида [A0, a_1, ..., a_N].
# Последняя строка T[-1] — оценки [Z, z_1 - c_1, ..., z_N - c_N].
# basis[i] — номер базисной переменной i-й строки.
# Все вычисления ведутся в дробях (Fraction), как в таблицах методички.


def frac(v: Fraction) -> Fraction:
    """Дробная часть числа: {v} = v - [v]."""
    return v - math.floor(v)


def print_table(T, basis, names, title=""):
    """Печать симплекс-таблицы в виде табл. 2.1-2.3 методички."""
    header = ["БП", "A0", *names]
    rows = [[names[b], *map(str, row)] for b, row in zip(basis, T[:-1])]
    rows.append(["z_j-c_j", *map(str, T[-1])])

    widths = [max(len(r[k]) for r in [header, *rows]) for k in range(len(header))]
    line = "-+-".join("-" * w for w in widths)

    if title:
        print(f"\n{title}")
    print(" | ".join(h.rjust(w) for h, w in zip(header, widths)))
    print(line)
    for r in rows[:-1]:
        print(" | ".join(v.rjust(w) for v, w in zip(r, widths)))
    print(line)
    print(" | ".join(v.rjust(w) for v, w in zip(rows[-1], widths)))


def make_z_row(T, basis, cost):
    """Строка оценок: Z = sum(c_Б * A0), z_j - c_j = sum(c_Б * a_ij) - c_j."""
    rows = T[:-1] if len(T) > len(basis) else T
    width = len(rows[0])
    z_row = []
    for col in range(width):
        z = sum((cost[b] * row[col] for b, row in zip(basis, rows)), Fraction(0))
        z_row.append(z if col == 0 else z - cost[col - 1])
    return z_row


def pivot(T, basis, r, k):
    """Жорданово исключение: переменная x_k входит в базис вместо строки r."""
    p = T[r][k + 1]
    T[r] = [v / p for v in T[r]]
    for i, row in enumerate(T):
        if i != r and row[k + 1] != 0:
            f = row[k + 1]
            T[i] = [a - f * b for a, b in zip(row, T[r])]
    basis[r] = k


def primal_simplex(T, basis, names, verbose=True):
    """Симплекс-метод (максимизация). Возвращает 'optimal' или 'unbounded'."""
    while True:
        d = T[-1][1:]
        # Вводим в базис столбец с наименьшей отрицательной оценкой
        k = min(range(len(d)), key=lambda j: d[j])
        if d[k] >= 0:
            return "optimal"

        # Выводим строку по минимальному симплексному отношению A0 / a_ik
        candidates = [i for i in range(len(basis)) if T[i][k + 1] > 0]
        if not candidates:
            return "unbounded"
        r = min(candidates, key=lambda i: T[i][0] / T[i][k + 1])

        pivot(T, basis, r, k)
        if verbose:
            print_table(T, basis, names, f"Симплекс: {names[k]} входит в базис")


def dual_simplex(T, basis, names, verbose=True):
    """Двойственный симплекс-метод. Возвращает 'optimal' или 'infeasible'."""
    while True:
        # Выводим строку с наименьшим (отрицательным) свободным членом
        r = min(range(len(basis)), key=lambda i: T[i][0])
        if T[r][0] >= 0:
            return "optimal"

        # Вводим столбец по минимуму |(z_j - c_j) / a_rj| при a_rj < 0
        candidates = [j for j in range(len(T[r]) - 1) if T[r][j + 1] < 0]
        if not candidates:
            return "infeasible"
        k = min(candidates, key=lambda j: T[-1][j + 1] / -T[r][j + 1])

        out = names[basis[r]]
        pivot(T, basis, r, k)
        if verbose:
            print_table(
                T,
                basis,
                names,
                f"Двойственный симплекс: {out} выходит, {names[k]} входит в базис",
            )


def two_phase(T, basis, names, cost, verbose=True):
    """
    Двухэтапный метод для строк с отрицательной правой частью:
    на первом этапе вводятся искусственные переменные и минимизируется их сумма.
    """
    n_real = len(names)
    artificial = []
    for i in range(len(basis)):
        if T[i][0] < 0:
            T[i] = [-v for v in T[i]]
            for row in T:
                row.append(Fraction(0))
            T[i][-1] = Fraction(1)
            basis[i] = len(names)
            artificial.append(len(names))
            names.append(f"y{len(artificial)}")

    # Этап 1: max(-sum(y))
    cost1 = [Fraction(0)] * n_real + [Fraction(-1)] * len(artificial)
    T[-1] = make_z_row(T, basis, cost1)
    if verbose:
        print_table(T, basis, names, "Этап 1: исходная таблица с искусственными переменными")
    primal_simplex(T, basis, names, verbose)
    if T[-1][0] < 0:
        return "infeasible"

    # Выводим оставшиеся (нулевые) искусственные переменные из базиса
    for i in reversed(range(len(basis))):
        if basis[i] in artificial:
            k = next((j for j in range(n_real) if T[i][j + 1] != 0), None)
            if k is None:
                del T[i], basis[i]  # строка линейно зависима
            else:
                pivot(T, basis, i, k)

    # Удаляем столбцы искусственных переменных
    for i in range(len(T)):
        T[i] = T[i][: n_real + 1]
    del names[n_real:]

    # Этап 2: исходная целевая функция
    T[-1] = make_z_row(T, basis, cost)
    if verbose:
        print_table(T, basis, names, "Этап 2: исходная целевая функция")
    return primal_simplex(T, basis, names, verbose)


def gomory(
    c: list[int],
    A_ub: list[list[int]],
    b_ub: list[int],
    max: bool = True,
    max_iter: int = 100,
    verbose: bool = True,
) -> tuple[np.ndarray | None, Fraction | None]:
    """
    Решает полностью целочисленную задачу ЛП методом отсечения Гомори.
    c: коэффициенты целевой функции
    A_ub, b_ub: матрица и вектор ограничений вида A*x <= b (целые числа!)
    max: True - максимизация, False - минимизация
    Все переменные x_j >= 0 и целые. Коэффициенты A и b должны быть целыми,
    тогда слабые переменные тоже целые и отсечение (2.9) правильное.
    """
    n = len(c)
    m = len(A_ub)

    # Таблица решается на максимизацию: для минимизации инвертируем c
    cost = [Fraction(v) if max else -Fraction(v) for v in c] + [Fraction(0)] * m
    names = [f"x{j + 1}" for j in range(n + m)]

    # Каноническая форма (2.2): к каждому ограничению добавляем слабую переменную
    T = [
        [Fraction(b_ub[i]), *map(Fraction, A_ub[i]), *(Fraction(int(k == i)) for k in range(m))]
        for i in range(m)
    ]
    basis = [n + i for i in range(m)]
    T.append(make_z_row(T, basis, cost))

    if verbose:
        print_table(T, basis, names, "Исходная симплекс-таблица")

    # Этапы 1-2: решаем задачу с отброшенным условием целочисленности
    if all(row[0] >= 0 for row in T[:-1]):
        status = primal_simplex(T, basis, names, verbose)
    elif all(d >= 0 for d in T[-1][1:]):
        # Базис недопустим, но оценки неотрицательны - двойственный симплекс
        status = dual_simplex(T, basis, names, verbose)
    else:
        status = two_phase(T, basis, names, cost, verbose)

    if status != "optimal":
        print(f"\nЗадача ЛП без условия целочисленности: {status}, решения нет")
        return None, None

    for iteration in range(1, max_iter + 1):
        # Проверка на целочисленность всех базисных переменных
        fractional = [i for i in range(len(basis)) if frac(T[i][0]) != 0]
        if not fractional:
            break

        # Этап 3: строка с наибольшей дробной частью свободного члена
        r = min(fractional, key=lambda i: -frac(T[i][0]))
        beta = T[r][0]
        alphas = [(j, a) for j, a in enumerate(T[r][1:]) if frac(a) != 0]

        if verbose:
            terms = "".join(f" - {{{a}}}{names[j]}" for j, a in alphas)
            simple = "".join(f" - {frac(a)}{names[j]}" for j, a in alphas)
            print(f"\n=== Отсечение {iteration} по {names[basis[r]]}-строке ===")
            print(f"{{{beta}}}{terms} <= 0")
            print(f"{frac(beta)}{simple} <= 0")

        # Отсечение (2.9) с новой слабой переменной s:
        # -{a_1}x_1 - ... - {a_N}x_N + s = -{beta}
        s = len(names)
        names.append(f"x{s + 1}")
        cost.append(Fraction(0))
        for row in T:
            row.append(Fraction(0))
        cut = [-frac(beta), *(-frac(a) for a in T[r][1:-1]), Fraction(1)]
        T.insert(-1, cut)
        basis.append(s)

        if verbose:
            print_table(T, basis, names, "Таблица с добавленным отсечением")

        # Этап 4: решаем расширенную задачу двойственным симплексом
        if dual_simplex(T, basis, names, verbose) != "optimal":
            print("\nЦелочисленного решения нет")
            return None, None
    else:
        print(f"\nПревышено число итераций ({max_iter})")
        return None, None

    x = [Fraction(0)] * n
    for i, b in enumerate(basis):
        if b < n:
            x[b] = T[i][0]

    z = T[-1][0] if max else -T[-1][0]
    return np.array([int(v) for v in x]), z


def solve(c, A_ub, b_ub, max=True):
    opt_x, opt_z = gomory(c, A_ub, b_ub, max=max)

    print("\n=== РЕЗУЛЬТАТ ===")
    if opt_x is None:
        print("Решения нет")
        return
    plan = ", ".join(f"X{j + 1} = {v}" for j, v in enumerate(opt_x))
    print(f"Оптимальный план: {plan}")
    print(f"{'Максимальное' if max else 'Минимальное'} значение Z = {opt_z}")


# ==========================================
# ПРИМЕР 2.1 из методички
# Max Z = x1 + x2
# -x1 + 3*x2 <= 3
# 3*x1 - x2 <= 3
# x1, x2 >= 0, целые
# Ответ: x = (1, 1), Z = 2
# ==========================================
def main():
    print("############ Пример 2.1 ############")
    solve(
        c=[1, 1],
        A_ub=[
            [-1, 3],
            [3, -1],
        ],
        b_ub=[3, 3],
        max=True,
    )

    print("\n\n############ Вариант ############")
    # Min Z = 2*x1 + 2*x2, x1, x2 >= 0, целые
    solve(
        c=[2, 2],
        A_ub=[
            [3, -4],
            [8, 7],
            [-4, -3],
            [-3, 2],
        ],
        b_ub=[0, 56, -6, 12],
        max=False,
    )


if __name__ == "__main__":
    main()
