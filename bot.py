import os
import asyncio
import logging
from anthropic import Anthropic
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Anthropic(api_key=ANTHROPIC_API_KEY)
conversation_history = {}

SYSTEM_PROMPT = """Ты личный рабочий ассистент. Помогаешь с анализом документов, коммерческих предложений, составлением писем, финансовыми расчётами и планированием задач. Отвечай чётко и по делу на русском языке."""

@dp.message(CommandStart())
async def start(message: types.Message):
    conversation_history[message.from_user.id] = []
    await message.answer("👋 Привет! Я твой личный рабочий ассистент.\n\nМогу помочь с:\n📄 Анализом документов и КП\n📊 Финансовыми расчётами\n✍️ Письмами и текстами\n📋 Планированием задач\n\nНапиши свой вопрос!")

@dp.message(Command("clear"))
async def clear(message: types.Message):
    conversation_history[message.from_user.id] = []
    await message.answer("🗑️ История очищена!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": "user", "content": message.text})
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = client.messages.create(
            model=os.environ.get("MODEL_NAME", "claude-sonnet-4-5"),
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=conversation_history[user_id]
        )
        reply = response.content[0].text
        conversation_history[user_id].append({"role": "assistant", "content": reply})
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                await message.answer(reply[i:i+4000])
        else:
            await message.answer(reply)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
