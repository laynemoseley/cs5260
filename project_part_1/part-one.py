from queue import PriorityQueue
from copy import deepcopy
from util import import_countries
from random import randint
import math

Population = "R1"
MetallicElements = "R2"
Timber = "R3"
MetallicAlloys = "R21"
Electronics = "R22"
Housing = "R23"
WasteOne = "R21'"
WasteTwo = "R22'"
HousingWaste = "R23'"
MetallicAlloysWaste = "R21'"
ElectronicsWaste = "R22'"


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

    # I added this because the priority queue needed it in case there were two scores that were the same
    # TODO: Add some logic here?
    def __lt__(self, other):
        return True

    def add_child(self, child):
        self.children.append(child)


def housing_template(country):

    inputs = {Population: 5, MetallicElements: 1, Timber: 5, MetallicAlloys: 3}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, Housing, 1)
    adjust_value(country, HousingWaste, 1)
    adjust_value(country, Timber, -5)
    adjust_value(country, MetallicElements, -1)
    adjust_value(country, MetallicAlloys, -3)

    return country


def alloy_template(country):
    inputs = {Population: 1, MetallicElements: 2}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, MetallicElements, -2)
    adjust_value(country, MetallicAlloys, 1)
    adjust_value(country, MetallicAlloysWaste, 1)

    return country


def electronics_template(country):
    inputs = {Population: 1, MetallicElements: 3, MetallicAlloys: 2}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, MetallicElements, -3)
    adjust_value(country, MetallicElements, -2)
    adjust_value(country, Electronics, 2)
    adjust_value(country, ElectronicsWaste, 1)

    return country


def verify_adequate_resources(country, resources):
    for key, value in resources.items():
        if country[key] < value:
            return False

    return True


def adjust_value(country, name, adjustment):
    if country.get(name) is None:
        country[name] = 0

    country[name] += adjustment


# Returns a list of nodes that make up a the given schedule
# The first element in the list is the first item in the schedule
# The last item in the list will be the node passed in as a parameter
# Because it is part of the schedule
def get_schedule(node):
    schedule = [node]
    parent = node.parent
    while parent.action is not None:
        schedule.insert(0, parent)
        parent = parent.parent

    return schedule


def get_schedule_count(node):
    schedule = get_schedule(node)
    return len(schedule)


# Returns the very first successor from which this node comes from
# The root node is _not_ the first successor, because the root node
# has no action associated with it
def get_first_successor(node):
    schedule = get_schedule(node)
    return schedule[0]


def state_quality(node):
    return randint(0, 10)


# From the requirements, this function implements the following equation:
# R(c_i, s_j) = Q_end(c_i, s_j) – Q_start(c_i, s_j) to a country c_i of a schedule s_j.
def undiscounted_reward(node):
    start = get_first_successor(node)
    return state_quality(node) - state_quality(start)


# From the requirements, this function implements the following equation:
# DR(c_i, s_j) = gamma^N * (Q_end(c_i, s_j) – Q_start(c_i, s_j)), where 0 <= gamma < 1.
def discounted_reward(node):

    # This value can be tweaked
    gamma = 0.5
    count = get_schedule_count(node)
    return gamma ** count * undiscounted_reward(node)


# from the reading, uses the logistic function:
# https://en.wikipedia.org/wiki/Logistic_function
def schedule_probility(node):
    L = 1
    k = 1
    x = discounted_reward(node)
    x_0 = 0

    return L / 1 + math.e ** (-k * (x - x_0))


# from the requirements, this function implements the following:
# EU(c_i, s_j) = (P(s_j) * DR(c_i, s_j)) + ((1-P(s_j)) * C), where c_i = self
def expected_utility(node):
    C = -5
    P = schedule_probility(node)
    DR = discounted_reward(node)
    return P * DR + ((1 - P) * C)


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

    print(f"Successors generated: {len(successors)}")

    return successors


def depth_first_search(node, depth):
    frontier = PriorityQueue()
    frontier.put((0, node))
    current_depth = 0
    while not frontier.empty() and current_depth < depth:
        goodestNode = frontier.get()
        successors = generate_successors(goodestNode[1])
        for child in successors:
            if child is None:
                continue
            score = expected_utility(child)
            frontier.put((score, child))

        current_depth += 1

    return None


countries = import_countries()
world = World(countries)
print(world.countries)
root = Node(None, world, None)
depth_first_search(root, 10)
