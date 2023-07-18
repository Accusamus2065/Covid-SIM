"""CSC111 Winter 2023 Course Project: SIR Model

Instructions
===============================

This Python module contains the implementation of SIR Model classes,
which are Person, Susceptible, Infective, and Removal.
The SIR model is a mathematical model used to understand the spread of infectious diseases in a population.
With these classes, we are able to simulate the COVID-19 infection and recovery process.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of instructors and TAs of
CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. :)

This file is Copyright (c) 2023 Marshal Guo, Yibin Cui, Zherui Zhang.
"""
from __future__ import annotations
from typing import Optional
import random


class Person:
    """Person class that represents a person in the population

    Instance Attributes
    - id:
        A identifier that's unique for every person.
        We use id to match each person.
    - infected_time:
        Tracking the infected_time of a person.
        Note: a person is possible to be recovered only if its infected_time is greater than 14 (days).

    Representation Invariants:
    - self.id is unique to each Person
    - 0 <= self.infected_time if self.infected_time is not None
    """
    id: int
    infected_time: Optional[int]

    def __init__(self, identifier: int) -> None:
        """Initialize this person with the given id.

        Preconditions:
            - isinstance(n, int)
        """
        self.id = identifier
        self.infected_time = None

    def __repr__(self) -> str:
        """Return a string representing this person."""
        return f'id={self.id}, infected_time={self.infected_time}'

    def get_infected(self) -> None:
        """Set the person's infected_time to 0 once the person is infected.

        Preconditions:
            - self.infected_time is None

        >>> person = Person(39)
        >>> person.get_infected()
        >>> person.infected_time
        0
        """
        self.infected_time = 0

    def add_infected_day(self) -> None:
        """Add the person's infected_time by 1.

        Preconditions:
            - self.infected_time is not None

        >>> person = Person(39)
        >>> person.get_infected()
        >>> person.add_infected_day()
        >>> person.infected_time
        1
        """
        self.infected_time += 1


class Susceptible:
    """
    Instance Attributes
    - people:
        A mapping containing all susceptible people.

    Representation Invariants:
    - all({self.people[person].id == person for person in self.people})
    """
    people: dict[int, Person]

    def __init__(self, people: list[Person]) -> None:
        """Initialize this Susceptible class with the given list of Person.

        Preconditions:
            - all([isinstance(p, Person) for p in people])
            - all([p.id not in self.people for p in people])
        """
        mapping = {}
        for p in people:
            mapping[p.id] = p

        self.people = mapping

    def add(self, person: Person) -> None:
        """Add a new Susceptible person.

        Preconditions:
            - person.id not in self.people
            - isinstance(person, Person)

        >>> p1 = Person(1)
        >>> s = Susceptible([p1])
        >>> p2 = Person(2)
        >>> s.add(p2)
        >>> len(s.people)
        2
        """
        self.people[person.id] = person

    def remove(self, person: Person) -> None:
        """Remove a person that is not susceptible anymore.

        Preconditions:
            - person.id in self.people
            - isinstance(person, Person)

        >>> p1 = Person(1)
        >>> s = Susceptible([p1])
        >>> s.remove(p1)
        >>> s.people
        {}
        """
        self.people.pop(person.id)

    def remove_by_number(self, n: int) -> list[Person]:
        """Remove n number of people that are not infected anymore.

        Preconditions:
            - isinstance(n, int)
            - n >= 0
            - len(self.people) >= 0

        >>> example = [Person(1), Person(2), Person(3), Person(4)]
        >>> s = Susceptible(example)
        >>> len(s.remove_by_number(2))
        2
        >>> len(s.remove_by_number(10))
        2
        """
        if len(self.people) == 0:
            return []
        # if n > len(self.people), then remove all the person in self.people
        elif n > len(self.people):
            lst = list(self.people.values())
            self.people = {}
            return lst
        else:
            lst_so_far = []
            for _ in range(n):
                ids = [self.people[p].id for p in self.people]
                id_to_remove = random.choice(ids)
                new_p = self.people.pop(id_to_remove)
                lst_so_far.append(new_p)

            return lst_so_far


