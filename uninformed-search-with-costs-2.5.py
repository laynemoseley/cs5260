from queue import PriorityQueue

graph = {
    "A": [("B", 1), ("C", 3)],
    "B": [("D", 5), ("F", 1), ("A", 1)],
    "C": [("D", 1), ("E", 2), ("A", 3)],
    "D": [("E", 4), ("C", 1)],
    "E": [("H", 1), ("C", 2), ("D", 4)],
    "F": [("G", 4), ("H", 7), ("B", 1)],
    "G": [("L", 2), ("I", 2), ("H", 5), ("F", 4)],
    "H": [("J", 3), ("K", 2), ("E", 1), ("F", 7), ("G", 5)],
    "I": [("L", 3), ("J", 1), ("G", 2)],
    "J": [("M", 1), ("H", 3), ("I", 1)],
    "K": [("M", 4), ("H", 2)],
    "L": [("G", 2), ("I", 3)],
}


def breadth_first_search(graph, start: str, goal: str):
    frontier = PriorityQueue()
    frontier.put((0, start))
    reached = { start: { 'path': start, 'cost': 0 } }
    while not frontier.empty():

        print(f"Frontier {frontier}")
        print(f"Reached {reached}")

        thing = frontier.get()
        path = thing[1]
        if goal in path:
            return path
        node = path[-1]

        for item in graph[node]:
            vertex = item[0]
            cost = item[1]
            if vertex not in reached:
                frontier.put((cost, f"{path}{vertex}"))
                reached[vertex] = { 'path': f"{path}{vertex}", 'cost': cost }

        print("=====================")

    return None


result = breadth_first_search(graph, "A", "M")
print(result)
