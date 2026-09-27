import math

import numpy as np
from scipy.optimize import linprog


def branch_and_bound_min(c, A_ub, b_ub, initial_bounds):
    """
    Решает задачу ЦЛП на МИНИМИЗАЦИЮ методом ветвей и границ.
    c: коэффициенты целевой функции (для минимизации)
    A_ub, b_ub: матрица и вектор ограничений вида A*x <= b
    initial_bounds: начальные границы переменных [(min, max), ...]
    """

    # ВАЖНО: linprog УЖЕ минимизирует, поэтому знаки НЕ меняем!
    # c_min = c  (можно просто передать c напрямую)

    stack = [initial_bounds]

    # ВАЖНО: для минимизации начальное значение рекорда = +бесконечность
    best_z = float("inf")
    best_x = None

    EPS = 1e-5

    while stack:
        bounds = stack.pop()

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

        if not res.success:
            continue

        z = res.fun  # ВАЖНО: НЕ меняем знак, т.к. linprog уже минимизирует
        x = res.x

        # ВАЖНО: для минимизации отсечение работает наоборот
        # Если текущая оценка ЛП УЖЕ БОЛЬШЕ или равна рекорду,
        # то целочисленное решение здесь будет только хуже (ещё больше)
        if z >= best_z - EPS:
            continue

        is_integer = all(abs(val - round(val)) < EPS for val in x)

        if is_integer:
            # ВАЖНО: обновляем рекорд, если нашли МЕНЬШЕ значение
            if z < best_z:
                best_z = z
                best_x = np.round(x).astype(int)
                print(f"[Найдено целое решение] Z = {best_z}, X = {best_x}")
        else:
            fractional_parts = [abs(val - round(val)) for val in x]
            branch_var_idx = np.argmax(fractional_parts)
            val = x[branch_var_idx]

            bounds_left = list(bounds)
            current_min, current_max = bounds_left[branch_var_idx]
            bounds_left[branch_var_idx] = (current_min, math.floor(val))
            stack.append(bounds_left)

            bounds_right = list(bounds)
            bounds_right[branch_var_idx] = (math.ceil(val), current_max)
            stack.append(bounds_right)

    return best_x, best_z


def branch_and_bound(
    c: list[int],
    A_ub: list[list[int]],
    b_ub: list[int],
    initial_bounds: list[tuple[int | None, int | None]],
    max: bool = True,
) -> tuple[np.ndarray, float]:
    """
    Решает задачу ЦЛП методом ветвей и границ.
    c: коэффициенты целевой функции (для максимизации)
    A_ub, b_ub: матрица и вектор ограничений вида A*x <= b
    initial_bounds: начальные границы переменных [(min, max), ...]
    """

    # scipy.optimize.linprog решает задачу МИНИМИЗАЦИИ.
    # Чтобы решить задачу МАКСИМИЗАЦИИ, мы инвертируем знаки коэффициентов c.
    if max:
        c_min = [-val for val in c]
        best_z = -float("inf")
    else:
        c_min = c
        best_z = float("inf")

    best_x = None
    stack = [initial_bounds]
    EPS = 1e-5

    while stack:
        bounds = stack.pop()

        res = linprog(c_min, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

        print(res)

        if not res.success:
            continue

        if max:
            z = -res.fun  # Возвращаем знак обратно для максимизации
        else:
            z = res.fun

        x = res.x

        # 2. Отсечение по оценке (Pruning by bound)
        # Если текущая оценка ЛП хуже или равна уже найденному целому решению,
        # дальше ветвить нет смысла (целое решение здесь будет еще хуже).
        if (max and z <= best_z + EPS) or (not max and z >= best_z - EPS):
            continue

        # 3. Проверка на целочисленность
        is_integer = all(abs(val - round(val)) < EPS for val in x)

        if is_integer:
            # Нашли целочисленный план!
            if (max and z > best_z) or (not max and z < best_z):
                best_z = z
                best_x = np.round(x).astype(int)
                print(f"[Найдено целое решение] Z = {best_z}, X = {best_x}")
        else:
            # 4. Ветвление
            # Выбираем переменную с наибольшей дробной частью (эвристика)
            fractional_parts = [abs(val - round(val)) for val in x]
            branch_var_idx = np.argmax(fractional_parts)
            val = x[branch_var_idx]

            # Создаем две новые подзадачи
            # Ветвь 1: x_i <= floor(val)
            bounds_left = list(bounds)
            current_min, current_max = bounds_left[branch_var_idx]
            bounds_left[branch_var_idx] = (current_min, math.floor(val))
            stack.append(bounds_left)

            # Ветвь 2: x_i >= ceil(val)
            bounds_right = list(bounds)
            bounds_right[branch_var_idx] = (math.ceil(val), current_max)
            stack.append(bounds_right)

    return best_x, best_z


# ==========================================
# ПРИМЕР: Задача 4.1 из методички
# Max Z = 2*x1 + 3*x2
# 5*x1 + 7*x2 <= 35
# 4*x1 + 9*x2 <= 36
# x1, x2 >= 0, целые
# ==========================================
def main():
    c = [2, 2]
    A_ub = [
        [3, -4],
        [8, 7],
        [-4, -3],
        [-3, 2],
    ]
    b_ub = [0, 56, -6, 12]
    initial_bounds = [
        (None, None),
        (None, None),
    ]  # x1 >= 0, x2 >= 0, без верхних пределов

    opt_x, opt_z = branch_and_bound(c, A_ub, b_ub, initial_bounds, max=False)

    print("\n=== РЕЗУЛЬТАТ ===")
    print(f"Оптимальный план: X1 = {opt_x[0]}, X2 = {opt_x[1]}")
    print(f"Максимальное значение Z = {opt_z}")


if __name__ == "__main__":
    main()
