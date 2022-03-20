# Performs a depth-first, uniformed search
# without checking for repeated values
# this follows 2.2 exactly, which means it will _never_ find M
# because of loops

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
    while len(frontier) != 0:
        print(frontier)
        path = frontier.pop(0)
        if goal in path:
            return path
        node = path[-1]
        paths = list(map(lambda vertex: f"{path}{vertex}", graph[node]))
        for idx, path in enumerate(paths):
            frontier.insert(idx, path)

    return None

result = depth_first_search(graph, "A", "M")
print(result)
