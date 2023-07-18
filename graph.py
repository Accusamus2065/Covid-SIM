"""CSC111 Winter 2023 Course Project: Graph

Instructions
===============================

This Python module contains the implementation of Graph (InfectedZones) and Vertex (State),
Using InfectedZones and State classes we can simulate how each state is affected by the
outbreak internally, and how each state is contagious to each other,
this file contains the most important functions and classes in our outbreak simulation.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of instructors and TAs of
CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. :)

This file is Copyright (c) 2023 Marshal Guo, Yibin Cui, Zherui Zhang.
"""
from __future__ import annotations
import random
import math
from typing import Optional

from sir_model import Person, Susceptible, Infective, Removal

# Assume that if the amount of infective people reaches this value,
# then this state has the capacity to infect another states.
# you may edit this value freely
TRANSMIT_THRESHOLD = 50


class InfectedZones:
    """A graph representing the infected zones in the US.

    Representation Invariants:
    - all(item == self._all_states[item].name for item in self._all_states)
    - set(self._all_states.keys()) == set(self._state_names)
    - set(self._infected_states.keys()) <= set(self._all_states.keys())

    Private Instance Attributes:
        - _infected_states: A dictionary mapping each infected state's name to its corresponding State object.
        - _all_states: A dictionary mapping each state's name to its corresponding State object.
        - _state_names: A list of all state names.
    """
    _infected_states: dict[str, State]  # {state name: State object}
    _all_states: dict[str, State]
    _state_names: list[str]

    def __init__(self, all_states: dict[str, State], state_names: list[str]) -> None:
        """Initialize the graph with the dictionary mapping every selected state's name to State,
        and a list of their name.

        Preconditions:
            - set(all_states.keys()) == set(state_names)
            - all(isinstance(s, State) for s in all_states.values())
        """
        self._infected_states = {}
        self._all_states = all_states
        self._state_names = state_names

    def get_infected_states(self) -> dict[str, State]:
        """Return a dictionary mapping each infected state's name to State.

        >>> s1 = State("state1", Susceptible([Person(1)]), 0.05, 0.3, (100, 100))
        >>> s2 = State("state2", Susceptible([Person(2)]), 0.02, 0.5, (200, 200))
        >>> all_states = {"state1": s1, "state2": s2}
        >>> state_names = ["state1", "state2"]
        >>> iz = InfectedZones(all_states, state_names)
        >>> iz.get_infected_states()
        {}
        """
        return self._infected_states

    def add_state(self, state: State) -> None:
        """Add a new infected state with the given information to the infected zones.
        After a state is infected, the state begins its infection process.

        Preconditions:
            - isinstance(state, State)
            - state.name not in self._infected_states
        """
        self._infected_states[state.name] = state
        patient_zero = state.get_patient_zero()
        if patient_zero is None:
            return None
        else:
            return state.infection_process(self, self._all_states, self._state_names, set())

    def add_edge(self, state1_name: str, state2_name: str) -> None:
        """Add an edge between the two states with the given name in InfectedZones.

        Raise a ValueError if state1_name or state2_name is not an infected state in the InfectedZones.

        Preconditions:
            - state1_name != state2_name
            - state1_name in self._all_states
            - state2_name in self._all_states
        """
        if state1_name in self._infected_states and state2_name in self._infected_states:
            v1 = self._infected_states[state1_name]
            v2 = self._infected_states[state2_name]
            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def change_a_and_r(self, state_name: str, isolation_degree: float, maskwearing_degree: float,
                       vaccination_degree: float) -> None:
        """Change the values of rate_of_removal (a) and rate_of_contact (r) by changing the selected state's
        policy, namely isolation, maskwearing or vaccination.

        Preconditions:
                - state_name in self._all_states
                - 1.0 <= isolation_degree <= 10.0
                - 1.0 <= maskwearing_degree <= 10.0
                - 1.0 <= vaccination_degree <= 10.0
        """
        target = self._all_states[state_name]
        target.isolation = isolation_degree
        target.maskwearing = maskwearing_degree
        target.vaccination = vaccination_degree
        score = isolation_degree + maskwearing_degree
        # change r
        target.r -= score * 0.000002
        if target.r <= 0.0:
            # target.r should be very small float
            target.r = 0.000000001
        elif target.r >= 1.0:
            target.r = 1.0
        # change a
        target.a += vaccination_degree * 0.25
        if target.a <= 0.1:
            target.a = 0.1
        elif target.a >= 1.0:
            target.a = 1.0

    def movement_prohibited(self, state_name: str) -> None:
        """Change the state's lockdown policy to True.

        Preconditions:
            - state_name in self._all_states

        >>> s1 = State("state1", Susceptible([Person(1)]), 0.05, 0.3, (100, 100))
        >>> s2 = State("state2", Susceptible([Person(2)]), 0.02, 0.5, (200, 200))
        >>> all_states = {"state1": s1, "state2": s2}
        >>> state_names = ["state1", "state2"]
        >>> iz = InfectedZones(all_states, state_names)
        >>> iz._all_states["state1"].lockdown
        False
        >>> iz.movement_prohibited("state1")
        >>> iz._all_states["state1"].lockdown
        True
        """
        target = self._all_states[state_name]
        target.lockdown = True

    def get_state_connections(self) -> list[set[str, str]]:
        """Return a list of all connected states, each pair is represented by a set containing the two
        connected states' name.
        """
        lst = []
        for state_name in self._infected_states:
            for other_state_object in self._infected_states[state_name].neighbours:
                new_pair = {state_name, other_state_object.name}
                if new_pair not in lst:
                    lst.append(new_pair)
        return lst


