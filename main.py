import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

# ================= НАСТРОЙКИ =================
GUILD_ID = 1467457427451673867
CHANNEL_ID = 1468379673292443809
UTC_OFFSET = 5  # Тюмень UTC+5
# ============================================


# ===== Названия боссов =====
BOSS_NAMES = {
    "Kzarka": "🦂 Кзарка",
    "Karanda": "🦅 Караганда",
    "Kutum": "🐍 Кутум",
    "Nouver": "🔥 Нубэр",
    "Offin": "🌳 Оффин",
    "Quint": "🗿 Квинт",
}


# ===== Расписание (UTC) =====
SCHEDULE = {
    "Mon": [("18:00", "Kutum")],
    "Tue": [("18:00", "Nouver")],
    "Wed": [("18:00", "Karanda")],
    "Thu": [("18:00", "Kutum")],
    "Fri": [("18:00", "Offin")],
    "Sat": [("15:00", "Nouver")],
    "Sun": [("14:00", "Offin")],
}


# ===== Intents =====
intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ===== Текущее время =====
def now_local():
    return datetime.now(timezone.utc) + timedelta(hours=UTC_OFFSET)


# ===== Красивый формат =====
def format_time(minutes):
    if minutes <= 0:
        return "🔥 СЕЙЧАС"

    h = minutes // 60
    m = minutes % 60

    if h:
        return f"{h}ч {m}м"
    return f"{m}м"


# ===== Поиск ближайшего босса =====
def get_next_boss():
    now = now_local()
    today = now.strftime("%a")

    days = list(SCHEDULE.keys())
    today_index = days.index(today)

    nearest = None
    nearest_boss = None

    for add_day in range(7):
        day_name = days[(today_index + add_day) % 7]

        for time_str, boss in SCHEDULE[day_name]:
            h, m = map(int, time_str.split(":"))

            boss_time = now.replace(hour=h, minute=m, second=0, microsecond=0)

            if add_day:
                boss_time += timedelta(days=add_day)

            if boss_time > now:
                if nearest is None or boss_time < nearest:
                    nearest = boss_time
                    nearest_boss = boss

    minutes = int((nearest - now).total_seconds() // 60)
    return nearest_boss, minutes


# ===== Обновление канала =====
@tasks.loop(minutes=1)
async def update_channel():

    try:
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            print("❌ Сервер не найден")
            return

        channel = guild.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ Канал не найден")
            return

        boss, minutes = get_next_boss()

        boss_name = BOSS_NAMES.get(boss, boss)
        time_text = format_time(minutes)

        new_name = f"{boss_name} • {time_text}"

        if channel.name != new_name:
            await channel.edit(name=new_name)
            print("✅ Канал обновлен:", new_name)

    except Exception as e:
        print("❌ Ошибка:", e)


# ===== Запуск =====
@bot.event
async def on_ready():
    print(f"🟢 Бот запущен как {bot.user}")
    update_channel.start()


bot.run(TOKEN)
