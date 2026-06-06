# Cordial Help Bot

Telegram bot for Cordial Care partner and PVZ support.

## Features
- Main menu in Telegram
- Categories: orders, bonuses, registration, delivery, PVZ, documents, products, training
- Collects request text from partner
- Sends request to the right office department group
- Sends confirmation to partner
- Basic FAQ answers

## Setup
1. Create bot in Telegram via @BotFather and copy token.
2. Rename `.env.example` to `.env`.
3. Paste `BOT_TOKEN`.
4. Create office department Telegram groups.
5. Add the bot to every group and make it admin.
6. Get each group chat_id and paste it into `.env`.
7. Install Python 3.11+.
8. Run:

```bash
pip install -r requirements.txt
python main.py
```

## How to get group chat_id
Add @userinfobot or temporarily print message.chat.id in bot logs. Group IDs usually start with -100.
