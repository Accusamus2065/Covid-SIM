"""CSC111 Winter 2023 Course Project: Main

Instructions
===============================

This Python module only contains the function to trigger the COVID-19 simulation,
you may change the DATASET for experiment, different DATASET files contains
different number of population, and different number of states.
Therefore, if you are running a csv file with many states, we recommend you
not editing each state's attribute by hand.
In all csv files except for states_full.csv we reduce the population in each state to increase performance.
Also, you may edit rate of contact and rate of removal in simulations.py,
and you may edit TRANSMIT_THRESHOLD in graph.py for furtuer experiment.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of instructors and TAs of
CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. :)


This file is Copyright (c) 2023 Marshal Guo, Yibin Cui, Zherui Zhang.
"""

import random
from graph import InfectedZones
from plotter import plot_diagram
from simulations import get_user_input, graph_to_csv, populate_states

# Dataset of the states the user decides test and observe (Changeable to see other datasets)
# Using DATASET = 'states_full.csv' is not recommended, it is created using actual data,
# it is very time-consuming to run.
DATASET = 'data/states_full_people_not_full.csv'


def main() -> None:
    """Main method of the program.
    Its job is to call populate_states, get user input on the variety parameters in each state to kick
    -start the simulation.
    """
    # Populate States
    states, keys = populate_states(DATASET)
    infected_zones = InfectedZones(states, keys)

    # GET INPUT AND ADJUST PARAMETERS
    input_dict = get_user_input(keys)
    if input_dict is not None:
        for key in input_dict:
            infected_zones.change_a_and_r(state_name=key,
                                          isolation_degree=input_dict[key][0],
                                          maskwearing_degree=input_dict[key][1],
                                          vaccination_degree=input_dict[key][2])
            if input_dict[key][3]:
                infected_zones.movement_prohibited(state_name=key)

    # START SIM
    # Pick one unlucky state and start internal infection
    key = random.choice(keys)
    infected_zones.add_state(states[key])

    file_path = graph_to_csv(infected_zones)
    # Plot Graph
    plot_diagram(DATASET, file_path)


if __name__ == '__main__':
    main()
