"""Задача 5: распределение кредита, вариант 11."""

# Доход g_i(x): выделенная сумма -> доход из таблицы варианта 11.
g = [
    {0: 0, 30: 10, 50: 16, 90: 30},
    {0: 0, 30: 12, 50: 32, 90: 45},
    {0: 0, 30: 15, 50: 25, 90: 32},
]
C, step = 90, 10


def main():
    credit_amounts = range(0, C + 1, step)
    values = [{amount: 0 for amount in credit_amounts}]
    decisions = []

    for n, income_by_amount in enumerate(g, start=1):
        current_values, current_decisions = {}, {}
        print(f"\nТаблица f{n}(c)")
        for amount in credit_amounts:
            cells = {
                allocation: income + values[-1][amount - allocation]
                for allocation, income in income_by_amount.items()
                if allocation <= amount
            }
            current_values[amount] = max(cells.values())
            current_decisions[amount] = min(
                allocation
                for allocation, value in cells.items()
                if value == current_values[amount]
            )
            if amount in (30, 50, 90):
                details = "  ".join(
                    f"x={allocation}: "
                    f"{income_by_amount[allocation]}+" 
                    f"{values[-1][amount - allocation]}={value}" for allocation, value in cells.items()
                )
                print(
                    f"c={amount}: {details}  ->  "
                    f"x{n}*={current_decisions[amount]}, "
                    f"f{n}={current_values[amount]}"
                )
        values.append(current_values)
        decisions.append(current_decisions)

    remaining, plan = C, []
    for n in range(len(g) - 1, -1, -1):
        allocation = decisions[n][remaining]
        plan.append(allocation)
        remaining -= allocation
    plan.reverse()
    print("\nРаспределение:", plan, "Доход:", values[-1][C])


if __name__ == "__main__":
    main()
