import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Вставьте ваш токен от @BotFather в кавычках ниже
BOT_TOKEN = "ВАШ_ТОКЕН_ИЗ_BOTFATHER"

logging.basicConfig(level=logging.INFO)
bot = Bot(8813865534:AAHiQhPlXvz-RMwB3bZjLmK90DoLg7WQIx0)
dp = Dispatcher()

games = {}

def get_game_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ +1 Приду", callback_data="join_game")
    builder.button(text="❌ -1 Не смогу", callback_data="leave_game")
    builder.adjust(2)
    return builder.as_markup()

def format_game_text(info_text: str, players: list) -> str:
    text = f"⚽ **СБОР НА ФУТБОЛ**\n\n📍 **Детали:** {info_text}\n\n👥 **Записались ({len(players)}):**\n"
    if not players:
        text += "_Пока никто не записался._"
    else:
        for idx, player in enumerate(players, 1):
            text += f"{idx}. {player['name']}\n"
    return text

@dp.message(Command("match"))
async def cmd_create_match(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Укажите время и место.\nПример: `/match Пятница, 20:00 | Стадион`", parse_mode="Markdown")
        return
    info_text = args[1]
    players = []
    msg_text = format_game_text(info_text, players)
    sent_message = await message.answer(msg_text, reply_markup=get_game_keyboard(), parse_mode="Markdown")
    games[sent_message.message_id] = {"info": info_text, "players": players}

@dp.callback_query(F.data == "join_game")
async def process_join(callback: types.CallbackQuery):
    msg_id = callback.message.message_id
    if msg_id not in games:
        await callback.answer("Запись неактивна.", show_alert=True)
        return
    game = games[msg_id]
    user = callback.from_user
    if any(p["id"] == user.id for p in game["players"]):
        await callback.answer("Вы уже в списке!", show_alert=True)
        return
    game["players"].append({"id": user.id, "name": user.full_name})
    new_text = format_game_text(game["info"], game["players"])
    await callback.message.edit_text(new_text, reply_markup=get_game_keyboard(), parse_mode="Markdown")
    await callback.answer("Вы записались!")

@dp.callback_query(F.data == "leave_game")
async def process_leave(callback: types.CallbackQuery):
    msg_id = callback.message.message_id
    if msg_id not in games:
        await callback.answer("Запись неактивна.", show_alert=True)
        return
    game = games[msg_id]
    user = callback.from_user
    if not any(p["id"] == user.id for p in game["players"]):
        await callback.answer("Вас нет в списке.", show_alert=True)
        return
    game["players"] = [p for p in game["players"] if p["id"] != user.id]
    new_text = format_game_text(game["info"], game["players"])
    await callback.message.edit_text(new_text, reply_markup=get_game_keyboard(), parse_mode="Markdown")
    await callback.answer("Вы удалены из списка.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
