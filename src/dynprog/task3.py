from .solver import solve

# Данные задачи 3; при необходимости замените спрос на свой вариант.
D = (3, 4, 4, 2)
h, M, B, i0 = 2, 4, 6, 2
cost_table = {0: 0, 1: 13, 2: 15, 3: 17, 4: 19, 5: 21, 6: 23}


def c(x):
    return cost_table[x]


def main():
    solve(D, h, M, B, i0, c)


if __name__ == "__main__":
    main()
