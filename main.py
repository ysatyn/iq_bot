from telebot.async_telebot import AsyncTeleBot
from telebot import types

import time
import random
import sqlite3
import asyncio
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = AsyncTeleBot(TOKEN)

conn = sqlite3.connect("iq_bot.db", check_same_thread=False)
c = conn.cursor()

good_actions = [
    "You've been hit over the head with an encyclopedia",
    "You have watched the video how to become a billionaire",
    "You have visited the laboratory, where you have checked your skills and knowledge",
    "You've attended a master class on coming up with new ideas",
    "You've learned a new fact about your country",
    "You've read the book, which has helped you with your brain",
    "You've visited the concert, where you've found new friends",
    "You've visited the art installation, where you've seen an incredible picture",
    "You've visited the quest, where you've checked your knowledge",
    "You've attended the physics lesson, where you've learned some new facts",
    "You've attended the biology lesson, where you've learned new facts about nature",
    "You've attended the history lesson, where you've learned some historical events"
]  # positive actions that increase IQ

bad_actions = [
    "You've been hit over the head with a baton",
    "You've lost your memory",
    "You've been scrolling Tik Tok through 3 hours",
    "You've been talking with an idiot during 10 minutes",
    "You've spent all day at the computer",
    "You've changed your name to 'Sergey'"]  # negative actions that lower IQ

neutral_actions = ["You've been messing around", "You've lost your memory, but you've taken the pills"]  # actions that don't affect IQ


def create_user_link(user_id: int, user_name: str) -> str:
    """
    Creates a HTMl link to a user using the ID of the user

    :param user_id: user ID
    :param user_name: user name
    :return: link to the user
    """
    link = f'<a href="tg://openmessage?user_id={user_id}">{user_name}</a>'
    return link

def main_create_tables():
    """
    Creates a table with a list of chats information
    """
    c.execute("""CREATE TABLE IF NOT EXISTS chats(
    chat_id INTEGER PRIMARY KEY UNIQUE,
    iq_count INTEGER DEFAULT 0,
    chat_name TEXT DEFAULT chat_id)""")
    conn.commit()


def create_chat_table(chat_id) -> None:
    """
    Create a chat table for the given chat ID
    :param chat_id: chat ID
    """
    safe_chat_id = -1 * chat_id
    c.execute(f"""CREATE TABLE IF NOT EXISTS '{safe_chat_id}' (
    user_id INTEGER PRIMARY KEY,
    user_name TEXT DEFAULT 'User',
    total_iq INTEGER DEFAULT 100,
    best_iq INTEGER DEFAULT 100,
    use BOOL DEFAULT False,
    status TEXT DEFAULT 'Add your text here via the /status command'
    )""")
    conn.commit()


def add_chat_to_table(chat_id, chat_name) -> bool:
    """
    Tries to add a chat to the table, if it don't already exist in the database.
    Returns True if the chat is new, False if the chat already exists in the table.
    :param chat_id: chat ID
    :param chat_name: chat name
    """
    c.execute(f"""SELECT * FROM chats WHERE chat_id = {chat_id}""")
    if c.fetchone():  # check if chat already exists in the table
        return False
    else:
        c.execute(f"""INSERT INTO chats (chat_id, chat_name) VALUES (?, ?)""", (chat_id, chat_name))
        conn.commit()
        return True


def update_chat_iq_count(chat_id: int) -> int:
    """
    Updates iq_count in table 'chats'
    :param chat_id: chat ID
    """
    safe_chat_id = -1 * chat_id
    c.execute(f"""SELECT total_iq FROM '{safe_chat_id}'""")
    users = c.fetchall()
    total_iq = sum(user[0] for user in users)

    c.execute(f"""UPDATE chats SET iq_count = ? WHERE chat_id = ?""", (total_iq, chat_id))
    conn.commit()
    return total_iq


