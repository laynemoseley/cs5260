# Performs a depth-first, uniformed search by removing duplicates/etc
# without checking for repeated values

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


def depth_first_search(graph, start: str, goal: str):
    frontier = [start]
    reached = set()
    while len(frontier) != 0:
        path = frontier.pop(0)
        if goal in path:
            return path
        node = path[-1]
        if path not in reached:
            for item in graph[node]:
                frontier.append(f"{path}{item}")
            reached.add(path)

    return None

result = depth_first_search(graph, "A", "M")
print(result)
