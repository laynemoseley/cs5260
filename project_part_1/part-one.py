from queue import PriorityQueue
from copy import deepcopy
from uuid import uuid4
from util import import_countries, import_resource_info
from random import randint
import math

# Resources definition constants
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

PersonsPerHouse = 4

# Calculation constants
Gamma = 0.5
C = -5
K = 1
X_0 = 0

resource_info = import_resource_info()


class World:
    def __init__(self, countries):
        # list of countries from csv
        self.countries = countries


class Node:
    def __init__(self, parent, world, action):
        self.parent = parent
        self.world = world
        self.action = action
        self.children = []
        self.uuid = str(uuid4())

    # Represents the country of interest by which we will be judging state quality
    def my_country(self):
        return world.countries[0]

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

    print(country)

    return country


def electronics_template(country):
    inputs = {Population: 1, MetallicElements: 3, MetallicAlloys: 2}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, MetallicElements, -3)
    adjust_value(country, MetallicAlloys, -2)
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


# Returns a list of nodes that make up a given schedule for a decendent node
# The first element in the list is the first item in the schedule
# The last item in the list will be the node passed in as a parameter
def get_schedule(node):
    schedule = [node]
    parent = node.parent
    while parent.action is not None:
        schedule.insert(0, parent)
        parent = parent.parent

    return schedule


# the number of steps in the schedule or the given node
def get_schedule_count(node):
    schedule = get_schedule(node)
    return len(schedule)


# Added for naming clarity when used
def get_depth(node):
    return get_schedule_count(node)


# Returns the very first successor from which this node comes from
# The root node is _not_ the first successor, because the root node
# has no action associated with it
def get_first_successor(node):
    schedule = get_schedule(node)
    return schedule[0]


#
# I used the state quality function by Jared Beach as a starting place: https://piazza.com/class/kyz01i5gip25bn?cid=57
#
def state_quality(node):

    result = 0
    country = node.my_country()
    for (resource, amount) in country.items():
        info = resource_info.get(resource)
        if info is None:
            continue
        weight = info["weight"]

        if resource == Housing:
            population = country[Population]

            # If there are no houses, there is no score
            if amount == 0:
                continue

            housesPerPerson = population / amount
            housingReward = population * min(housesPerPerson, 1) * weight
            if housesPerPerson < 1 / PersonsPerHouse:
                housingReward *= housesPerPerson * PersonsPerHouse
            result += housingReward
        else:
            result += info["weight"] * amount

    #   for (const r of Object.keys(country)) {
    #     const resourceName = r as keyof CountryResources;
    #     const amount = country[resourceName];
    #     if (resourceName === 'R23_Housing') {
    #       const housesPerPerson =
    #         country.R1_Population === 0 ? 0 : amount / country.R1_Population;
    #       // Reward = number of houses per person
    #       let housingReward =
    #         country.R1_Population *
    #         // Don't reward extra if there's more than 1 house per person (too many houses)
    #         Math.min(housesPerPerson, 1) *
    #         resourceDefinitions.R23_Housing.weight;
    #       // Shrink reward if housesPerPerson is very small
    #       if (housesPerPerson < 1 / PEOPLE_PER_HOUSE) {
    #         housingReward *= housesPerPerson * PEOPLE_PER_HOUSE;
    #       }

    #       result += housingReward;
    #     } else {
    #       // Every other resource is just a weighted sum
    #       result += resourceDefinitions[resourceName].weight * amount;
    #     }
    #   }

    return result


# From the requirements, this function implements the following equation:
# R(c_i, s_j) = Q_end(c_i, s_j) – Q_start(c_i, s_j) to a country c_i of a schedule s_j.
def undiscounted_reward(node):
    start = get_first_successor(node)
    return state_quality(node) - state_quality(start)


# From the requirements, this function implements the following equation:
# DR(c_i, s_j) = gamma^N * (Q_end(c_i, s_j) – Q_start(c_i, s_j)), where 0 <= gamma < 1.
def discounted_reward(node):
    count = get_schedule_count(node)
    return Gamma ** count * undiscounted_reward(node)


# from the requirements, uses the logistic function:
# https://en.wikipedia.org/wiki/Logistic_function
def schedule_probility(node):
    L = 1
    x = discounted_reward(node)

    return L / 1 + math.e ** (-K * (x - X_0))


# from the requirements, this function implements the following:
# EU(c_i, s_j) = (P(s_j) * DR(c_i, s_j)) + ((1-P(s_j)) * C), where c_i = self
def expected_utility(node):
    P = schedule_probility(node)
    DR = discounted_reward(node)
    return P * DR + ((1 - P) * C)


def generate_successors(parent):
    world = parent.world
    countries = world.countries

    template_functions = [housing_template, alloy_template, electronics_template]

    successors = []

    for template in template_functions:
        for i, _ in enumerate(countries):
            copy = deepcopy(world)
            country = copy.countries[i]
            template(country)
            child = Node(parent, copy, "transform")
            successors.append(child)

    return successors


def search(root_node, max_depth):
    frontier = PriorityQueue()
    frontier.put((0, root_node))
    current_depth = 0

    # The current best node. As searching proceeds, if a new node comes up with a better Expected Utility
    # this variable will be set to that node
    best = (-100000, root_node)

    # For inspection, keep track of the total number of successors generated over the course of the entire search
    successor_count = 0
    while not frontier.empty() and current_depth < max_depth:
        item = frontier.get()
        score = item[0]
        node = item[1]

        # continually update the best if a new better score comes along
        if score > best[0]:
            best = item
            print(f"new best score found {score} depth: {current_depth} successor count: {successor_count}")

        successors = generate_successors(node)
        successor_count += len(successors)
        for child in successors:
            if child is None:
                continue
            score = expected_utility(child)
            frontier.put((score, child))
            node.add_child(child)

            # update the current depth if needed
            current_depth = max(current_depth, get_depth(child))

    print(f"finished best score found {score} depth: {current_depth} successor count: {successor_count}")
    return None


countries = import_countries()
world = World(countries)
root = Node(None, world, None)
search(root, 10)
