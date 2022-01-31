# Performs a breadth-first, uniformed search
# checks for repeated values

graph = {
    "A": ["B", "C"],
    "B": ["D", "F", "A"],
    "C": ["D", "E", "A"],
    "D": ["E", "C"],
    "E": ["H", "C", "D"],
    "F": ["G", "H", "B"],
    "G": ["L", "I", "H", "F"],
    "H": ["J", "K", "E", "F", "G"],
    "I": ["L", "J", "G"],
    "J": ["M", "H", "I"],
    "K": ["M", "H"],
    "L": ["G", "I"],
}


def breadth_first_search(graph, start: str, goal: str):
    frontier = [start]
    reached = set(start)
    while len(frontier) != 0:

        print(f"Frontier {frontier}")
        print(f"Reached {reached}")

        path = frontier.pop(0)
        if goal in path:
            return path
        node = path[-1]

        for item in graph[node]:
            if item not in reached:
                frontier.append(f"{path}{item}")
                reached.add(f"{path}{item}")

        print("=====================")

    return None


result = breadth_first_search(graph, "A", "M")
print(result)
