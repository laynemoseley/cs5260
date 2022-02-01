# Performs a depth-first, uniformed search by removing duplicates/etc
# without checking for repeated values

graph = {
    "A": ["B", "C"],
    "B": ["F", "D", "A"],
    "C": ["D", "E", "A"],
    "D": ["E", "B", "C"],
    "E": ["H", "C", "D"],
    "F": ["G", "H", "B"],
    "G": ["L", "I", "F", "H"],
    "H": ["J", "K", "E", "F", "G"],
    "I": ["L", "J", "G"],
    "J": ["M", "H", "I"],
    "K": ["M", "H"],
    "L": ["G", "I"],
}


def depth_first_search(graph, start: str, goal: str):
    frontier = [start]
    reached = { start: start }
    while len(frontier) != 0:
        
        print(f"Frontier {frontier}")
        print(f"Reached {reached}")

        path = frontier.pop(0)
        if goal in path:
            return path

        node = path[-1]
        paths = []
        for vertex in graph[node]:
            if vertex not in reached:
                new_path = f"{path}{vertex}"
                paths.append(new_path)
                reached[vertex] = new_path

        for idx, path in enumerate(paths):
            frontier.insert(idx, path)

        print("=====================")

    return None

result = depth_first_search(graph, "A", "M")
print(result)
