from datetime import date

SIGNS_DATA = [
    (1, 1, 1, 19, "capricorn"), (1, 20, 2, 18, "aquarius"), (2, 19, 3, 20, "pisces"),
    (3, 21, 4, 19, "aries"), (4, 20, 5, 20, "taurus"), (5, 21, 6, 20, "gemini"),
    (6, 21, 7, 22, "cancer"), (7, 23, 8, 22, "leo"), (8, 23, 9, 22, "virgo"),
    (9, 23, 10, 22, "libra"), (10, 23, 11, 21, "scorpio"), (11, 22, 12, 21, "sagittarius"),
    (12, 22, 12, 31, "capricorn"),
]

SIGNS_RU = {
    "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы", "cancer": "Рак",
    "leo": "Лев", "virgo": "Дева", "libra": "Весы", "scorpio": "Скорпион",
    "sagittarius": "Стрелец", "capricorn": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы",
}

SIGNS_EMOJI = {
    "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋",
    "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
    "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓",
}


def zodiac_from_date(d: date) -> str:
    m, day = d.month, d.day
    for fm, fd, tm, td, sign in SIGNS_DATA:
        if (m > fm or (m == fm and day >= fd)) and (m < tm or (m == tm and day <= td)):
            return sign
    return "capricorn"
