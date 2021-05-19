from random import randint, choice
import uuid
from typing import List, Dict, Tuple
from itertools import combinations


class Trip:
    """
    A basic class to represent a trip object
    """
    # __MIN, __MAX and __STEP are used in random generation function(for start, end nd duration generation)
    __MIN = 0
    __MAX = 1000
    __STEP = 1000
    __PRIORITIES = (1, 2, 3)

    def __init__(self, start: int, end: int, priority: int, trip_id: int):
        """
        Create Trip object
        :param start:
        :param end:
        :param priority: priority of the trip
        :param trip_id: id of the trip
        """
        if priority not in self.__PRIORITIES:
            raise ValueError("%s is not a valid priority" % priority)

        self.start: int = start
        self.end: int = end
        self.priority: int = priority
        self.trip_id: int = trip_id

    def __str__(self):
        return "start=%s, end=%s, priority=%s, id=%s" % (self.start, self.end, self.priority, self.trip_id)

    def to_list(self) -> List:
        """
        Return a list representation of a trip
        :return:
        """
        return [self.start, self.end, self.priority, self.trip_id]

    @classmethod
    def from_list(cls, trip_list: List) -> "Trip":
        """
        Create a Trip object from it's list representation
        :param trip_list: list with start, end, priority and trip_id
        :return: Trip object
        """
        start, end, priority, trip_id = trip_list
        return cls(start=start, end=end, priority=priority, trip_id=trip_id)

    @classmethod
    def generate_random(cls, use_fixed_priority=True, trip_id=None) -> "Trip":
        """
        Helper function to generate a random trip.
        :param use_fixed_priority: indicates if the generated trips should have the same priority over and over again
        :param trip_id: id of the trip, if none, random UUID integer is used
        :return: Trip object with random properties
        """
        start = randint(cls.__MIN, cls.__MAX)
        end_max = min(cls.__MAX, start + cls.__STEP)
        end = randint(start + 1, end_max)

        if use_fixed_priority:
            priority = cls.__PRIORITIES[0]
        else:
            priority = choice(cls.__PRIORITIES)

        if trip_id is None:
            trip_id = uuid.uuid4().int

        return cls(start=start, end=end, priority=priority, trip_id=trip_id)

    def is_colliding(self, other: "Trip") -> bool:
        """
        Detect if the current and other trips collide or not
        :param other: an instance of Trip which should be compared to self
        :return: True if they collide, False otherwise
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Cant compare Trip with other types")

        if self.start <= other.start <= self.end:
            return True
        elif self.start <= other.end <= self.end:
            return True
        return False


def get_n_random_trips(n: int = 20, use_fixed_priority=False) -> List[Trip]:
    trips = [Trip.generate_random(trip_id=i, use_fixed_priority=use_fixed_priority) for i in range(n)]
    trips.sort(key=lambda x: (x.start, x.end))
    return trips


def calculate_collisions(trips: List[Trip]) -> Dict[Trip, List[Trip]]:
    """
    Calculate the adjacency list of the collisions of given trips
    :param trips: list of the trips to find collisions
    :return:
    """
    collision_elements = {}
    for trip_pair in combinations(iter(trips), r=2):
        trip_1, trip_2 = trip_pair
        if trip_1 not in collision_elements:
            collision_elements[trip_1] = []

        if trip_2 not in collision_elements:
            collision_elements[trip_2] = []

        if trip_1.is_colliding(trip_2):
            collision_elements[trip_1].append(trip_2)
            collision_elements[trip_2].append(trip_1)

    return collision_elements


def start_from_the_beginning_and_remove_collisions(trips: List[Trip]):
    """
    Start from the first trip and remove all colliding one by one until no collisions are present
    :param trips: list of trips to filter
    :return: list of non colliding trips
    """
    assigned = []
    while trips:
        trip = trips.pop(0)
        if len(assigned) == 0:
            assigned.append(trip)
        elif not assigned[-1].is_colliding(trip):
            assigned.append(trip)
    return assigned


def remove_most_colliding_until_no_collisions(trips: List[Trip]) -> List[Trip]:
    """
    The main logic of the assignment algorithm. Calculate the adjacency list for each trips collisions, then one by one
    remove the most colliding trips while updating the adjacency list of collisions until no collisions are left
    ** It is assumed that trips have equal priority as it is not taken into account when comparing.
    This function only checks for collisions.
    :param trips: list of trips to select from
    :return: non colliding list of trips
    """
    print("Collision calculation started")
    collisions = calculate_collisions(trips)
    print("Collision calculation done")

    while True:
        max_collisions = 0
        max_collisions_trip = None
        for trip, trip_collisions in collisions.items():
            curr_collision_count = len(trip_collisions)
            if curr_collision_count >= max_collisions:
                max_collisions = curr_collision_count
                max_collisions_trip = trip
        if max_collisions == 0:
            break

        for trip in collisions[max_collisions_trip]:
            collisions[trip].remove(max_collisions_trip)
        collisions.pop(max_collisions_trip)
    no_collision_trips = list(collisions.keys())
    return no_collision_trips


def find_highest_priority_trips(trips: List[Trip]) -> Tuple[int, List[Trip]]:
    """
    Find and return the highest priority trips from the given trips
    :param trips: list of Trip objects to select from
    :return: list of highest priority trips
    """
    highest_priority = float("-inf")
    highest_priority_trips = []

    for trip in trips:
        if trip.priority > highest_priority:
            highest_priority_trips = []
            highest_priority = trip.priority

        if trip.priority == highest_priority:
            highest_priority_trips.append(trip)

    return highest_priority, highest_priority_trips


def remove_collisions(constant_trips: List[Trip], to_filter: List[Trip]) -> None:
    """
    Remove all trips from to_filter if it collides with anything from constant
    :param constant_trips: list of trips that is the baseline
    :param to_filter: list of trips to filter if they collide with constant
    :return: None
    """
    i = 0
    while i < len(to_filter):
        trip = to_filter[i]
        for constant_trip in constant_trips:
            if trip.is_colliding(constant_trip):
                to_filter.remove(trip)
                break
        else:
            i += 1


def remove_given_priority(trips: List[Trip], priority: int) -> List[Trip]:
    """
    Remove all trips which have the given priority from the trips
    :param trips: list of the trips to remove from
    :param priority: priority which should be removed
    :return: the same trips list but all trips with given priority are removed
    """
    i = 0
    while i < len(trips):
        trip = trips[i]
        if trip.priority == priority:
            trips.remove(trip)
        else:
            i += 1
    return trips


def assign_trips(trips: List[Trip], use_most_colliding_algorithm=True) -> List[Trip]:
    """
    Starting from highest priority, select non colliding trips.
    The initial order of the trips is not preserved when returning
    :param trips: list of Trips from which to select
    :param use_most_colliding_algorithm: if true, use remove most colliding algorithm,
           otherwise, start from first algorithm
    :return: list of assigned trips
    """
    assigned = []
    while trips:
        highest_priority, highest_priority_trips = find_highest_priority_trips(trips)
        remove_given_priority(trips=trips, priority=highest_priority)
        remove_collisions(constant_trips=assigned, to_filter=highest_priority_trips)

        if use_most_colliding_algorithm:
            currently_assigned_trips = remove_most_colliding_until_no_collisions(trips=highest_priority_trips)
        else:
            currently_assigned_trips = start_from_the_beginning_and_remove_collisions(trips=highest_priority_trips)
        assigned.extend(currently_assigned_trips)
    assigned.sort(key=lambda x: (x.start, x.end))
    return assigned


def measure_total_wait_time_between_trips(trips: List[Trip]) -> Tuple[int, int]:
    """
    Given a list of non colliding trips sorted by their (start, end) times, calculate what is the wait time between
    trips.
    :param trips: list of non colliding trips
    :return: sum of all wait times in between
    """
    if len(trips) < 1:
        return 0, 0
    wait_time = 0
    total_duration = trips[-1].end - trips[0].start
    for trip1, trip2 in zip(trips, trips[1::]):
        wait_time += trip2.start - trip1.end

    return wait_time, total_duration
