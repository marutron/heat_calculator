from datetime import datetime
import os

from constants import DATE_FORMAT
from services import clear_folder_files
from topaz_file_handler import read_topaz, decode_tvs_pool

cur_dir = os.getcwd()
input_dir = os.path.join(cur_dir, "input")
output_dir = os.path.join(cur_dir, "output")
initial_state_file = os.path.join(input_dir, "initial_state")

if __name__ == '__main__':
    CHUNK_SIZE = 1749
    clear_folder_files(output_dir)
    # date = input_date()
    date = datetime.strptime("02.01.2026", DATE_FORMAT)
    chunk_pool, k_pool = read_topaz(initial_state_file, CHUNK_SIZE)
    # chunk_pool_mapper: dict[str, int] задает соответствие номера ТВС индексу в списке chunk_pool
    bv_hash_initial, chunk_pool_mapper = decode_tvs_pool(k_pool, date=date)
    pass
