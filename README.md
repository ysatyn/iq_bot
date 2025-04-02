# IQ_Bot
A simple bot for boosting IQ in chats.

## Description
An uncomplicated project designed for entertainment in chats. Most of the bot's logic is intended for operating within chat groups. The core idea is to allow users to boost their IQ using a special command once per hour. **The code includes detailed comments to help understand its structure and functionality.**

Dependencies:
*   `pyTelegramBotAPI` (telebot)
*   `asyncio`
*   `sqlite`

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ysatyn/iq_bot.git
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your bot token:
    *   Create a file named `.env` in the project's root directory.
    *   Obtain your bot token from [BotFather on Telegram](https://t.me/BotFather).
    *   Inside the `.env` file, add the following line, placing your actual token between the quotation marks:
```env
        BOT_TOKEN="YOUR_TOKEN_HERE"
```
4.  Run the bot:
    ```bash
    python main.py
    ```

Enjoy!
        