def new_user(user_id: int, chat_id: int, user_name: str) -> bool:
    """
    Attempts to add a new user to the chat.
    Returns True if the user is new, False if the user already exists in the table.
    :param user_id: user ID
    :param chat_id: chat ID
    :param user_name: user name
    """
    safe_chat_id = -1 * chat_id
    c.execute(f"""SELECT * FROM '{safe_chat_id}' WHERE user_id = {user_id}""")
    if c.fetchone():  # checks whether the user is in the table or not
        return False
    else:
        c.execute(
            f"""INSERT OR IGNORE INTO '{safe_chat_id}' (user_id, total_iq, best_iq, user_name) VALUES (?, ?, ?, ?)""",
            (user_id, 100, 100, user_name))
        conn.commit()
        return True


def get_status(user_id: int, chat_id: int, user_name: str) -> str:
    """
    Gets the status of the user in current chat
    :param user_id: user ID
    :param chat_id: chat ID
    :param user_name: user name
    :return: user's status
    """
    safe_chat_id = chat_id * -1
    new_user(user_id, chat_id, user_name)
    c.execute(f"""SELECT status FROM '{safe_chat_id}' WHERE user_id = {user_id}""")
    status = c.fetchone()[0]
    return status

def set_new_status(user_id: int, chat_id: int, new_status: str) -> None:
    """
    Sets the new status of user in current chat
    :param user_id: user ID
    :param chat_id: chat ID
    :param new_status: new user status
    """
    safe_chat_id = -1 * chat_id
    c.execute(f"""UPDATE '{safe_chat_id}' SET status = ? WHERE user_id = ?""", (new_status, user_id))
    conn.commit()


def update_iq(user_id: int, chat_id: int) -> (int, int):
    """
    Updates user's IQ in current chat
    :param user_id: user ID
    :param chat_id: chat ID
    :return: change in IQ, total IQ
    """
    safe_chat_id = -1 * chat_id
    c.execute(f"""SELECT total_iq, best_iq FROM '{safe_chat_id}' WHERE user_id = {user_id}""")
    total_iq, best_iq = c.fetchone()
    plus_or_minus = random.randint(0, 100)
    delta = random.randint(0, 20)
    if plus_or_minus <= 40:
        delta = -1 * delta
    total_iq += delta
    if total_iq > best_iq:
        best_iq = total_iq

    c.execute(f"""UPDATE '{safe_chat_id}' SET total_iq = ?, best_iq = ?, use = ? WHERE user_id = ?""", (total_iq, best_iq, True, user_id))
    conn.commit()

    return delta, total_iq


def remake(chat_id: int) -> None:
    """
    Remakes a chat's table
    :param chat_id: chat ID
    """
    safe_chat_id = -1 * chat_id
    c.execute(f"""DROP TABLE IF EXISTS '{safe_chat_id}'""")
    conn.commit()

    create_chat_table(chat_id)


def seconds_until_next_hour() -> int:
    """
    :return number of seconds until next hour
    """
    x = time.localtime()
    current_minute = x.tm_min
    current_second = x.tm_sec

    minutes = 60 - current_minute
    seconds = 60 - current_second

    return minutes * 60 + seconds


