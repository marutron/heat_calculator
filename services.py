import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import ceil, floor
from typing import TYPE_CHECKING, Literal, Iterator

from constants import DATE_FORMAT, TIME_DATE_FORMAT
from input import controller

if TYPE_CHECKING:
    from classes import TVS


@dataclass
class Permutation:
    tvs_number: str
    new_most: int
    new_tel: int


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
    comment: str


@dataclass
class Dates:
    block_number: int
    begin_date: datetime
    end_date: datetime
    stage_3_begin: datetime
    stage_3_end: datetime
    stage_5_begin: datetime
    stage_5_end: datetime
    otvs_begin: datetime
    otvs_end: datetime


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


def get_dates() -> Dates:
    """
    Обрабатывает получение дат из файла `input/controller.py`
    :return: словарь дат из controller.py
    """
    try:
        begin_date = datetime.strptime(controller.begin_date, DATE_FORMAT)
        end_date = datetime.strptime(controller.end_date, DATE_FORMAT)
        stage_3_begin = datetime.strptime(controller.stage_3_begin, TIME_DATE_FORMAT)
        stage_3_end = datetime.strptime(controller.stage_3_end, TIME_DATE_FORMAT)
        stage_5_begin = datetime.strptime(controller.stage_5_begin, TIME_DATE_FORMAT)
        stage_5_end = datetime.strptime(controller.stage_5_end, TIME_DATE_FORMAT)
        otvs_begin = datetime.strptime(controller.otvs_begin, TIME_DATE_FORMAT)
        otvs_end = datetime.strptime(controller.otvs_end, TIME_DATE_FORMAT)
    except ValueError as err:
        print("Ошибка парсинга дат, проверьте данные в файле `input/controller.py`")
        raise err

    # полную проверку делать очень долго => минимальную валидацию разместил здесь
    assert begin_date < end_date
    assert stage_3_begin < stage_3_end
    assert stage_5_begin < stage_5_end
    assert otvs_begin < otvs_end

    dates = Dates(
        controller.block_number,
        begin_date,
        end_date,
        stage_3_begin,
        stage_3_end,
        stage_5_begin,
        stage_5_end,
        otvs_begin,
        otvs_end,
    )
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

            # не учитываем перестановки имитаторов нигде
            if "ITVS" not in tvs_number:
                permutations.append(Permutation(tvs_number, new_most, new_tel))

        return permutations


def get_permutation_time(permutations_count: int, begin: datetime, end: datetime) -> float:
    """
    Высчитывает время на одну перестановку (округляет в большую сторону)
    :param permutations_count:
    :param begin:
    :param end:
    :return:
    """
    overall_time = (end - begin).total_seconds()
    try:
        permutation_time = ceil(overall_time / permutations_count)
    except ZeroDivisionError as err:
        print("Количество перестановок = 0")
        raise err
    return permutation_time


def make_permutations(
        period_begin_time: datetime,
        period_end_time: datetime,
        time_by_permutation: float,
        iterator: Iterator[Permutation],
        tvs_hash: dict[str, "TVS"],
        mode: Literal["floor", "ceil"] = "ceil"
):
    """
    Выполняет перестановки, укладывающиеся в отведенный промежуток времени
    :param period_begin_time: конец временного периода
    :param period_end_time: начало временного периода (дня)
    :param time_by_permutation: время, затрачиваемое на одну перестановку
    :param iterator: итератор перестановок
    :param tvs_hash: словарь, содержащий информащию о всех ТВС (мутирует)
    :param mode: режим округления
    :return: None, но мутирует `tvs_hash`
    """
    # вычисляем время, доступное для перестановок (в секундах)
    time_reserve = (period_end_time - period_begin_time).total_seconds()
    # вычисляем доступное число перестановок
    match mode:
        case "floor":
            perm_number = floor(time_reserve / time_by_permutation)
        case _:
            perm_number = ceil(time_reserve / time_by_permutation)

    # делаем перестановки
    i = 1
    while i <= perm_number:
        try:
            permutation = next(iterator)
        except StopIteration:
            i += 1
            continue
        tvs = tvs_hash[permutation.tvs_number]
        tvs.most = permutation.new_most
        tvs.tel = permutation.new_tel
        i += 1


def permutation_processor(
        period_begin: datetime,
        period_end: datetime,
        today: datetime,
        time_by_permutation: float,
        iterator: Iterator[Permutation],
        tvs_hash: dict[str, "TVS"],
):
    """
    Производит перестановки в период времени от `period_begin` до `period_end`
    :param period_begin: начало обрабатываемого периода
    :param period_end: конец обрабатываемо периода
    :param today: день (главный итератор)
    :param time_by_permutation: время на перестановку
    :param iterator: итератор по списку перестановок
    :param tvs_hash: словарь, содержащий информащию о всех ТВС (мутирует)
    :return: None, но мутирует `tvs_hash`
    """
    if period_begin.date() == today.date():
        tomorrow = today + timedelta(days=1)
        make_permutations(
            period_begin_time=period_begin,
            period_end_time=tomorrow,
            time_by_permutation=time_by_permutation,
            iterator=iterator,
            tvs_hash=tvs_hash,
            mode="floor"
        )
    elif period_begin.date() < today.date() < period_end.date():
        tomorrow = today + timedelta(days=1)
        make_permutations(
            period_begin_time=today,
            period_end_time=tomorrow,
            time_by_permutation=time_by_permutation,
            iterator=iterator,
            tvs_hash=tvs_hash,
            mode="ceil"
        )
    elif today.date() == period_end.date():
        make_permutations(
            period_begin_time=today,
            period_end_time=period_end,
            time_by_permutation=time_by_permutation,
            iterator=iterator,
            tvs_hash=tvs_hash,
            mode="ceil"
        )


def generate_comment(
        last_day: Day,
        count_az: int,
        count_b03: int,
        count_b01: int,
        count_b02: int,
) -> str:
    """
    Генерирует комментарий "Перестановки" для корректного заполнения итоговой таблицы
    :param last_day:
    :param count_az:
    :param count_b03:
    :param count_b01:
    :param count_b02:
    :return:
    """
    comment = []
    if last_day.count_az > count_az:
        comment.append(f"Выгрузка {last_day.count_az - count_az} ТВС в БВ.")
    elif last_day.count_az < count_az:
        comment.append(f"Загрузка {count_az - last_day.count_az} ТВС из БВ в реактор.")

    if ((last_day.count_b03 > count_b03 or last_day.count_b01 > count_b01 or last_day.count_b02 > count_b02)
            and last_day.count_az == count_az):
        delta_bv = (last_day.count_b03 + last_day.count_b01 + last_day.count_b02) - (count_b03 + count_b01 + count_b02)
        comment.append(f"Отправка " f"{delta_bv} " f"ОТВС.")

    return "".join(elm for elm in comment)
