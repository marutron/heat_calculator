import os
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from constants import DATE_FORMAT, TIME_DATE_FORMAT
from input import controller

if TYPE_CHECKING:
    from classes import TVS


def clear_folder_files(folder_path):
    """Удаляет все файлы в папке и её вложенных подпапках, сохраняя структуру каталогов."""
    try:
        # Обходим все директории и поддиректории
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении файла {file_path}: {e}")
    except Exception as e:
        print(f"Ошибка при обходе директории {folder_path}: {e}")


def parse_real48(real48):
    """
    Преобразует массив из 6 байт (формат Real48 Delphi) в число типа float (double).

    Args:
        real48: list или bytes длиной 6 — байты числа в формате Real48 (little‑endian).

    Returns:
        float — значение в формате double.
    """
    if len(real48) != 6:
        raise ValueError("Массив real48 должен содержать ровно 6 байт")

    # Если первый байт равен 0, число считается нулевым
    if real48[0] == 0:
        return 0.0

    # Экспонента: первый байт минус bias (129)
    exponent = real48[0] - 129.0

    # Сборка мантиссы
    mantissa = 0.0
    # Обрабатываем байты 1–4 (индексы 1–4 в массиве)
    for i in range(1, 5):
        mantissa += real48[i]
        mantissa *= 0.00390625  # Эквивалентно делению на 256

    # Добавляем младший байт (5‑й элемент, индекс 5), маскируя старший бит (знак)
    mantissa += (real48[5] & 0x7F)
    mantissa *= 0.0078125  # Эквивалентно делению на 128

    # Неявная единица перед двоичной точкой
    mantissa += 1.0

    # Проверяем старший бит последнего байта — это бит знака
    if (real48[5] & 0x80) == 0x80:
        mantissa = -mantissa

    # Итоговый результат: мантисса * 2^экспонента
    return mantissa * (2.0 ** exponent)


@dataclass
class Dates:
    begin_date: datetime
    end_date: datetime
    stage_3_begin: datetime
    stage_3_end: datetime
    stage_5_begin: datetime
    stage_5_end: datetime
    otvs_begin: datetime
    otvs_end: datetime


def get_dates() -> Dates:
    """
    Обрабатывает получение дат из файла `input/controller.py`
    :return: словарь дат из controller.py
    """
    try:
        dates = Dates(
            begin_date=datetime.strptime(controller.begin_date, DATE_FORMAT),
            end_date=datetime.strptime(controller.end_date, DATE_FORMAT),
            stage_3_begin=datetime.strptime(controller.stage_3_begin, TIME_DATE_FORMAT),
            stage_3_end=datetime.strptime(controller.stage_3_end, TIME_DATE_FORMAT),
            stage_5_begin=datetime.strptime(controller.stage_5_begin, TIME_DATE_FORMAT),
            stage_5_end=datetime.strptime(controller.stage_5_end, TIME_DATE_FORMAT),
            otvs_begin=datetime.strptime(controller.otvs_begin, TIME_DATE_FORMAT),
            otvs_end=datetime.strptime(controller.otvs_end, TIME_DATE_FORMAT)
        )
    except ValueError as err:
        print("Ошибка парсинга дат, проверьте данные в файле `input/controller.py`")
        raise err
    return dates


def get_content(tvs_hash: dict[str, "TVS"]) -> (dict[str, "TVS"], dict[str, "TVS"], dict[str, "TVS"], dict[str, "TVS"]):
    """
    Сортирует содержимое общего словаря с ТВС на списки содержимого АЗ и отсеков БВ
    :param tvs_hash: словарь, содержащий все ТВС
    :return:
    """
    az = {}
    b_03 = {}
    b_01 = {}
    b_02 = {}
    for tvs in tvs_hash.values():
        match tvs.get_section():
            case "az":
                az[tvs.number] = tvs
            case "b03":
                b_03[tvs.number] = tvs
            case "b01":
                b_01[tvs.number] = tvs
            case "b02":
                b_02[tvs.number] = tvs

    return az, b_03, b_01, b_02


def calculate_section(content: dict[str, "TVS"], date: datetime) -> (int, float):
    """
    Подсчитывает количество ТВС в отсеке и общее тепловыделение отсека
    :param content:
    :param date:
    :return:
    """
    count = len(content)
    heat = 0.0
    for tvs in content.values():
        heat += tvs.calculate_heat(date)
    return count, heat


@dataclass
class Permutation:
    tvs_number: str
    new_most: int
    new_tel: int


def parse_mp_file(file_path: str) -> list[Permutation]:
    """
    Парсит файл МП в список последовательных перестановок
    :param file_path:
    :return:
    """
    permutations = []
    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            split_line = line.split()
            try:
                tvs_number = split_line[3]
                try:
                    new_most = int(split_line[6])
                    new_tel = int(split_line[7])
                except ValueError as err:
                    print(f"Ошибка парсинга файла МП: `{file_path}`.\n(Ошибка приведения типов int()).")
                    raise err
            except IndexError as err:
                print(f"Ошибка парсинга файла МП: `{file_path}`.\n(Ошибка индексации строки файла.)")
                raise err

            permutations.append(Permutation(tvs_number, new_most, new_tel))

        return permutations
