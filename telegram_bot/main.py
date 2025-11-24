import asyncio
import sqlite3
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ============ НАСТРОЙКИ ============
TOKEN = "8467556633:AAFwl2sXSzq-3SCSHfp0TCSr4vbduIHOOlU"
LANGS = {
    "RU": {
        "name": "🇷🇺 Русский",
        "welcome": "Добро пожаловать в Vet Helper!",
        "main_menu": "Главное меню",
        "symptom_check": "🩺 Проверка симптомов",
        "find_clinics": "📍 Поиск клиник и аптек",
        "reminders": "📅 Напоминания",
        "profile": "👤 Мой профиль",
        "change_lang": "🌐 Изменить язык",
        "back": "🔙 Назад",
        "add_reminder": "➕ Добавить напоминание",
        "list_reminders": "📋 Список напоминаний",
        "enter_owner": "Введите имя владельца:",
        "enter_phone": "Введите номер телефона:",
        "enter_city": "Введите город:",
        "enter_pet_name": "Имя питомца:",
        "enter_pet_type": "Вид животного (собака, кошка и т.д.):",
        "enter_breed": "Порода:",
        "enter_age": "Возраст:",
        "enter_weight": "Вес:",
        "enter_color": "Окрас:",
        "enter_allergies": "Аллергии:",
        "enter_chronic": "Хронические болезни:",
        "profile_saved": "✅ Профиль сохранён!",
        "reminder_text": "Введите текст напоминания:",
        "reminder_time": "Введите дату и время (в формате ГГГГ-ММ-ДД ЧЧ:ММ):",
        "invalid_time": "❌ Неверный формат! Пример: 2025-08-12 14:30",
        "future_time": "❌ Укажите время в будущем!",
        "reminder_added": "✅ Напоминание добавлено!",
        "no_reminders": "📭 У вас нет напоминаний.",
        "reminders_list": "Ваши напоминания:\n\n",
        "reminder_menu": "Меню напоминаний:",
        "profile_exists": "Ваш профиль уже заполнен.",
        "profile_title": "🐾 Ваш профиль:\n",
        "reminder_notification": "⏰ Напоминание:"
    },
    "UZ": {
        "name": "🇺🇿 O‘zbek",
        "welcome": "Vet Helper ga xush kelibsiz!",
        "main_menu": "Asosiy menyu",
        "symptom_check": "🩺 Alomatlarni tekshirish",
        "find_clinics": "📍 Klinika va dorixonalarni qidirish",
        "reminders": "📅 Eslatmalar",
        "profile": "👤 Mening profilim",
        "change_lang": "🌐 Tilni o'zgartirish",
        "back": "🔙 Orqaga",
        "add_reminder": "➕ Eslatma qo'shish",
        "list_reminders": "📋 Eslatmalar ro'yxati",
        "enter_owner": "Egasi ismini kiriting:",
        "enter_phone": "Telefon raqamini kiriting:",
        "enter_city": "Shaharni kiriting:",
        "enter_pet_name": "Hayvonning ismi:",
        "enter_pet_type": "Hayvon turi (kuchuk, mushuk va h.k.):",
        "enter_breed": "Zoti:",
        "enter_age": "Yoshi:",
        "enter_weight": "Vazni:",
        "enter_color": "Rangi:",
        "enter_allergies": "Allergiyalar:",
        "enter_chronic": "Surunkali kasalliklar:",
        "profile_saved": "✅ Profil saqlandi!",
        "reminder_text": "Eslatma matnini kiriting:",
        "reminder_time": "Vaqtni kiriting (YYYY-AA-KK SS:DD formatida):",
        "invalid_time": "❌ Noto'g'ri format! Misol: 2025-08-12 14:30",
        "future_time": "❌ Kelajakdagi vaqtni kiriting!",
        "reminder_added": "✅ Eslatma qo'shildi!",
        "no_reminders": "📭 Sizda eslatmalar yo'q.",
        "reminders_list": "Sizning eslatmalaringiz:\n\n",
        "reminder_menu": "Eslatmalar menyusi:",
        "profile_exists": "Profilingiz allaqachon to'ldirilgan.",
        "profile_title": "🐾 Sizning profilingiz:\n",
        "reminder_notification": "⏰ Eslatma:"
    },
    "EN": {
        "name": "🇬🇧 English",
        "welcome": "Welcome to Vet Helper!",
        "main_menu": "Main menu",
        "symptom_check": "🩺 Symptom check",
        "find_clinics": "📍 Find clinics and pharmacies",
        "reminders": "📅 Reminders",
        "profile": "👤 My profile",
        "change_lang": "🌐 Change language",
        "back": "🔙 Back",
        "add_reminder": "➕ Add reminder",
        "list_reminders": "📋 List of reminders",
        "enter_owner": "Enter owner name:",
        "enter_phone": "Enter phone number:",
        "enter_city": "Enter city:",
        "enter_pet_name": "Pet name:",
        "enter_pet_type": "Animal type (dog, cat, etc.):",
        "enter_breed": "Breed:",
        "enter_age": "Age:",
        "enter_weight": "Weight:",
        "enter_color": "Color:",
        "enter_allergies": "Allergies:",
        "enter_chronic": "Chronic diseases:",
        "profile_saved": "✅ Profile saved!",
        "reminder_text": "Enter reminder text:",
        "reminder_time": "Enter date and time (YYYY-MM-DD HH:MM format):",
        "invalid_time": "❌ Invalid format! Example: 2025-08-12 14:30",
        "future_time": "❌ Please enter future time!",
        "reminder_added": "✅ Reminder added!",
        "no_reminders": "📭 You have no reminders.",
        "reminders_list": "Your reminders:\n\n",
        "reminder_menu": "Reminders menu:",
        "profile_exists": "Your profile is already filled.",
        "profile_title": "🐾 Your profile:\n",
        "reminder_notification": "⏰ Reminder:"
    }
}

