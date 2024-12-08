#!/usr/bin/env python3

# Sophie Lama           8 December 2024
# Theory of Computing   Project 02

import sys

total_transitions = 0   # track how many transitions are taking place (throughout all the branches)
stat_list = []          # list holding exit statuses of branches and their depths

class Machine:
    # each Turing Machine has a name, a start state, accept state, reject state, and list of transitions
    def __init__(self, name, start, acc, rej, transitions):
        self.name = name
        self.start = start
        self.acc = acc
        self.rej = rej
        self.transitions = transitions

# Functions

def read_tm_file(file):
    tm = [ line.strip() for line in file.readlines() ] # remove newline character from each line in file

    machine_name = tm[0]
    start = tm[4]
    acc = tm[5]
    rej = tm[6]
    transitions = [ t.split(",") for t in tm[7:] ] # create list of elements in each transition
    return Machine(machine_name, start, acc, rej, transitions)


def make_transition(transition: list, string: list, curr_state: str, head_index: int, configs: list, depth: int):
    configuration = ["".join(string[:head_index]), transition[2], "".join(string[head_index:])]
    
    configs.append(configuration)
    
    string[head_index] = transition[3]  # edit char at head
    curr_state = transition[2]          # edit current state to new/next one
    if transition[4] == 'R': head_index += 1        # move head pointer either to the right or left
    elif transition[4] == 'L':   head_index -= 1
    global total_transitions
    total_transitions += 1       # update the total number of transitions simulated

    return string, curr_state, head_index, configs


def iterate(tm: Machine, curr_state: str, string: list, head_index: int, depth: int, limit: int, configs: list):
    if depth >= limit: # break out if max depth/step limit has been reached
        return tm.rej, depth, configs # no transition simulated here, so don't update transition counter

    t_matches = []
    for t in tm.transitions:
        if t[0] == curr_state and t[1] == string[head_index]:
            t_matches.append(t)

    if len(t_matches) == 0:
        configs.pop() # pop this configuration from the list if we've hit a dead end (aka this is not the right path)
        global total_transitions
        total_transitions += 1  # add one to the counter, transitioning into a reject state
        return tm.rej, depth, configs    # reject string if no transition found for this state, char combo
    
    depth += 1
    for match in t_matches:     # first search through the list of matches to see if any lead to an accept state
        if match[2] == tm.acc:
            total_transitions += 1  # add one to the counter, transitioning into an accept state
            _, _, _, a_configs = make_transition(match, string, curr_state, head_index, configs, depth)
            return tm.acc, depth, a_configs
    
    for match in t_matches:
        m_str, m_curr, m_head_index, m_configs = make_transition(match, string, curr_state, head_index, configs, depth)
        status = iterate(tm, m_curr, m_str, m_head_index, depth, limit, m_configs)
        if status[0] == tm.acc: return status # return if the path eventually leads to acceptance

        global stat_list
        if status not in stat_list:
            stat_list.append(status)

    max_depth = 0
    for stat in stat_list: # search through all the exit statuses
        if stat[1] > max_depth: # find the one with the max depth
            max_depth = stat[1]

    return tm.rej, max_depth, configs


def gather_starting_input(stream):
    print("Enter the name of the file describing the machine: (format: check_(name here)_slama.csv)")
    file_name = stream.readline().strip()
    tm_file = open(file_name)

    print("Enter the input string to run:")
    string = list(stream.readline().strip())
    if string[-1] != "_": # if user's string doesn't end with __, add it in for them
        string.append("_")
        string.append("_")

    print("Enter the limit (max depth of the configuration tree):")
    limit = int(stream.readline().strip())

    return tm_file, string, limit


# Main Execution

def main(stream = sys.stdin):
    depth = 0
    head_index = 0
    configs = []

    tm_file, string, limit = gather_starting_input(stream)
    tm = read_tm_file(tm_file)
    
    print(f'\nMachine: {tm.name}')
    print(f'Initial string: {"".join(string)}')
    state, depth, configs = iterate(tm, tm.start, string, head_index, depth, limit, configs)
    print(f'Depth of the tree of configurations: {depth}')
    print(f'Total number of transitions simulated: {total_transitions}')
    
    if state == tm.acc:
        print(f'String accepted in {depth} steps') # print the number of transitions from the start to the accept
        print(f'Configurations:')
        [ print(c) for c in configs ] # print out each configuration
    elif depth >= limit: # else if step limit was exceeded
        print(f'Execution stopped after {depth} steps')
    else:
        print(f'String rejected in {depth} steps') # print the number of steps from the start to the last reject
    
    return


if __name__ == '__main__':
    main()