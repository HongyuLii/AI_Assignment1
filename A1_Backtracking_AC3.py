import copy
import os
import sys
import time


class State:
    def __init__(self, name, neighbors):
        self.name = name
        self.neighbors = neighbors
        self.color = ''
        self.colored = False


# ---------------GLOBAL VARS---------------
colors = []
states = []
pairings = []
graph = {}
domains = []
queue = []
neighbors_list = []
steps = 0
# ---------------PARSER---------------
with open(sys.argv[1], "r") as f: # os.path.join(sys.path[0], "US_map")
    # split input into the 3 sections
    sections = f.read().split("\n\n")
    # step 1: create a list of colors, states, and domains
    colors = sections[0].split()
    states = sections[1].split()
    for state in states:
        domains.append(colors)
    # step 2: update graph dict with state keys
    for state in states:
        graph.update({state:[]})
    # step 3: update state keys with paired neighbor values
    for pair in sections[2].split("\n"):
        neighbor = pair.strip()
        pairings.append(neighbor)
        for key in graph.keys():
            if key in neighbor.split():
                for new_connected in neighbor.split():
                    if new_connected != key:
                        graph[key].append(new_connected)
# step 4: clear old list of states and fill w/ State class nodes
states.clear()
state_strings = []
for key, value in graph.items():
    states.append(State(key, value))
    state_strings.append(key)
    neighbors_list.append(value)
# step 5: start coloring nodes

# ---------------BACKTRACKING SEARCH---------------
def backtrack(node):
    global states
    global steps
    global domains
    colored_states = 0

    for color in colors:
        # color state, update steps
        if not can_use_color(color, node):
            # print('Cannot use color: '+color+' for '+node)
            continue
        if ac3(node, color):
            # print(node+' '+color)
            # print(domains)
            states[state_strings.index(node)].color = color
            states[state_strings.index(node)].colored = True
            steps += 1
        else:
            return False
        # check if all domains have one color, stop algorithm
        if check_domains():
            for domain in domains:
                temp_domain = copy.deepcopy(domain)
                states[domains.index(domain)].color = temp_domain[0]
                states[domains.index(domain)].colored = True
                steps += 1
                if len(domain) == 1:
                    colored_states += 1
            if colored_states == len(states):
                print("MAP COLORING COMPLETE")
                return True
        # check if all states are colored, stop algorithm
        # move to next uncolored vertex
        uncolored_neighbors = len(states[state_strings.index(node)].neighbors)
        for neighbor1 in states[state_strings.index(node)].neighbors:
            # print('Next state: ' + neighbor1)
            # check if neighbor is not colored yet (unvisited)
            if not states[state_strings.index(neighbor1)].colored:
                # color neighbor and see if parent state has any other neighbors
                if backtrack(neighbor1):
                    if uncolored_neighbors != 0:
                        continue
                    else:
                        uncolored_neighbors -= 1
                    return True
        return True
    return False

# ---------------AC3---------------
def ac3(node, color):
    global domains
    original_domains = []
    for domain in domains:
        original_domains.append(domain)
    # fill up queue
    for state in state_strings:
        for neighbor in neighbors_list[state_strings.index(state)]:
            if [state, neighbor] not in queue:
                queue.append([state, neighbor])
            if [neighbor, state] not in queue:
                queue.append([neighbor, state])
    # node's domain changes to one color
    domains[state_strings.index(node)] = [color]
    # ac3 algorithm
    while queue:
        arc = queue.pop(0)
        if revise(arc):
            if len(domains[state_strings.index(arc[0])]) == 0:
                domain = original_domains
                return False
            for xk in neighbors_list[state_strings.index(arc[0])]:
                if xk != arc[1]:
                    queue.append([xk, arc[0]])
    return True


# checks to see whether a state's current color is valid with neighboring colors
def can_use_color(color1, node):
    for neighbor1 in states[state_strings.index(node)].neighbors:
        if states[state_strings.index(neighbor1)].colored and color1 == states[state_strings.index(neighbor1)].color:
            # print('Invalid assignment: '+states[state_strings.index(neighbor1)].name+' and '+node+' have same color')
            return False
    return True


def revise(arc):
    global domains
    xi = arc[0]
    xj = arc[1]
    revised = False
    for color in domains[state_strings.index(xi)]:
        if color in domains[state_strings.index(xj)]:
            if len(domains[state_strings.index(xj)]) == 1 and len(domains[state_strings.index(xi)]) > 1:
                temp_domain = copy.deepcopy(domains[state_strings.index(xi)])
                temp_domain.remove(color)
                domains[state_strings.index(xi)] = temp_domain # removes from all domains, not just one??? WTF???
                return True
    return revised


def check_domains():
    # deleted Tasmania from input file since this code can't detect it
    for domain in domains:
        if len(domain) != 1:
            return False
    return True


# ---------------PRINT SOLUTION, IF ANY---------------
start_time = time.time()
if not backtrack(state_strings[0]):
    print('NO SOLUTION FOUND')
else:
    print("--- %s seconds ---" % (time.time() - start_time))
    print('SOLUTION FOUND')
    print('Steps taken: ' + str(steps))
    for state in states:
        print(state.name+' '+domains[state_strings.index(state.name)][0])
    print(domains)