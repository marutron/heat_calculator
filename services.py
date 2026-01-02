import os
from datetime import datetime
from typing import Optional

from constants import DATE_FORMAT


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


def input_date() -> Optional[datetime]:
    """
    Управляет получением даты вывоза от пользователя
    :return:
    """
    while True:
        input_date = input("Введите дату расчета тепловыделения или нажмите Enter для продолжения без даты: ")
        if input_date == "":
            return None
        try:
            return datetime.strptime(input_date, DATE_FORMAT)
        except:
            print(
                'Нужно ввести дату в формате "дд.мм.гггг", например 01.11.2025, или пустую строку - для отказа от ввода даты.'
            )


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
