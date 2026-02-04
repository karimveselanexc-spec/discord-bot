1  import os
2  import discord
3  from discord.ext import commands, tasks
4  from datetime import datetime, timedelta, timezone
5  import math


# ================= TOKEN =================
TOKEN = os.getenv("TOKEN")

# ================= НАСТРОЙКИ =================
GUILD_ID = 1467457427451678867
CHANNEL_ID = 1468379673292443809
UTC_OFFSET = 5  # Тюмень
SOON_MINUTES = 5          # когда писать "Скоро"
BOSS_ACTIVE_MINUTES = 2   # сколько минут считать "Сейчас"
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


# ===== Расписание =====
SCHEDULE = {
    "Mon": [("18:00", "Kutum")],
    "Tue": [("18:00", "Nouver")],
    "Wed": [("18:00", "Karanda")],
    "Thu": [("18:00", "Kutum")],
    "Fri": [("18:00", "Offin")],
    "Sat": [("15:00", "Nouver")],
    "Sun": [("14:00", "Offin")],
}


# ================= INTENTS =================
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True  # убирает warning

bot = commands.Bot(command_prefix="!", intents=intents)


# ================= ВРЕМЯ =================
def now_local():
    return datetime.now(timezone.utc) + timedelta(hours=UTC_OFFSET)


def format_time(minutes):

    # уже появился
   # уже появился
if minutes <= BOSS_ACTIVE_MINUTES:
    return "🔥 СЕЙЧАС"

# скоро появится
if minutes <= SOON_MINUTES:
    return "⚔ СКОРО"
    # обычный таймер
    minutes = math.ceil(minutes / 5) * 5

    h = minutes // 60
    m = minutes % 60

    if h:
        return f"⏳ до спавна: {h}ч {m}м"
    return f"⏳ до спавна: {m}м"
# ================= ПОИСК БОССА =================
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
            h, m = map(int, time_str.split(":"))

            boss_time = now.replace(hour=h, minute=m, second=0, microsecond=0)

            if add_day:
                boss_time += timedelta(days=add_day)

            if boss_time > now:
                if nearest_time is None or boss_time < nearest_time:
                    nearest_time = boss_time
                    nearest_boss = boss

    minutes = int((nearest_time - now).total_seconds() // 60)
    return nearest_boss, minutes
    @tasks.loop(minutes=5)

# ================= ОБНОВЛЕНИЕ КАНАЛА =================
@tasks.loop(minutes=1)
async def update_channel():
    print("\n==== ЦИКЛ ОБНОВЛЕНИЯ ====")

    try:
        guild = bot.get_guild(GUILD_ID)
        print("guild ->", guild)

        if not guild:
            print("❌ Сервер не найден")
            return

        channel = guild.get_channel(CHANNEL_ID)
        print("channel ->", channel)

        if not channel:
            print("❌ Канал не найден")
            return

        boss, minutes = get_next_boss()
        print("boss/minutes ->", boss, minutes)

        boss_name = BOSS_NAMES.get(boss, boss)
        time_text = format_time(minutes)

        new_name = f"{boss_name} • {time_text}"
        print("new name ->", new_name)

        if channel.name != new_name:
            await channel.edit(name=new_name)
            print("✅ Канал обновлён")
        else:
            print("ℹ️ Уже актуально")

    except Exception as e:
        print("❌ ОШИБКА:", e)

# ================= ЗАПУСК =================
# ================= НАПОМИНАЛКА О РЕСТАРТЕ =================
from datetime import datetime, timedelta

RESET_HOURS = 0.05
PANEL_URL = "https://justrunmy.app/panel/application/4504/"
REMINDER_CHANNEL_ID = 1468572187731562702

start_time = datetime.now(timezone.utc)

def format_time_left(td: timedelta):
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    return f"{h}ч {m}м"

@tasks.loop(minutes=10)
async def restart_reminder():
    now = datetime.now(timezone.utc)
    left = timedelta(hours=RESET_HOURS) - (now - start_time)

    if left.total_seconds() <= 0:
        return

    channel = bot.get_channel(REMINDER_CHANNEL_ID)
    if not channel:
        return

    if 0 < left.total_seconds() <= 3600:
        await channel.send(
            f"⚠️ <@&1467620945056501972>\n"
            f"🚨 Босс, у меня 1% HP… сейчас отключусь 🤖\n\n"
            f"⏳ Осталось: **{format_time_left(left)}**\n"
            f"🧯 Срочно тыкни сюда:\n{PANEL_URL}"
        )

@bot.event
async def on_ready():
    print(f"\n🟢 Бот запущен как {bot.user}")
    print("Запускаю цикл обновления...")
    update_channel.start()
    restart_reminder.start()

bot.run(TOKEN)
