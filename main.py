import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

# ================= НАСТРОЙКИ =================
GUILD_ID = 1467457247451678887      # ID сервера
CHANNEL_ID = 1468379673292443809    # ID голосового канала
UTC_OFFSET = 5                      # Тюмень UTC+5
# ============================================


# ===== Русские названия + эмодзи =====
BOSS_NAMES = {
    "Kzarka": "👹 Кзарка",
    "Karanda": "🦅 Каранда",
    "Kutum": "🐍 Кутум",
    "Nouver": "🔥 Нубэр",
    "Offin": "🌳 Оффин",
    "Quint": "🗿 Квинт",
    "Muraka": "🐻 Мурака",
    "Golden Pig King": "🐷 Золотой Кабан",
    "Uturi": "❄️ Утури",
    "Sangoon": "🐺 Сангун",
    "Bulgasa": "🩸 Булгаса",
}
# ====================================


# ===== Расписание (UTC) =====
SCHEDULE = {
    "Mon": [("08:00", "Kzarka"), ("16:00", "Offin"), ("17:00", "Karanda"),
            ("18:00", "Kutum"), ("23:00", "Kzarka"), ("00:00", "Kutum")],

    "Tue": [("08:00", "Karanda"), ("17:00", "Kzarka"), ("18:00", "Nouver"),
            ("23:00", "Kutum"), ("00:00", "Nouver")],

    "Wed": [("08:00", "Nouver"), ("17:00", "Kutum"), ("18:00", "Karanda"),
            ("23:00", "Quint"), ("00:00", "Kzarka")],

    "Thu": [("08:00", "Kutum"), ("17:00", "Kzarka"), ("18:00", "Nouver"),
            ("23:00", "Karanda"), ("00:00", "Nouver")],

    "Fri": [("08:00", "Nouver"), ("17:00", "Kutum"), ("18:00", "Kzarka"),
            ("23:00", "Offin"), ("00:00", "Karanda")],

    "Sat": [("12:00", "Karanda"), ("15:00", "Quint"), ("23:15", "Nouver")],

    "Sun": [("12:00", "Kutum"), ("14:00", "Offin"), ("15:00", "Karanda"),
            ("17:00", "Kzarka"), ("23:00", "Nouver")]
}
# ============================


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ===== Текущее время Тюмени =====
def now_local():
    return datetime.now(timezone.utc) + timedelta(hours=UTC_OFFSET)


# ===== Красивый формат времени =====
def format_time(minutes: int):
    if minutes <= 0:
        return "🔔 СЕЙЧАС"

    hours = minutes // 60
    mins = minutes % 60

    if hours:
        return f"{hours}ч {mins}м" if mins else f"{hours}ч"
    return f"{mins}м"


# ===== Поиск ближайшего босса =====
def get_next_boss():
    now = now_local()
    today = now.strftime("%a")

    days = list(SCHEDULE.keys())
    today_index = days.index(today)

    nearest_time = None
    nearest_boss = None

    for add_day in range(7):
        day_name = days[(today_index + add_day) % 7]

        for time_str, boss in SCHEDULE[day_name]:
            hour, minute = map(int, time_str.split(":"))

            boss_time = now.replace(hour=hour, minute=minute,
                                    second=0, microsecond=0)

            if add_day:
                boss_time += timedelta(days=add_day)

            if boss_time > now:
                if nearest_time is None or boss_time < nearest_time:
                    nearest_time = boss_time
                    nearest_boss = boss

    if nearest_time is None:
        return None, 0

    minutes_left = int((nearest_time - now).total_seconds() // 60)
    return nearest_boss, minutes_left


# ===== Автообновление канала =====
@tasks.loop(minutes=1)
async def update_channel():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        return

    boss, minutes = get_next_boss()
    if not boss:
        return

    boss_name = BOSS_NAMES.get(boss, boss)
    time_text = format_time(minutes)

    new_name = f"{boss_name} • {time_text} • Тюмень (UTC+5)"

    if channel.name != new_name:
        await channel.edit(name=new_name)


# ===== Запуск =====
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    update_channel.start()


bot.run(TOKEN)
