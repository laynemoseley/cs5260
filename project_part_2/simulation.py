import math
from queue import PriorityQueue
from copy import deepcopy
from time import time
from util import import_countries, import_resource_info, reset_results, update_results, finish_results

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

ResourceNames = {
    Population: "Population",
    MetallicElements: "Metallic Elements",
    Timber: "Timber",
    MetallicAlloys: "Metallic Alloys",
    Electronics: "Electronics",
    Housing: "Housing",
    HousingWaste: "Housing Waste",
    MetallicAlloysWaste: "Metallic Alloys Waste",
    ElectronicsWaste: "Electronics Waste",
}

# Resources that are available for a trade
TradableResources = [MetallicElements, Timber, Electronics]

# To keep things deterministic, trades are always initiated by the following percentage, which is 10% of the available resource
TradePercentage = 0.2

# In order to keep the simulation deterministic, each time a trade is initiated by the country of interest,
# a predictable resource will be traded back every time
TradeMap = {
    MetallicElements: Timber,
    Timber: Electronics,
    Electronics: MetallicElements,
}

PersonsPerHouse = 4

# Calculation constants
Gamma = 0.95
C = -10
K = 1
X_0 = 0

resource_info = import_resource_info("1")


class SearchResult:
    def __init__(self, best_score, best_node, depth_reached, seconds_elapsed, node_count, frontier_size, timeout):
        self.best_score = best_score
        self.best_node = best_node
        self.best_schedule = Schedule(best_node)
        self.depth_reached = depth_reached
        self.seconds_elapsed = seconds_elapsed
        self.node_count = node_count
        self.frontier_size = frontier_size
        self.search_type = "best_first"
        self.data_set = "0"
        self.timeout = timeout


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


class Schedule:
    def __init__(self, node):
        self.node = node

    def print(self):
        nodes = get_schedule(self.node)

        if len(nodes) == 0:
            return ""

        result = "[\n"
        for n in nodes:
            result += f"{n.action.strip()}\n"
        result += "]"

        return result


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

    def print(self):
        f = self.trade_from
        from_name = f.country["Country"]
        t = self.trade_to
        to_name = t.country["Country"]

        return f"""
(TRANSFER BETWEEN {from_name} and {to_name} 
    ({ResourceNames[f.resource]} {f.amount} exchanged for {ResourceNames[t.resource]} {t.amount})
)
"""


def housing_template(country):

    inputs = {Population: 5, MetallicElements: 1, Timber: 5, MetallicAlloys: 3}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, Housing, 1)
    adjust_value(country, HousingWaste, 1)
    adjust_value(country, Timber, -5)
    adjust_value(country, MetallicElements, -1)
    adjust_value(country, MetallicAlloys, -3)

    return f"""
(TRANSFORM {country["Country"]}
    (INPUTS  (Population {inputs[Population]})
             (Metallic Elements {inputs[MetallicElements]})
             (Timber {inputs[Timber]})
             (Metallic Alloys {inputs[MetallicAlloys]})
    )
    (OUTPUTS (Housing {1})
             (Housing Waste {1})
    )
)
"""


def alloy_template(country):
    inputs = {Population: 1, MetallicElements: 2}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, MetallicElements, -2)
    adjust_value(country, MetallicAlloys, 1)
    adjust_value(country, MetallicAlloysWaste, 1)

    return f"""
(TRANSFORM {country["Country"]}
    (INPUTS  (Population {inputs[Population]})
             (Metallic Elements {inputs[MetallicElements]})
    )
    (OUTPUTS (Metallic Alloys {1})
             (Metallic Alloys Waste {1})
    )
)
"""


def electronics_template(country):
    inputs = {Population: 1, MetallicElements: 3, MetallicAlloys: 2}
    if not verify_adequate_resources(country, inputs):
        return None

    adjust_value(country, MetallicElements, -3)
    adjust_value(country, MetallicAlloys, -2)
    adjust_value(country, Electronics, 2)
    adjust_value(country, ElectronicsWaste, 1)

    return f"""
(TRANSFORM {country["Country"]}
    (INPUTS  (Population {inputs[Population]})
             (Metallic Elements {inputs[MetallicElements]})
             (Metallic Alloys {inputs[MetallicAlloys]})
    )
    (OUTPUTS (Electronics {2})
             (ElectronicsWaste {1})
    )
)
"""


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
    # Root node has no parent, therefore no schedule
    if node.parent is None:
        return []

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
# However, I did adjust to my own ideas
def state_quality(node):
    result = 0

    # State Quality is always counted against the "self" country
    country = node.my_country()
    for (resource, amount) in country.items():
        info = resource_info.get(resource)
        if info is None:
            continue

        weight = info["weight"]

        if resource == Housing:

            # Housing is extremely important, therefore any housing is worth more than all other
            # resources combined
            # In order to incentivize, housing becomes increasingly more important
            # *until* there is enough for the entire population
            # at which point it loses value significantly

            # current population
            population = country[Population]

            # how much is needed by the population
            housing_needed_by_population = math.ceil(population / PersonsPerHouse)

            # How many are currently satisfied
            houses_per_person = 0 if amount == 0 else math.ceil(population / amount)

            # if there is enough housing, multipy massively to incentivize
            if houses_per_person < housing_needed_by_population:
                diff = housing_needed_by_population - houses_per_person
                result += (weight * amount or 1) * (5 * diff)
            else:
                # If they have enough, use the same rule as other resources
                result += weight * amount
        else:
            # Otherwise, multiply the amount of the resource by the weight
            result += weight * amount

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
    return (Gamma ** count) * undiscounted_reward(node)


