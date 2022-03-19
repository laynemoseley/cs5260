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

TradableResources = [MetallicElements, Timber, MetallicAlloys, Electronics]

# To keep things deterministic, trades are always initiated by the following percentage, which is 10% of the available resource
TradePercentage = 0.1

# In order to keep the simulation deterministic, each time a trade is initiated by the country of interest,
# a predictable resource will be traded back every time
TradeMap = {
    MetallicElements: Timber,
    Timber: MetallicAlloys,
    MetallicAlloys: Electronics,
    Electronics: MetallicElements,
}

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

    def clone(self):
        countries = deepcopy(self.countries)
        return World(countries)

    def my_country(self):
        return self.countries[0]


class Node:
    node_count = 0

    def __init__(self, parent, world, action):
        self.parent = parent
        self.world = world
        self.action = action
        self.children = []
        Node.node_count += 1
        self.id = Node.node_count

    # Represents the country of interest by which we will be judging state quality
    def my_country(self):
        return self.world.my_country()

    def __lt__(self, other):
        return self.id < other.id

    def add_child(self, child):
        self.children.append(child)


# A trade proposal from a country
class TradeFrom:
    def __init__(self, country, resource, amount):
        self.country = country
        self.resource = resource
        self.amount = amount


# A trade proposal back from a country
class TradeTo:
    def __init__(self, country, resource, amount):
        self.country = country
        self.resource = resource
        self.amount = amount


# Represents a trade between two countries, where f == TradeFrom and t == TradeTo
class Trade:
    def __init__(self, f, t):
        self.trade_from = f
        self.trade_to = t

    # validates that the trade is valid, meaning both countries have the required resources to do the trade
    def validate(self):
        f = self.trade_from
        trade_from = {}
        trade_from[f.resource] = f.amount
        if not verify_adequate_resources(f.country, trade_from):
            return False

        t = self.trade_to
        trade_to = {}
        trade_to[t.resource] = t.amount
        return verify_adequate_resources(t.country, trade_to)


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
    adjust_value(country, MetallicAlloys, -2)
    adjust_value(country, Electronics, 2)
    adjust_value(country, ElectronicsWaste, 1)

    return country


def trade_resources(trade):
    if not trade.validate():
        return False

    f = trade.trade_from
    t = trade.trade_to

    # Remove the resource that they are giving away
    adjust_value(f.country, f.resource, -f.amount)
    adjust_value(t.country, t.resource, -t.amount)

    # Add the resource that they are taking
    adjust_value(f.country, t.resource, t.amount)
    adjust_value(t.country, f.resource, f.amount)

    return True


def verify_adequate_resources(country, resources):
    for key, value in resources.items():
        if country[key] < value or value == 0:
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

    # attempt and transforms if possible
    successors = []
    for template in template_functions:
        for i, _ in enumerate(countries):
            clone = world.clone()
            country = clone.countries[i]
            template(country)
            child = Node(parent, clone, "transform")
            successors.append(child)

    # attempt trades from my country to other countries in increments of TradePercentage
    for resource in TradableResources:
        for i, _ in enumerate(countries):
            # no trades to self!
            if i == 0:
                continue

            clone = world.clone()
            my_country = clone.my_country()
            country = clone.countries[i]

            trade_from = TradeFrom(my_country, resource, math.floor(my_country[resource] * TradePercentage))
            trade_to = TradeTo(country, TradeMap[resource], math.floor(country[resource] * TradePercentage))
            trade = Trade(trade_from, trade_to)
            if trade_resources(trade) is False:
                continue

            child = Node(parent, clone, "trade")
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
    while not frontier.empty():
        item = frontier.get()

        # I had to put in the negative number into the queue because of how the queue works
        # This gets back the original value
        score = -item[0]
        node = item[1]

        # continually update the best if a new better score comes along
        if score > best[0]:
            best = (score, node)
            print(f"new best score found {score} depth: {current_depth} successor count: {successor_count}")

        successors = generate_successors(node)
        successor_count += len(successors)
        for child in successors:
            if child is None:
                continue
            score = expected_utility(child)

            # Python PriorityQueue sorts best as lowest
            # By inverting the score, the best scores will be popped off first
            frontier.put((-score, child))
            node.add_child(child)

            # update the current depth if needed
            current_depth = max(current_depth, get_depth(child))

    print(f"finished best score found {score} depth: {current_depth} successor count: {successor_count}")
    return None


countries = import_countries()
world = World(countries)
root = Node(None, world, None)
search(root, 10)