@bot.message_handler(commands=["start"])
async def start_command(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    bot_info = await bot.get_me()  # bot gets info about himself
    bot_username = bot_info.username  # bot gets his username

    link_add = f"https://t.me/{bot_username}?startgroup=me&admin=change_info+restrict_members+delete_messages+pin_messages+invite_users"  # link to add the bot to a group

    top_message = f"Hi, {user_name}! Unfortunately this bot only works in groups. To add it to a group, use the link below ⬇️"

    markup = types.InlineKeyboardMarkup()  # создание кнопок
    markup.add(types.InlineKeyboardButton(text="Add bot to a group", url=link_add))  # добавляем кнопку для добавления бота в чат

    if message.chat.type == "private":
        await bot.send_message(chat_id, top_message, reply_markup=markup)


@bot.message_handler(commands=["help"])
async def help_command(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    markup = types.InlineKeyboardMarkup()
    if message.chat.type == "private":  # if chat is private, add special button to add bot to a group
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        link_add = f"https://t.me/{bot_username}?startgroup=me&admin=change_info+restrict_members+delete_messages+pin_messages+invite_users"
        markup.add(types.InlineKeyboardButton(text="Add bot to a group", url=link_add))

    help_text = (f"Hey {user_name}! Ready to play? Here are the commands you can use:\n\n"
                 f"/iqup or /iq - Start a game to boost your IQ!\n"
                 f"/help - Need help? Use this to see the command list again.\n"
                 f"/profile - Check out your profile and stats.\n"
                 f"/status - Update your status message.\n"
                 f"/top - See the leaderboard of the top 10 players.\n"
                 f"/chat_top - View the leaderboard for the top 10 chats.\n"
                 f"/remake - Reset the game data for this chat (requires admin permissions).\n\n"
                 f"Quick tip: Most commands work only when you use them in a group chat!")
    await bot.send_message(chat_id, help_text, reply_markup=markup)


async def new_members_message(message):
    bot_info = await bot.get_me()
    bot_username = bot_info.username  # bot gets his username

    new_members = [zzz.id for zzz in message.new_chat_members]

    if bot_username not in new_members:  # if the bot wasn't the one just added
        return

    chat_id = message.chat.id
    chat_name = message.chat.title

    create_chat_table(chat_id)
    add_chat_to_table(chat_id, chat_name)

    with open("iq.png", "rb") as f:
        photo = f.read()
    text = (f"Hello {chat_name}! I appreciate you adding me to the group.\n"
               f"This is a straightforward IQ game... unfortunately, the IQ points are just part of the game and won't affect your real-life intelligence..\n"
               f"To give the IQ game a try, use the /iq command, and for a list of commands, please use /help.")

    await bot.send_photo(chat_id, photo, caption=text)


@bot.message_handler(commands=["iqup", "iq"])
async def iq_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if message.chat.type == "private":
        await bot.send_message(chat_id, "This command works only in groups")
        return

    new_user(user_id, chat_id, user_name)
    c.execute(f"""SELECT use FROM '{chat_id * -1}' WHERE user_id = '{user_id}'""")
    use_flag = bool(c.fetchone()[0])
    seconds = seconds_until_next_hour()
    if use_flag:
        await bot.send_message(chat_id, f"You've played in this chat before. Next game will be available in {seconds // 60 % 60} minutes and {seconds % 60} seconds.")
        return

    delta, total_iq = update_iq(user_id, chat_id)
    text = f"{user_name}, your current IQ: {total_iq}.\n\n"
    if delta > 0:
        text += random.choice(good_actions)
        text += f" and after that, your IQ has been increased by {delta} points."
    elif delta < 0:
        text += random.choice(bad_actions)
        text += f" and after that, your IQ dropped by {-delta} points"
    else:
        text += random.choice(neutral_actions)
        text += ". Nothing has changed"

    update_chat_iq_count(chat_id)
    await bot.send_message(chat_id, text)



@bot.message_handler(commands=["remake"])
async def remake_command(message):
    if message.chat.type == 'private':
        return
    admins = await bot.get_chat_administrators(message.chat.id)
    admin_ids = [admin.user.id for admin in admins]

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in admin_ids:
        await bot.send_message(message.chat.id, "You don't have permission to this command")
        return

    remake(chat_id)
    update_chat_iq_count(chat_id)
    await bot.send_message(chat_id, "Chat data has been deleted")


@bot.message_handler(commands=['top'])
async def top_command(message):
    total_iq = 0
    chat_id = message.chat.id
    safe_chat_id = -1 * chat_id
    c.execute(f"""SELECT user_id, total_iq, user_name FROM '{safe_chat_id}' ORDER BY total_iq DESC""")
    all_users = c.fetchall()
    top_users = all_users[:10]

    top_message = f"🤓 Top <s>dummies</s> smartest 🤓:\n\n"
    for user_id, delta, user_name in top_users:
        user = create_user_link(user_id, user_name)
        top_message += f"{user}, IQ: {delta}\n"
        total_iq += delta
    top_message += f"\nTotal chat's IQ: {total_iq}\n"

    with open("top.png", "rb") as f:
        photo = f.read()

    await bot.send_photo(message.chat.id, caption=top_message, photo=photo, parse_mode="HTML")


@bot.message_handler(commands=["chat_top"])
async def chat_top(message):
    top_message = f"🤓 Top <s>Derp</s> Genius Chats 🤓:\n\n"
    c.execute(f"""SELECT chat_id, chat_name FROM chats ORDER BY iq_count DESC""")
    all_chats = c.fetchall()
    top_chats = all_chats[:10]

    for chat_id, chat_name in top_chats:
        total_iq = update_chat_iq_count(chat_id)

        top_message += f"{chat_name}, total chat's IQ: {total_iq}\n"

    c.execute("""SELECT iq_count FROM chats""")
    iq_from_all_chats = [int(row[0]) for row in c.fetchall()]
    iq_from_all_chats = sum(iq_from_all_chats)

    top_message += f"\nTotal IQ of all chats: {iq_from_all_chats}"

    with open("chat_top.png", "rb") as f:
        photo = f.read()

    await bot.send_photo(message.chat.id, photo=photo, caption=top_message, parse_mode="HTML")





@bot.message_handler(commands=['status'])
async def set_status(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    if len(message.text.split(' ')) == 1:
        status = get_status(user_id, chat_id, user_name)
        top_message = (f"Your current status:\n\n{status}\n\n"
                          f"To change it, use the command like this: /status <Your New Status>")
        await bot.send_message(chat_id, top_message)
        return

    new_status = str(' '.join(message.text.split(' ')[1:]))
    set_new_status(user_id, chat_id, new_status)
    top_message = f"{user_name}, your new status in profile: \n\n{new_status}"

    await bot.send_message(chat_id, top_message)


@bot.message_handler(commands=["profile"])
async def profile_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if message.chat.type == "private":
        await bot.send_message(chat_id, "This command only works in groups")
        return

    new_user(user_id, chat_id, user_name)
    c.execute(f"""SELECT total_iq, best_iq, status FROM '{chat_id * -1}' WHERE user_id = '{user_id}'""")
    total_iq, best_iq, status = c.fetchone()

    status = status.capitalize()
    fun_facts = [
        "IQ is just a number. In reality, you're a fucking idiot.",
        "Increasing your IQ might lead to an increase in your chromosome count.",
        "The higher your IQ, the... fuck all it means."
    ]

    fun_fact = random.choice(fun_facts)

    profile_text = (f"Hi, {create_user_link(user_id, user_name)}!\n\n"
                       f"Your profile:\n\n"
                       f"Current IQ: {total_iq}\n"
                       f"Best IQ: {best_iq}\n"
                       f"Status: {status}\n\n"
                       f"{fun_fact}")
    await bot.send_message(chat_id, profile_text, parse_mode="HTML")


async def timer():
    while True:
        seconds = seconds_until_next_hour()
        await asyncio.sleep(seconds)
        
        c.execute("SELECT chat_id FROM chats")
        all_tables = c.fetchall()
        safe_chat_ids = [int(row[0]) * -1 for row in all_tables]

        for name in safe_chat_ids:
            c.execute(f"""UPDATE '{name}' SET use = 0""")
            conn.commit()



async def main():
    main_create_tables()

    commands = [
        types.BotCommand("iq", "Boost IQ"),
        types.BotCommand("status", "Change status"),
        types.BotCommand("profile", "View profile"),
        types.BotCommand("remake", "Reset chat data"),
        types.BotCommand("top", "Chat leaderboard"),
        types.BotCommand("chat_top", "Top chats ranking"),
        types.BotCommand("help", "Help"),
    ]

    await bot.set_my_commands(commands)

    asyncio.create_task(timer())
    await bot.polling(none_stop=True)


if __name__ == "__main__":
    asyncio.run(main())