import os
from datetime import datetime, timedelta

from constants import DATE_FORMAT
from services import clear_folder_files, get_dates, calculate_section, get_content, parse_mp_file, get_permutation_time, \
    permutation_processor, Day, generate_comment, get_irrevocable_permutations, filter_backup
from table_handler import fill_table
from topaz_file_handler import read_topaz, decode_tvs_pool

cur_dir = os.getcwd()
input_dir = os.path.join(cur_dir, "input")
output_dir = os.path.join(cur_dir, "output")
initial_state_file = os.path.join(input_dir, "initial_state")
stage_3_file = os.path.join(input_dir, "stage_3.mp")
stage_5_file = os.path.join(input_dir, "stage_5.mp")
permutations_file = os.path.join(input_dir, "permutations.txt")
otvs_file = os.path.join(input_dir, "otvs.mp")

if __name__ == '__main__':

    CHUNK_SIZE = 1749
    clear_folder_files(output_dir)
    dates = get_dates()
    chunk_pool, k_pool = read_topaz(initial_state_file, CHUNK_SIZE)
    tvs_hash, _ = decode_tvs_pool(k_pool)

    try:
        irrevocable_permutations = get_irrevocable_permutations(permutations_file)
    except FileNotFoundError:
        irrevocable_permutations = set()

    backup_permutations, stage_3_permutations = parse_mp_file(stage_3_file, "backup")
    backup_permutations = filter_backup(backup_permutations, irrevocable_permutations)

    try:
        stage_5_permutations = parse_mp_file(stage_5_file)
    except FileNotFoundError:
        stage_5_permutations = backup_permutations

    otvs_permutations = parse_mp_file(otvs_file)

    stage_3_iter = iter(stage_3_permutations)
    stage_5_iter = iter(stage_5_permutations)
    otvs_iter = iter(otvs_permutations)

    time_by_stage_3_permutation = get_permutation_time(
        len(stage_3_permutations),
        dates.stage_3_begin,
        dates.stage_3_end
    )
    time_by_stage_5_permutation = get_permutation_time(
        len(stage_5_permutations), dates.stage_5_begin,
        dates.stage_5_end
    )
    time_by_otvs_permutation = get_permutation_time(len(otvs_permutations), dates.otvs_begin, dates.otvs_end)

    # print(
    #     f"Среднее время перестановки: \n"
    #     f"этап 3 - {ceil(time_by_stage_3_permutation / 60)} мин,\n"
    #     f"этап 5 - {ceil(time_by_stage_5_permutation / 60)} мин,\n"
    #     f"отвс - {ceil(time_by_otvs_permutation / 60)} мин."
    # )

    days = []
    day_iter = 0
    while True:
        today = dates.begin_date + timedelta(days=day_iter)

        # выгрузка ТВС из АЗ в БВ
        permutation_processor(
            period_begin=dates.stage_3_begin,
            period_end=dates.stage_3_end,
            today=today,
            time_by_permutation=time_by_stage_3_permutation,
            iterator=stage_3_iter,
            tvs_hash=tvs_hash,
        )

        # загрузка ТВС из БВ в АЗ
        permutation_processor(
            period_begin=dates.stage_5_begin,
            period_end=dates.stage_5_end,
            today=today,
            time_by_permutation=time_by_stage_5_permutation,
            iterator=stage_5_iter,
            tvs_hash=tvs_hash,
        )

        # выгрузка ОТВС
        permutation_processor(
            period_begin=dates.otvs_begin,
            period_end=dates.otvs_end,
            today=today,
            time_by_permutation=time_by_otvs_permutation,
            iterator=otvs_iter,
            tvs_hash=tvs_hash,
        )

        # эти сущности лишь ссылаются на объекты ТВС, находящиеся в tvs_hash
        az_content, b03_content, b01_content, b02_content = get_content(tvs_hash)
        count_az, heat_az = calculate_section(az_content, today)
        count_b03, heat_b03 = calculate_section(b03_content, today)
        count_b01, heat_b01 = calculate_section(b01_content, today)
        count_b02, heat_b02 = calculate_section(b02_content, today)

        try:
            comment = generate_comment(days[-1], count_az, count_b03, count_b01, count_b02)
        except IndexError:
            comment = ""

        days.append(Day(
            today,
            count_az,
            heat_az,
            count_b03,
            heat_b03,
            count_b01,
            heat_b01,
            count_b02,
            heat_b02,
            comment
        ))

        if today >= dates.end_date:
            break
        day_iter += 1

    # готовим данные и заполняем итоговую таблицу
    summary = {
        "block": dates.block_number,
        "begin": datetime.strftime(dates.begin_date, DATE_FORMAT),
        "end": datetime.strftime(dates.end_date, DATE_FORMAT)
    }

    table_data = []
    for day in days:
        row = [
            f"{datetime.strftime(day.date, DATE_FORMAT)}",
            f"{day.count_az} / {round(day.heat_az, 1)}",
            f"{day.count_b03} / {round(day.heat_b03, 1)}",
            f"{day.count_b01} / {round(day.heat_b01, 1)}",
            f"{day.count_b02} / {round(day.heat_b02, 1)}",
            f"{day.comment}"
        ]
        table_data.append(row)

    fill_table(table_data, summary)