class State:
    """Local population

    Instance Attributes
    - name: the name of the state
    - sus: Susceptible objects specific for this state
    - inf: Infective objects specific for this state
    - rem: Removal objects specific for this state
    - a: rate of removal
    - r: rate of contact
    - isolation: the index of isolation for this state
    - maskwearing: the index of mask-wearing of this state
    - vaccination: the index of vaccination of this state
    - lockdown: whether this state is free for interstate travel
    - neighbours: a set of State object of all the state that is infected by this state or infect this state
    - location: a tuple for representing the state's latitude and longitude
    - during_infection: a boolean that tells if a state is currently infected


    Representation Invariants:
    - self.name is valid
    - 0.0 <= a <= 1.0
    - 0.0 <= r <= 1.0
    - 1.0 <= self.isolation <= 10.0
    - 1.0 <= self.maskwearing <= 10.0
    - 1.0 <= vaccination <= 10.0
    """
    name: str
    sus: Susceptible
    inf: Infective
    rem: Removal
    a: float  # rate recovery
    r: float  # rate of contact
    # Human input:
    # Impact on a and r
    isolation: float
    maskwearing: float
    vaccination: float
    # Impact on infecting next state
    lockdown: bool   # False for no interstate travel, True for interstate travel
    neighbours: set
    location: tuple[float, float]   # Simulation Essential
    during_infection: bool

    def __init__(self, name: str, sus: Susceptible, a: float, r: float, location: tuple[float, float]) -> None:
        """Initialize a state with the given information.

        Preconditions:
        - name is a non-empty string.
        - 0 <= a <= 1.0
        - 0 <= r <= 1.0
        """
        self.name = name
        self.sus = sus
        self.inf = Infective([])
        self.rem = Removal([])
        self.a = a
        self.r = r

        # default values for these attributes
        self.isolation = 1.0
        self.maskwearing = 1.0
        self.vaccination = 1.0
        self.lockdown = False
        self.neighbours = set()
        self.location = location
        self.during_infection = False

    def __repr__(self) -> str:
        """Return a string representing this state."""
        return f"{self.name}: S={len(self.sus.people)}, I={len(self.inf.people)}, R={len(self.rem.people)}"

    def is_at_threshold(self) -> bool:
        """Return if a state is at threshold baseline, if it is True, then disease is able to spread to other states.
        We set the threshold as 1000 as an assumption.
        """
        return len(self.inf.people) > TRANSMIT_THRESHOLD

    def infection_process(self, infected_zones: InfectedZones, dict_of_states: dict[str, State],
                          lst_of_states: list[str], visited: set) -> None:
        """Simulate the infection process and how the state infects other states.
        If the state's during_infection is True,
        the state will not be infected again until during_infection is False again.
        This function is the main part of our simulation and calls many other functions.

        Preconditions:
            - infected_zones is a valid InfectedZones object
            - dict_of_states is a dictionary where the keys are valid state names and \
                the values are valid State objects
            - lst_of_states is a list of valid state names
            - visited is a set containing the names of the states that have been visited

        Notes:
            this is a recursive function, if self is currectly infected,
            there's no need to start the recursion again,
            since we have already mutate self.neighbours to point out
            which state infected self in the following methods.
        """
        i = 0
        # If a state is infected, set state.during_infection be True.
        if self.during_infection is False:
            self.during_infection = True
        else:
            return None

        # Use visited attribute to make self cannot infect a same state again.
        visited = visited.union({self.name})

        # Loop ends if there's no infected people in a state.
        while len(self.inf.people) > 0:
            print(f"--- {self.name, len(self.sus.people), len(self.inf.people), len(self.rem.people)} ----")

            # Calculation of the number of sick and recovered people according to the SIR model.
            num_of_infected = math.ceil(self.r * len(self.inf.people) * len(self.sus.people))
            infected_people = self.sus.remove_by_number(num_of_infected)
            self.inf.add_multiple(infected_people)
            num_of_recovery = math.ceil(self.a * len(self.inf.get_recoverable()))
            removed_people = self.inf.remove_by_number(num_of_recovery)
            self.rem.add_multiple(removed_people)

            # Only when num of infected is large enough, namely > transmit_threshold it can infect another state.
            if len(self.inf.people) > TRANSMIT_THRESHOLD and self.lockdown is False:
                self.infect_next_state(infected_zones, dict_of_states, lst_of_states, visited)
            # If a state's lockdown is True, it's hard to infect another state,
            # so we decide that there is only 10 percent possibility to infect another state.
            elif len(self.inf.people) > TRANSMIT_THRESHOLD and self.lockdown is True:
                p = random.uniform(0, 1)
                if p < 0.1:
                    self.infect_next_state(infected_zones, dict_of_states, lst_of_states, visited)

            # For infected people, add their infected time by one,
            # notice that only when infected time > 14 they are possible to recover.
            self.inf.increment_day()
            i += 1

        print(f'All Removed: {self.name, len(self.sus.people), len(self.inf.people), len(self.rem.people)}')

    def get_patient_zero(self) -> Optional[Person]:
        """Return a random Person object from the Susceptible group.
        If the Susceptible group is empty, then return None.

        >>> s1 = State("state1", Susceptible([Person(1)]), 0.05, 0.3, (100, 100))
        >>> s1.get_patient_zero()
        id=1, infected_time=0
        >>> len(s1.sus.people)
        0
        >>> len(s1.inf.people)
        1
        """
        keys = list(self.sus.people)
        if not keys:
            return None
        patient_zero = self.sus.people[random.choice(keys)]
        self.inf.add(patient_zero)
        self.sus.remove(patient_zero)
        return patient_zero

    def infect_next_state(self, infected_zones: InfectedZones, dict_of_states: dict[str, State],
                          lst_of_states: list[str], visited: set[str]) -> None:
        """Choose the next state to infect using an algorithm below.

            1. Find every other state other than self.
            2. Find the state that has a minimum score according to the other state.
               If there is only one state with the minimum score, choose that state. Otherwise, continue.
            3. Find the state from the states after screening for the minimum score that is at the least
               distance. If there is only one closest, choose that one. Otherwise randomly choose one.
        """
        states = self.get_other_states(dict_of_states, lst_of_states, visited)
        if not states:
            return None

        min_score = min([self.compute_state_score(state) for state in states])
        candidates = [state for state in states if self.compute_state_score(state) == min_score]
        if len(candidates) == 1:
            next_state = candidates[0]
            infected_zones.add_state(next_state)
            infected_zones.add_edge(self.name, next_state.name)
            return None

        min_distance = min([self.get_distance(state) for state in candidates])
        finalists = [state for state in candidates if self.get_distance(state) == min_distance]

        next_state = random.choice(finalists)
        infected_zones.add_state(next_state)
        infected_zones.add_edge(self.name, next_state.name)
        return None

    def get_other_states(self, dict_of_states: dict[str, State], lst_of_states: list[str],
                         visited: set[str]) -> list[State]:
        """Return a list of states, not including the current state, this method helps to determine
        what other states can the current state infect.

        >>> s1 = State("state1", Susceptible([Person(1)]), 0.05, 0.3, (100, 100))
        >>> s2 = State("state2", Susceptible([Person(2)]), 0.02, 0.5, (200, 200))
        >>> s1.get_other_states({'state1': s1, "state2": s2}, ["state1", "state2"], {s1.name})
        [state2: S=1, I=0, R=0]
        """
        return [dict_of_states[state_name] for state_name in lst_of_states if
                state_name not in visited and len(dict_of_states[state_name].sus.people) != 0]

    def get_distance(self, other_state: State) -> float:
        """Measure the distance between two states using the location attribute initialized.

        Preconditions:
            - other_state is a valid State object
        """
        x1, y1 = other_state.location
        x2, y2 = other_state.location
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def compute_state_score(self, other_state: State) -> float:
        """Details of the algorithm can be referred from the docstring in infect_next_state()

        Preconditions:
            - other_state is a valid State object

        Notes:
            The way we prefer to infect another state is not limited to the distance between the two states;
            we also consider whether the other state is on lockdown and
            the ratio of the number of people infected to the number of people who can be infected in a state.
        """
        inf_score = len(other_state.inf.people) / len(other_state.sus.people)
        if other_state.lockdown:
            interstate_score = 50
        else:
            interstate_score = 0
        return interstate_score + self.get_distance(other_state) + inf_score


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['random'],
        'disable': ['W0622', 'E9999', 'R0902', 'R0913', 'E9998']
    })
