import copy

import pandas as pd

from trip_selection import get_n_random_trips, assign_trips, measure_total_wait_time_between_trips
from vehicle_availability import check_vehicle_availability


def test_pandas():
    df = check_vehicle_availability(
        start_time=pd.Timestamp(2021, 1, 10, 20, 14, 0),
        end_time=pd.Timestamp(2021, 1, 10, 20, 14, 30)
    )
    return df


def test_assignment():
    print("Generating")
    n_trips = get_n_random_trips(40, use_fixed_priority=False)
    print("Generation done")

    first = copy.deepcopy(n_trips)
    second = copy.deepcopy(n_trips)
    most_colliding = assign_trips(trips=first, use_most_colliding_algorithm=True)
    my_stats = measure_total_wait_time_between_trips(trips=most_colliding)
    from_first = assign_trips(trips=second, use_most_colliding_algorithm=False)
    their_stats = measure_total_wait_time_between_trips(trips=from_first)
    print("My: %s\nstats: %s, \ntheir: %s\nstats: %s" % (len(most_colliding), my_stats, len(from_first), their_stats))
    return n_trips, most_colliding, from_first


TEST_ASSIGNMENT = True
if TEST_ASSIGNMENT is True:
    trips, most_coll_solution, from_beginning_solution = test_assignment()
else:
    df = test_pandas()
