"""Задача 10: кратчайший путь, вариант 11."""

E = {
    (1, 2): 2,
    (1, 3): 5,
    (1, 4): 7,
    (2, 5): 9,
    (2, 7): 4,
    (3, 5): 6,
    (3, 6): 2,
    (3, 7): 1,
    (4, 5): 3,
    (4, 6): 5,
    (4, 7): 2,
    (5, 8): 6,
    (5, 9): 7,
    (6, 8): 8,
    (6, 9): 2,
    (7, 9): 6,
    (8, 10): 7,
    (9, 10): 9,
}
END = 10


def main():
    distance = {END: 0}
    for node in range(9, 0, -1):
        options = {
            target: weight + distance[target]
            for (source, target), weight in E.items()
            if source == node
        }
        distance[node] = min(options.values())
        best = [target for target, value in options.items() if value == distance[node]]
        choices = ", ".join(
            f"через {target}: {E[(node, target)]}+{distance[target]}={value}" for target, value in options.items()
        )
        print(
            f"s={node}: {choices}  ->  f={distance[node]}, "
            f"едем в {'/'.join(map(str, best))}"
        )

    def routes(node):
        if node == END:
            return [[END]]
        return [
            [node, *route]
            for (source, target), weight in E.items()
            if source == node and weight + distance[target] == distance[node]
            for route in routes(target)
        ]

    print()
    for node in range(1, END):
        paths = ["-".join(map(str, route)) for route in routes(node)]
        print(f"из {node}: f={distance[node]}, маршруты: {paths}")


if __name__ == "__main__":
    main()