class Infective:
    """
    Instance Attributes
    - people:
        A mapping containing all infected people.

    Representation Invariants:
    - all({self.people[person].id == person for person in self.people})
    """
    people: dict[int, Person] = {}

    def __init__(self, people: list[Person]) -> None:
        """Initialize this Infectie class with the given list of Person.

        Preconditions:
            - all([isinstance(p, Person) for p in people])
            - all([p.id not in self.people for p in people])
        """
        for person in people:
            self.add(person)

    def add(self, person: Person) -> None:
        """Add a new infected person.
        Note: using non-mutating method is required for not causing error.

        Preconditions:
            - isinstance(person, Person)
            - person.id not in self.people

        >>> p = Person(1)
        >>> infective = Infective([])
        >>> infective.add(p)
        >>> len(infective.people)
        1
        """
        self.people = {**self.people, person.id: person}
        self.people[person.id].get_infected()

    def add_multiple(self, people: list[Person]) -> None:
        """
        Add multiple new infected people.

        Preconditions:
            - all([isinstance(p, Person) for p in people])
            - all([p.id not in self.people for p in people])

        >>> person1 = Person(1)
        >>> person2 = Person(2)
        >>> infective = Infective([])
        >>> infective.add_multiple([person1, person2])
        >>> len(infective.people)
        2
        """
        for p in people:
            self.add(p)

    def remove(self, person: Person) -> None:
        """Remove a person that is not infective anymore.

        Preconditions:
            - isinstance(person, Person)
            - person.id in self.people

        >>> p = Person(1)
        >>> infective = Infective([p])
        >>> infective.remove(p)
        >>> len(infective.people)
        0
        """
        person.infected_time = None
        self.people.pop(person.id)

    def remove_by_number(self, n: int) -> list[Person]:
        """Remove n number of people that are not infected anymore.

        Preconditions:
            - isinstance(n, int)
            - n >= 0
            - len(self.people) >= 0

        >>> person1 = Person(1)
        >>> person2 = Person(2)
        >>> person1.infected_time = 15
        >>> person2.infected_time = 16
        >>> infective = Infective([person1, person2])
        >>> len(infective.remove_by_number(1))
        0
        """
        if len(self.people) == 0 or n == 0:
            return []
        lst_so_far = []
        for _ in range(n):
            # a infected person is possible to recover only if its infected_time > 14
            ids = [self.people[p].id for p in self.people if self.people[p].infected_time > 14]
            if len(ids) == 0:
                return []
            elif len(ids) != 1:
                id_to_remove = random.choice(ids)
            else:
                id_to_remove = ids[0]

            new_p = self.people.pop(id_to_remove)
            new_p.infected_time = None
            lst_so_far.append(new_p)

        return lst_so_far

    def increment_day(self) -> None:
        """Add the person's infected_time by 1.

        Preconditions:
            - all([isinstance(p, Person) for p in self.people.values()])

    >>> p1 = Person(1)
    >>> p2 = Person(2)
    >>> i = Infective([p1, p2])
    >>> i.increment_day()
    >>> i.people[1].infected_time
    1
    >>> i.people[2].infected_time
    1
        """
        for p in self.people.values():
            p.add_infected_day()

    def get_recoverable(self) -> list[Person]:
        """Return all the recoverable people in a list.

        Preconditions:
            - all([isinstance(p, Person) for p in self.people.values()])

        >>> p1 = Person(1)
        >>> p2 = Person(2)
        >>> p3 = Person(3)
        >>> i = Infective([p1, p2, p3])
        >>> len(i.get_recoverable())
        0
        """
        return [p for p in self.people.values() if p.infected_time > 14]


class Removal:
    """
    Instance Attributes
    - people:
        A mapping containing all recovered or dead people.

    Representation Invariants:
    - all({self.people[person].id == person for person in self.people})
    """
    people: dict[int, Person]

    def __init__(self, people: list[Person]) -> None:
        """Initialize this Removal object with the given list of people.

        Preconditions:
            - all(isinstance(person, Person) for person in people)

        >>> p1 = Person(1)
        >>> p2 = Person(2)
        >>> r = Removal([p1, p2])
        >>> r.people[1] == p1
        True
        >>> r.people[2] == p2
        True
        """
        mapping = {}
        for p in people:
            mapping[p.id] = p

        self.people = mapping

    def add(self, person: Person) -> None:
        """Add the given people in Removal.

        Preconditions:
            - all(isinstance(person, Person) for person in people)
            - all([person.id not in self.people for person in people])

        >>> r = Removal([])
        >>> p = Person(1)
        >>> r.add(p)
        >>> r.people[1] == p
        True
        """
        self.people[person.id] = person

    def add_multiple(self, people: list[Person]) -> None:
        """Add the given people in Removal.

        Preconditions:
            - all(isinstance(person, Person) for person in people)
            - all([person.id not in self.people for person in people])

        >>> r = Removal([])
        >>> p1, p2 = Person(1), Person(2)
        >>> r.add_multiple([p1, p2])
        >>> r.people[1] == p1 and r.people[2] == p2
        True
        """
        for p in people:
            self.add(p)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['random'],
        'disable': ['W0622']
    })
