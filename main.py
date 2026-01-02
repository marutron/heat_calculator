import os
from dataclasses import dataclass
from datetime import datetime, timedelta

from services import clear_folder_files, get_dates, calculate_section, get_content
from topaz_file_handler import read_topaz, decode_tvs_pool

cur_dir = os.getcwd()
input_dir = os.path.join(cur_dir, "input")
output_dir = os.path.join(cur_dir, "output")
initial_state_file = os.path.join(input_dir, "initial_state")


@dataclass
class Day:
    date: datetime
    count_az: int
    heat_az: float
    count_b03: int
    heat_b03: float
    count_b01: int
    heat_b01: float
    count_b02: int
    heat_b02: float


if __name__ == '__main__':

    CHUNK_SIZE = 1749
    clear_folder_files(output_dir)
    dates = get_dates()
    chunk_pool, k_pool = read_topaz(initial_state_file, CHUNK_SIZE)
    tvs_hash, _ = decode_tvs_pool(k_pool)
    az_content, b03_content, b01_content, b02_content = get_content(tvs_hash)

    days = []
    day_iter = 0
    while True:
        date = dates.begin_date + timedelta(days=day_iter)
        count_az, heat_az = calculate_section(az_content, date)
        count_b03, heat_b03 = calculate_section(b03_content, date)
        count_b01, heat_b01 = calculate_section(b01_content, date)
        count_b02, heat_b02 = calculate_section(b02_content, date)

        days.append(Day(
            date,
            count_az,
            heat_az,
            count_b03,
            heat_b03,
            count_b01,
            heat_b01,
            count_b02,
            heat_b02
        ))

        if date >= dates.end_date:
            break
        day_iter += 1

    pass