# База данных
conn = sqlite3.connect("bot_data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS profiles
               (
                   user_id
                   INTEGER
                   PRIMARY
                   KEY,
                   owner_name
                   TEXT,
                   phone
                   TEXT,
                   city
                   TEXT,
                   pet_name
                   TEXT,
                   pet_type
                   TEXT,
                   breed
                   TEXT,
                   age
                   TEXT,
                   weight
                   TEXT,
                   color
                   TEXT,
                   allergies
                   TEXT,
                   chronic
                   TEXT,
                   lang
                   TEXT
               )
               """)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS reminders
               (
                   id
                   INTEGER
                   PRIMARY
                   KEY
                   AUTOINCREMENT,
                   user_id
                   INTEGER,
                   text
                   TEXT,
                   remind_time
                   TEXT
               )
               """)

conn.commit()

try:
    cursor.execute("ALTER TABLE profiles ADD COLUMN lang TEXT")
    conn.commit()
except sqlite3.OperationalError as e:
        print(f"Lang column already exists: {e}")

# ============ FSM ============
class ProfileForm(StatesGroup):
    owner_name = State()
    phone = State()
    city = State()
    pet_name = State()
    pet_type = State()
    breed = State()
    age = State()
    weight = State()
    color = State()
    allergies = State()
    chronic = State()


class ReminderForm(StatesGroup):
    text = State()
    date_time = State()


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============
def get_user_lang(user_id):
    cursor.execute("SELECT lang FROM profiles WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else "RU"


def get_text(user_id, key):
    lang = get_user_lang(user_id)
    return LANGS[lang].get(key, key)


def main_menu(user_id):
    lang = get_user_lang(user_id)
    kb = [
        [KeyboardButton(text=LANGS[lang]["symptom_check"])],
        [KeyboardButton(text=LANGS[lang]["find_clinics"])],
        [KeyboardButton(text=LANGS[lang]["reminders"])],
        [
            KeyboardButton(text=LANGS[lang]["profile"]),
            KeyboardButton(text=LANGS[lang]["change_lang"])
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def back_btn(user_id):
    lang = get_user_lang(user_id)
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=LANGS[lang]["back"])]], resize_keyboard=True)


