import re
from typing import List, Tuple

import pandas as pd


def parse_timestamps(busy_ranges: str):
    timestamp_pattern = r"Timestamp\('(.*?)'\)"
    matches = re.findall(r"\[" + timestamp_pattern + ", " + timestamp_pattern + "]", busy_ranges)

    return matches


def parse_and_load_trip_pairs(busy_ranges: str):
    matches = parse_timestamps(busy_ranges=busy_ranges)
    pairs = []
    for match in matches:
        try:
            start_stamp, end_stamp = match
        except ValueError as e:
            print("Invalid pair, skipping: msg: %s" % e)
            continue
        try:
            start = pd.Timestamp(start_stamp)
            end = pd.Timestamp(end_stamp)
        except ValueError as e:
            print("Failed to convert to timestamp, skipping, msg: %s" % e)
            continue
        pairs.append((start, end))
    return pairs


def is_available(
        busy_ranges: List[Tuple[pd.Timestamp, pd.Timestamp]],
        start: pd.Timestamp,
        end: pd.Timestamp,
) -> bool:
    for busy_range in busy_ranges:
        busy_start, busy_end = busy_range
        if busy_start < start < busy_end:
            return False
        elif start < busy_start < end:
            return False
    return True


def check_vehicle_availability(
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        df_path: str = "vehicle_availability.csv",
):
    try:
        df = pd.read_csv(df_path, converters={"busy_ranges": parse_and_load_trip_pairs})
    except Exception as e:
        print("Failed to load data frame from %s: %s" % (df_path, e))
        raise ValueError("Invalid CSV file") from e

    df['is_available'] = df['busy_ranges'].apply(is_available, args=(start_time, end_time))
    return df
