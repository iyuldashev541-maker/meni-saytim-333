import os, io, asyncio, re
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile, WebAppInfo, ContentType

# Bot sozlamalari
TOKEN = "SIZNING_BOT_TOKENINGIZ"
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
user_data = {}


class ExpenseState(StatesGroup):
    waiting_for_amount = State()


# --- KLAVIATURA ---
def main_keyboard():
    # Sayt manzilingizni tekshirib yozing!
    url = "https://satim-eight.vercel.app"
    kb = [
        [KeyboardButton(text="🚀 Launcherni ochish", web_app=WebAppInfo(url=url))],
        [KeyboardButton(text="📊 Statistika")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# --- DIAGRAMMA ---
def create_chart(data):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=140,
           textprops={'color': "black", 'weight': 'bold'})
    plt.title("💰 Xarajatlar")
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='white')
    buf.seek(0)
    return buf


# --- HANDLERLAR ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Xarajatlarni kiritish uchun Launcherni oching.", reply_markup=main_keyboard())


@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def get_data(m: types.Message, state: FSMContext):
    cat = m.web_app_data.data
    await state.update_data(c=cat)
    await m.answer(f"📂 {cat} tanlandi. Miqdorni yozing (masalan: 15000):")
    await state.set_state(ExpenseState.waiting_for_amount)


@dp.message(ExpenseState.waiting_for_amount)
async def save_amount(m: types.Message, state: FSMContext):
    num = re.search(r'\d+', m.text)
    if not num: return await m.answer("Faqat raqam yozing!")

    data = await state.get_data()
    uid, cat, val = m.from_user.id, data['c'], int(num.group())

    if uid not in user_data: user_data[uid] = {}
    user_data[uid][cat] = user_data[uid].get(cat, 0) + val

    await state.clear()
    await m.answer(f"✅ Saqlandi: {val:,} so'm", reply_markup=main_keyboard())


@dp.message(F.text == "📊 Statistika")
async def stats(m: types.Message):
    uid = m.from_user.id
    if uid not in user_data: return await m.answer("Hali ma'lumot yo'q.")
    chart = create_chart(user_data[uid])
    await m.answer_photo(BufferedInputFile(chart.read(), filename="s.png"), caption="Sizning tahlilingiz")


async def main(): await dp.start_polling(bot)


if __name__ == '__main__': asyncio.run(main())