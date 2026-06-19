from calendar import monthrange
from datetime import datetime, date, timedelta

from fastapi import APIRouter

router = APIRouter()

NEW_MOON_REF = datetime(2000, 1, 6, 18, 14)
LUNAR_CYCLE = 29.53058867

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
            "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]

PHASE_NAMES_RU = ["Новолуние", "Молодой месяц", "Первая четверть", "Прибывающая",
                  "Полнолуние", "Убывающая", "Последняя четверть", "Старый месяц"]
PHASE_NAMES_EN = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
                  "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
PHASE_ICONS = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]

RECS_RU = [
    ["Начинай новые дела", "Ставь намерения на цикл", "Медитируй на цели"],
    ["Составь план действий", "Доверяй интуиции", "Записывай идеи"],
    ["Действуй решительно", "Преодолевай препятствия", "Принимай вызовы"],
    ["Совершенствуй начатое", "Учись и развивайся", "Укрепляй связи"],
    ["Празднуй результаты", "Благодари вселенную", "Проявляй щедрость"],
    ["Делись знаниями", "Анализируй пройденное", "Помогай другим"],
    ["Отпускай лишнее", "Завершай дела", "Прощай обиды"],
    ["Отдыхай и восстанавливайся", "Слушай тело", "Готовься к новому циклу"],
]
RECS_EN = [
    ["Start new projects", "Set intentions for the cycle", "Meditate on your goals"],
    ["Make a plan of action", "Trust your intuition", "Write down your ideas"],
    ["Act decisively", "Overcome obstacles", "Accept challenges"],
    ["Refine what you started", "Learn and grow", "Strengthen bonds"],
    ["Celebrate results", "Thank the universe", "Be generous"],
    ["Share knowledge", "Analyze the journey", "Help others"],
    ["Let go of excess", "Finish projects", "Forgive grievances"],
    ["Rest and recharge", "Listen to your body", "Prepare for a new cycle"],
]

ENERGY_RU = ["Минимальная", "Растущая", "Активная", "Высокая",
             "Максимальная", "Снижающаяся", "Умеренная", "Низкая"]
ENERGY_EN = ["Minimal", "Rising", "Active", "High",
             "Maximum", "Declining", "Moderate", "Low"]


def _calc_lunar(dt: datetime) -> dict:
    days_since = (dt - NEW_MOON_REF).total_seconds() / 86400
    pos_in_cycle = days_since % LUNAR_CYCLE
    lunar_day = int(pos_in_cycle) + 1
    phase_index = int(pos_in_cycle / LUNAR_CYCLE * 8) % 8
    sign_index = int(pos_in_cycle / LUNAR_CYCLE * 12) % 12
    return {
        "lunar_day": min(lunar_day, 30),
        "phase_index": phase_index,
        "sign_index": sign_index,
    }


@router.get("/lunar/today")
async def lunar_today(lang: str = "ru"):
    info = _calc_lunar(datetime.utcnow())
    pi = info["phase_index"]
    si = info["sign_index"]
    recs = RECS_RU[pi] if lang == "ru" else RECS_EN[pi]
    return {
        "lunar_day": info["lunar_day"],
        "phase_name": PHASE_NAMES_RU[pi] if lang == "ru" else PHASE_NAMES_EN[pi],
        "phase_icon": PHASE_ICONS[pi],
        "moon_sign": SIGNS_RU[si] if lang == "ru" else SIGNS[si],
        "recommendations": recs,
        "energy": ENERGY_RU[pi] if lang == "ru" else ENERGY_EN[pi],
    }


@router.get("/lunar/month")
async def lunar_month():
    today = date.today()
    _, days_in_month = monthrange(today.year, today.month)
    result = []
    for d in range(1, days_in_month + 1):
        dt = datetime(today.year, today.month, d, 12, 0)
        info = _calc_lunar(dt)
        result.append({
            "date": f"{today.year}-{today.month:02d}-{d:02d}",
            "lunar_day": info["lunar_day"],
            "phase_icon": PHASE_ICONS[info["phase_index"]],
        })
    return result
