import re
from typing import List, Tuple

import pandas as pd


def parse_timestamps(text: str) -> List[Tuple[str, str]]:
    """
    Match all Timestamp pairs and return them in the list
    :param text: string representation of a list of timestamp pairs
    :return: list of timestamp pairs matched frm the busy_ranges
    """
    timestamp_pattern = r"Timestamp\('(.*?)'\)"
    timestamp_pair_pattern = r"\[" + timestamp_pattern + ", " + timestamp_pattern + "]"
    matches = re.findall(timestamp_pair_pattern, text)

    return matches


def parse_and_load_trip_pairs(text: str) -> List[Tuple[pd.Timestamp, pd.Timestamp]]:
    """
    Find timestamp pairs from the text, create pd.Timestamp instances and return the list of tuples
    :param text: text from which timestamp pairs should be extracted
    :return: list of pairs of timestamps
    """
    matches = parse_timestamps(text=text)
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
    """
    Core of the algorithm. Take the list of pairs of start and end timestamps, start and end of desired time range
    and get boolean indicating weather the given start, end is colliding with any of the busy_ranges or not
    :param busy_ranges: list of pairs of start and end timestamps
    :param start: start of the desired time period
    :param end: end of the desired time period
    :return: boolean indicating weather the given time range collides with any from busy_ranges
    """
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
) -> pd.DataFrame:
    """
    Parse the df_path csv file, and for each row detect if the the given time range collides with busy_ranges
    :param start_time: start time of the time period
    :param end_time: end time of the time period
    :param df_path: path to the dsv file
    :return: pd.DataFrame with new column added to it indicating time collision with desired time range
    """
    try:
        df = pd.read_csv(df_path, converters={"busy_ranges": parse_and_load_trip_pairs})
    except Exception as e:
        print("Failed to load data frame from %s: %s" % (df_path, e))
        raise ValueError("Invalid CSV file") from e

    df['is_available'] = df['busy_ranges'].apply(is_available, args=(start_time, end_time))
    return df
