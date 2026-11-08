from .solver import solve

# Данные варианта 22.
D = (2, 3, 4)
h, M, B, i0, k, l = 2, 5, 6, 3, 9, 2


def c(x):
    return 0 if x == 0 else k + l * x


def main():
    solve(D, h, M, B, i0, c)


if __name__ == "__main__":
    main()