def reminders_menu(user_id):
    lang = get_user_lang(user_id)
    kb = [
        [KeyboardButton(text=LANGS[lang]["add_reminder"])],
        [KeyboardButton(text=LANGS[lang]["list_reminders"])],
        [KeyboardButton(text=LANGS[lang]["back"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# ============ БОТ ============
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ======= Обработчики команд =======
# ============ Start handlerini yangilash ============
@dp.message(Command("start"))
async def start(message: types.Message):
    # Foydalanuvchi bazada bormi?
    cursor.execute("SELECT lang FROM profiles WHERE user_id=?", (message.from_user.id,))
    row = cursor.fetchone()

    if row:
        # Agar profil mavjud bo'lsa, asosiy menyuni ko'rsat
        lang_code = row[0]
        welcome_text = LANGS[lang_code]["welcome"]
        await message.answer(f"✅ {welcome_text}", reply_markup=main_menu(message.from_user.id))
    else:
        # Agar profil mavjud bo'lmasa, til tanlash menyusini ko'rsat
        buttons = []
        for lang_code in LANGS:
            buttons.append([KeyboardButton(text=LANGS[lang_code]["name"])])

        kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("🌍 Выберите язык / Tilni tanlang / Choose language:", reply_markup=kb)


# ============ Tilni saqlash funksiyasini yangilash ============
@dp.message(lambda m: any(m.text == LANGS[lang]["name"] for lang in LANGS))
async def set_language(message: types.Message):
    lang_code = None
    for code, lang_data in LANGS.items():
        if lang_data["name"] == message.text:
            lang_code = code
            break

    if not lang_code:
        await message.answer("❌ Language not recognized")
        return

    # Yangi tilni saqlash
    cursor.execute("""
        INSERT OR REPLACE INTO profiles (user_id, lang) 
        VALUES (?, ?)
    """, (message.from_user.id, lang_code))
    conn.commit()

    welcome_text = LANGS[lang_code]["welcome"]
    await message.answer(
        f"✅ {welcome_text}\n"
        f"🌐 {get_text(message.from_user.id, 'change_lang')}",
        reply_markup=main_menu(message.from_user.id)
    )

@dp.message(lambda m: m.text in [LANGS[lang]["back"] for lang in LANGS])
async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()

    await message.answer(
        get_text(message.from_user.id, "main_menu"),
        reply_markup=main_menu(message.from_user.id)
    )


# ============ Tilni o'zgartirish handleri ============
@dp.message(lambda m: m.text in [LANGS[lang]["change_lang"] for lang in LANGS])
async def change_language_start(message: types.Message):
    buttons = []
    for lang_code in LANGS:
        buttons.append([KeyboardButton(text=LANGS[lang_code]["name"])])

    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("🌍 Выберите язык / Tilni tanlang / Choose language:", reply_markup=kb)

# ======= Профиль =======
@dp.message(lambda m: m.text in [LANGS[lang]["profile"] for lang in LANGS])
async def profile_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,))
    profile = cursor.fetchone()

    if profile and all(profile[1:12]):  # Проверяем, заполнен ли профиль
        profile_text = (
            f"{get_text(user_id, 'profile_title')}"
            f"👤 {get_text(user_id, 'enter_owner')} {profile[1]}\n"
            f"📞 {get_text(user_id, 'enter_phone')} {profile[2]}\n"
            f"🏙️ {get_text(user_id, 'enter_city')} {profile[3]}\n"
            f"🐶 {get_text(user_id, 'enter_pet_name')} {profile[4]}\n"
            f"🔬 {get_text(user_id, 'enter_pet_type')} {profile[5]}\n"
            f"🎯 {get_text(user_id, 'enter_breed')} {profile[6]}\n"
            f"⏳ {get_text(user_id, 'enter_age')} {profile[7]}\n"
            f"⚖️ {get_text(user_id, 'enter_weight')} {profile[8]}\n"
            f"🎨 {get_text(user_id, 'enter_color')} {profile[9]}\n"
            f"⚠️ {get_text(user_id, 'enter_allergies')} {profile[10]}\n"
            f"💊 {get_text(user_id, 'enter_chronic')} {profile[11]}"
        )
        await message.answer(profile_text, reply_markup=main_menu(user_id))
    else:
        await message.answer(
            get_text(user_id, "enter_owner"),
            reply_markup=back_btn(user_id)
        )
        await state.set_state(ProfileForm.owner_name)


# Остальные шаги профиля с обработкой языка
@dp.message(ProfileForm.owner_name)
async def set_owner_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(owner_name=message.text)
    await state.set_state(ProfileForm.phone)
    await message.answer(get_text(user_id, "enter_phone"))


@dp.message(ProfileForm.phone)
async def set_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(phone=message.text)
    await state.set_state(ProfileForm.city)
    await message.answer(get_text(user_id, "enter_city"))


@dp.message(ProfileForm.city)
async def set_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(city=message.text)
    await state.set_state(ProfileForm.pet_name)
    await message.answer(get_text(user_id, "enter_pet_name"))


@dp.message(ProfileForm.pet_name)
async def set_pet_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(pet_name=message.text)
    await state.set_state(ProfileForm.pet_type)
    await message.answer(get_text(user_id, "enter_pet_type"))


@dp.message(ProfileForm.pet_type)
async def set_pet_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(pet_type=message.text)
    await state.set_state(ProfileForm.breed)
    await message.answer(get_text(user_id, "enter_breed"))


@dp.message(ProfileForm.breed)
async def set_breed(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(breed=message.text)
    await state.set_state(ProfileForm.age)
    await message.answer(get_text(user_id, "enter_age"))


@dp.message(ProfileForm.age)
async def set_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(age=message.text)
    await state.set_state(ProfileForm.weight)
    await message.answer(get_text(user_id, "enter_weight"))


@dp.message(ProfileForm.weight)
async def set_weight(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(weight=message.text)
    await state.set_state(ProfileForm.color)
    await message.answer(get_text(user_id, "enter_color"))


@dp.message(ProfileForm.color)
async def set_color(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(color=message.text)
    await state.set_state(ProfileForm.allergies)
    await message.answer(get_text(user_id, "enter_allergies"))


@dp.message(ProfileForm.allergies)
async def set_allergies(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(allergies=message.text)
    await state.set_state(ProfileForm.chronic)
    await message.answer(get_text(user_id, "enter_chronic"))


@dp.message(ProfileForm.chronic)
async def set_chronic(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    data = await state.get_data()
    lang = get_user_lang(user_id)

    cursor.execute("""
        INSERT OR REPLACE INTO profiles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id,
        data.get('owner_name', ''),
        data.get('phone', ''),
        data.get('city', ''),
        data.get('pet_name', ''),
        data.get('pet_type', ''),
        data.get('breed', ''),
        data.get('age', ''),
        data.get('weight', ''),
        data.get('color', ''),
        data.get('allergies', ''),
        message.text,
        lang
    ))
    conn.commit()
    await state.clear()
    await message.answer(
        get_text(user_id, "profile_saved"),
        reply_markup=main_menu(user_id)
    )


# ======= Напоминания =======
@dp.message(lambda m: m.text in [LANGS[lang]["reminders"] for lang in LANGS])
async def reminders_start(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        get_text(user_id, "reminder_menu"),
        reply_markup=reminders_menu(user_id)
    )


@dp.message(lambda m: m.text in [LANGS[lang]["add_reminder"] for lang in LANGS])
async def reminder_add_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(ReminderForm.text)
    await message.answer(
        get_text(user_id, "reminder_text"),
        reply_markup=back_btn(user_id)
    )


@dp.message(ReminderForm.text)
async def reminder_set_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    await state.update_data(text=message.text)
    await state.set_state(ReminderForm.date_time)
    await message.answer(get_text(user_id, "reminder_time"))


@dp.message(ReminderForm.date_time)
async def reminder_set_time(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == get_text(user_id, "back"):
        await back_handler(message, state)
        return

    try:
        remind_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        if remind_time <= datetime.now():
            await message.answer(get_text(user_id, "future_time"))
            return
    except ValueError:
        await message.answer(get_text(user_id, "invalid_time"))
        return

    data = await state.get_data()
    cursor.execute(
        "INSERT INTO reminders (user_id, text, remind_time) VALUES (?,?,?)",
        (user_id, data['text'], message.text)
    )
    conn.commit()
    await state.clear()
    await message.answer(
        get_text(user_id, "reminder_added"),
        reply_markup=main_menu(user_id)
    )


@dp.message(lambda m: m.text in [LANGS[lang]["list_reminders"] for lang in LANGS])
async def reminder_list(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT text, remind_time FROM reminders WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        await message.answer(get_text(user_id, "no_reminders"))
    else:
        txt = "\n".join([f"📌 {t} — {tm}" for t, tm in rows])
        await message.answer(f"{get_text(user_id, 'reminders_list')}{txt}")


# ======= Проверка напоминаний =======
async def check_reminders():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("SELECT id, user_id, text FROM reminders WHERE remind_time=?", (now,))
        for rid, uid, text in cursor.fetchall():
            try:
                await bot.send_message(uid, f"{get_text(uid, 'reminder_notification')} {text}")
                cursor.execute("DELETE FROM reminders WHERE id=?", (rid,))
                conn.commit()
            except Exception as e:
                logging.error(f"Reminder error: {e}")
        await asyncio.sleep(60)


# ======= Запуск и завершение =======
async def on_startup():
    asyncio.create_task(check_reminders())


async def on_shutdown():
    conn.close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())