# from the requirements, uses the logistic function:
# https://en.wikipedia.org/wiki/Logistic_function
def schedule_probability(node):
    L = 1
    x = discounted_reward(node)

    return L / 1 + math.e ** (-K * (x - X_0))


# from the requirements, this function implements the following:
# EU(c_i, s_j) = (P(s_j) * DR(c_i, s_j)) + ((1-P(s_j)) * C), where c_i = self
def expected_utility(node):
    P = schedule_probability(node)
    DR = discounted_reward(node)
    return (P * DR) + ((1 - P) * C)


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
            action = template(country)
            if action is None:
                continue
            child = Node(parent, clone, action)
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

            child = Node(parent, clone, trade.print())
            successors.append(child)

    return successors


def best_first_search(root_node, max_depth, timeout, frontier_size, on_new_schedule_found):
    start_time = time()
    frontier = PriorityQueue(frontier_size)
    frontier.put((0, root_node))
    current_depth = 0

    # The current best node. As searching proceeds, if a new node comes up with a better Expected Utility
    # this variable will be set to that node
    best = (0, root_node)

    # For inspection, keep track of the total number of successors generated over the course of the entire search
    successor_count = 0
    while not frontier.empty():
        now = time()
        seconds_elapsed = now - start_time
        minutes_elapsed = seconds_elapsed / 60
        if seconds_elapsed > 1 and minutes_elapsed >= timeout:
            break

        try:
            item = frontier.get()
        except:
            print("Tried to get item from queue, but failed. Ignoreing")
            continue

        # I had to put in the negative number into the queue because of how the queue works
        # This gets back the original value
        score = -item[0]
        node = item[1]

        if get_depth(node) >= max_depth:
            break

        # continually update the best if a new better score comes along
        if score > best[0]:
            best = (score, node)
            print(f"new best score found {score} depth: {current_depth} successor count: {successor_count}")
            schedule = Schedule(node)
            on_new_schedule_found(schedule)

        successors = generate_successors(node)
        successor_count += len(successors)
        for child in successors:
            if child is None:
                continue
            score = expected_utility(child)

            # Python PriorityQueue sorts best as lowest
            # By inverting the score, the best scores will be popped off first
            try:
                frontier.put((-score, child), False)
                node.add_child(child)

                # update the current depth if needed
                current_depth = max(current_depth, get_depth(child))
            except:
                # If the queue is full, ignore the child and move on
                pass

    print(f"finished best score found {best[0]} depth: {current_depth} successor count: {successor_count}")
    schedule = Schedule(best[1])

    now = time()
    seconds_elapsed = now - start_time

    return SearchResult(best[0], best[1], current_depth, seconds_elapsed, successor_count, frontier_size, timeout)


def run_simulation(test_number, timeout, frontier_size, search_type):
    """
    Run a simulation until all nodes are discovered or until the timeout has been reached
    Arguments:
        test_number: which input dataset to use
        timout: time in minutes
        frontier_size: the size of the frontier for the search being performed
        search_type: best_first or breadth_first
    """

    test_name = f"{search_type}-frontiersize-{frontier_size}-dataset-{test_number}-timeout-{timeout}"

    # clear out results for this test run
    reset_results(test_name)

    # import necessary data for the test run
    countries = import_countries(test_number)
    global resource_info
    resource_info = import_resource_info(test_number)

    # Create the world and commence the search!
    world = World(countries)
    root = Node(None, world, None)
    result = best_first_search(root, 100, timeout, frontier_size, lambda schedule: update_results(test_name, schedule))
    result.search_type = search_type
    result.data_set = test_number
    finish_results(test_name, result)
    return result
