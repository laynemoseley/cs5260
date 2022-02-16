from queue import PriorityQueue
from copy import deepcopy
from util import import_countries

Population = 'r1'
MetallicElements = 'r2'
Timber = 'r3'
MetallicAlloys = 'r21'
Electronics = 'r22'
Housing = 'r23'
WasteOne = "r21'"
WasteTwo = "r22'"
HousingWaste = "r23'"

class World:
    def __init__(self, countries):
        # list of countries from csv
        self.countries = countries

    def country_of_interest(self):
        return self.countries[0]

class Node:
    def __init__(self, parent, country, action):
        self.parent = parent
        self.country = country
        self.action = action
        self.children = []

    def add_child(self, child):
        self.children.append(child)

countries = import_countries()
world = World(countries)
print(world.countries)

def housing_template(country):
    if country[Population] < 5:
        return None

    if country[MetallicElements] < 1:
        return None

    if country[Timber] < 5:
        return None

    if country[MetallicAlloys] > 3:
        return None

    country[Housing] += 1
    country[HousingWaste] += 1
    country[Timber] -= 5
    country[MetallicElements] -= 1
    country[MetallicAlloys] -= 3
    return country

def state_quality(node):
    return -1

def generate_successors(node):
    housing = housing_template(node.country)
    housing_node = Node(node, housing, 'transform')

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