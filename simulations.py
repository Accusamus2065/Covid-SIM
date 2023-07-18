"""CSC111 Winter 2023 Course Project: Simulation

Instructions
===============================

This Python module contains the functions for reading csv files,
recording data to create csv files, and editing each state's attribute
by user. Specifically, we read csv files to initialize InfectedZones, State and Person classes,
and we record how each state infect each other in a csv file with state's location
this is useful for visual presentation, namely represent the connection between vertices in a graph,
Finally, users may use get_user_input() function to change attributes in a state for experiment.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of instructors and TAs of
CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. :)

This file is Copyright (c) 2023 Marshal Guo, Yibin Cui, Zherui Zhang.
"""
from __future__ import annotations

import csv
from typing import Optional

from graph import InfectedZones, State
from sir_model import Person, Susceptible

RATE_OF_REMOVAL = 0.4               # Rate of removing people from the infective group to removed
RATE_OF_CONTACT = 0.0005           # Rate of removing people from the susceptible group to the infective


def populate_states(csv_file: str) -> tuple[dict[str, State], list[str]]:
    """Initialize State objects and populate States with Person objects.
    Return a tuple with the first element being the dictionary with state_names to State objects,
    and the second element being the list of state_names that comes in handy to randomly select
    states.

    Preconditions:
        - csv_file is a valid path to the file
    """
    states = {}
    keys = []
    with open(csv_file) as file:
        reader = csv.reader(file)
        next(reader)
        person_id = 0
        for line in reader:
            lst = []
            for i in range(person_id, person_id + int(line[3])):
                lst.append(Person(i))
            person_id += int(line[3])
            keys.append(line[0])
            states[line[0]] = State(name=line[0],
                                    sus=Susceptible(lst),
                                    a=RATE_OF_REMOVAL,
                                    r=RATE_OF_CONTACT,
                                    location=(float(line[1]), float(line[2])))
    return (states, keys)


def graph_to_csv(infected_zones: InfectedZones) -> str:
    """Create a new csv file, from the given InfectedZones, each row represent a pair of connected states,
    with their location and state names. Then save the csv file under project file.
    Return the path of the dataset.
    Preconditions:
        - infected_zones is a valid object
    """
    # field names
    fields = ['start_lat', 'start_lon', 'end_lat', 'end_lon', 'state1', 'state2']

    # data rows of csv file
    state1_state2 = infected_zones.get_state_connections()
    infected_states = infected_zones.get_infected_states()
    rows = []
    for row in state1_state2:
        state_name1, state_name2 = list(row)[0], list(row)[1]
        start_lat, start_lon = infected_states[state_name1].location
        end_lat, end_lon = infected_states[state_name2].location
        state1 = state_name1
        state2 = state_name2
        rows.append([start_lat, start_lon, end_lat, end_lon, state1, state2])

    # name of csv file
    filename = "edges.csv"

    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(fields)

        # writing the data rows
        csvwriter.writerows(rows)
    return filename


def get_user_input(keys) -> Optional[dict[str, list]]:
    """Takes in a list of keys and prompts the user to enter values for each key.

    Args:
        keys: A list of strings representing the keys for the input dictionary.

    Returns:
        A dictionary where the keys are strings and the values are lists containing the isolation index,
        maskwearing index, vaccination index, and lockdown status (True/False).

    Preconditions:
        - Each key in the 'keys' list is a unique string.
        - The user enters a float between 1.0 and 10.0 (inclusive) for the isolation index, vaccination index,
          and maskwearing index.
        - The user enters 'Y' or 'N' for editing states' attributes
        - The user enters 'T' or 'F' for the lockdown status.
    """
    print(f"Do you want to edit states' attributes? (Y/N). You should enter 'Y' or 'N' (◍•ᴗ•◍)")
    edit_or_nah = input()
    # if input() != 'Y' then editing states' statements wouldn't be triggered
    # when there comes to be several / many states in a csv file, we recommend you input 'N'
    if edit_or_nah == 'Y':
        print('For each of the following states, you may adjust the parameters\
              \n PLEASE FOLLOW THE INPUT GUIDE STRICTLY :)')
        input_dict = {}
        for i in range(len(keys)):
            print(f'{keys[i]}')
            print(f'\t Isolation Index: (Float from 1.0 ~ 10.0 Inclusive)')
            isolation_index = float(input())
            print(f'\t Vaccination Index:(Float from 1.0 ~ 10.0 Inclusive)')
            vaccination_index = float(input())
            print(f'\t Maskwearing Index: (Float from 1.0 ~ 10.0 Inclusive)')
            maskwearing_index = float(input())
            print(f'\t Lockdown?: (T/F)')
            # if input() != 'T' then lockdown is set to False
            lockdown = input() == 'T'
            input_dict[keys[i]] = [isolation_index, maskwearing_index, vaccination_index, lockdown]
        return input_dict
    else:
        return None


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['random'],
        'disable': ['W0622', 'E9999', 'R0902', 'R0913', 'E9998', 'R0914']
    })
