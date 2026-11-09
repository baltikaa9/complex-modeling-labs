from .solver import solve

# Данные задачи 3; при необходимости замените спрос на свой вариант.
D = (2, 3, 4, 4)
h, M, B, i0 = 2, 5, 6, 3
cost_table = {0: 0, 1: 12, 2: 14, 3: 16, 4: 18, 5: 20, 6: 22}


def c(x):
    return cost_table[x]


def main():
    solve(D, h, M, B, i0, c)


if __name__ == "__main__":
    main()
