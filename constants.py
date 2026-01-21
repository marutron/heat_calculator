TIME_DATE_FORMAT = "%d.%m.%Y %H:%M"
DATE_FORMAT = "%d.%m.%Y"
EXPOSURE_DAYS = [0, 5, 15, 30, 90, 183, 365, 730, 1095, 1460, 1825, 3650, 7300, 10960]

reactor_places_gen = {
    15: (col for col in range(24, 36, 2)),
    14: (col for col in range(21, 39, 2)),
    13: (col for col in range(20, 40, 2)),
    12: (col for col in range(19, 41, 2)),
    11: (col for col in range(18, 42, 2)),
    10: (col for col in range(17, 43, 2)),
    9: (col for col in range(16, 44, 2)),
    8: (col for col in range(17, 43, 2)),
    7: (col for col in range(16, 44, 2)),
    6: (col for col in range(17, 43, 2)),
    5: (col for col in range(18, 42, 2)),
    4: (col for col in range(19, 41, 2)),
    3: (col for col in range(20, 40, 2)),
    2: (col for col in range(21, 39, 2)),
    1: (col for col in range(24, 36, 2)),
}
