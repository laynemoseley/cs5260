from queue import PriorityQueue
from copy import deepcopy
from util import import_countries
from random import randint

Population = "R1"
MetallicElements = "R2"
Timber = "R3"
MetallicAlloys = "R21"
Electronics = "R22"
Housing = "R23"
WasteOne = "R21'"
WasteTwo = "R22'"
HousingWaste = "R23'"


class World:
    def __init__(self, countries):
        # list of countries from csv
        self.countries = countries

    def country_of_interest(self):
        return self.countries[0]


class Node:
    def __init__(self, parent, world, action):
        self.parent = parent
        self.world = world
        self.action = action
        self.children = []

    def add_child(self, child):
        self.children.append(child)


def housing_template(country):
    if country[Population] < 5:
        return None

    if country[MetallicElements] < 1:
        return None

    if country[Timber] < 5:
        return None

    if country[MetallicAlloys] > 3:
        return None

    adjust_value(country, Housing, 1)
    adjust_value(country, HousingWaste, 1)
    adjust_value(country, Timber, -5)
    adjust_value(country, MetallicElements, -1)
    adjust_value(country, MetallicAlloys, -3)

    return country


def adjust_value(country, name, adjustment):
    if country.get(name) is None:
        country[name] = 0

    country[name] += adjustment


def alloy_template(country):
    return country


def electronics_template(country):
    return country


def state_quality(node):
    return randint(0, 100000)


def generate_successors(node):
    world = node.world
    countries = world.countries

    template_functions = [housing_template, alloy_template, electronics_template]

    successors = []

    for template in template_functions:
        for i, _ in enumerate(countries):
            copy = deepcopy(world)
            country = copy.countries[i]
            template(country)
            child = Node(node, copy, "transform")
            successors.append(child)

    print(len(successors))

    return successors

    world_one = deepcopy(node.world)
    housing_template(world_one.country_of_interest())
    housing_node = Node(node, world_one, "transform")

    world_two = deepcopy(node.world)
    alloy_template(world_two.country_of_interest())
    alloy_node = Node(node, world_two, "transform")

    world_three = deepcopy(node.world)
    electronics_template(world_three.country_of_interest())
    electronics_node = Node(node, world_three, "transform")

    return [housing_node, alloy_node, electronics_node]


def depth_first_search(node, depth):
    frontier = PriorityQueue()
    frontier.put((0, node))
    schedule = []
    actual_depth = 0
    while not frontier.empty() and actual_depth < depth:
        print(schedule)
        goodestNode = frontier.get()
        schedule.append(goodestNode[1].action)
        successors = generate_successors(goodestNode[1])
        for child in successors:
            if child is None:
                continue
            score = state_quality(child)
            frontier.put((score, child))

        actual_depth += 1

    return None


countries = import_countries()
world = World(countries)
print(world.countries)
root = Node(None, world, "????")
depth_first_search(root, 10)
