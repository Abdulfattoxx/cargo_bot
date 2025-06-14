import logging
import json
import aiofiles
import asyncio
import time
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router
from aiogram.client.default import DefaultBotProperties

API_TOKEN = "8062759797:AAHbkfPHvkOmYJDCVugcfWw1c7FpJSOdBeY"
ADMIN_IDS = [6950346918]
GROUP_IDS = [-1002658308062, -1002688780911, -1002273042338]
USER_DB = "users.json"
ORDERS_DB = "orders.json"

regions_data = {
    "Toshkent": [
        "Bektemir", "Chilonzor", "Mirobod", "Mirzo Ulug‘bek", "Olmazor", "Sergeli",
        "Shayxontohur", "Uchtepa", "Yakkasaroy", "Yashnobod", "Yunusobod"
    ],
    "Toshkent viloyati": [
        "Bekobod", "Bo‘ka", "Bo‘stonliq", "Chinoz", "Qibray", "Ohangaron", "Olmaliq",
        "Oqqo‘rg‘on", "Parkent", "Piskent", "Quyichirchiq", "Yangiyo‘l", "Zangiota"
    ],
    "Andijon": [
        "Andijon sh.", "Asaka", "Baliqchi", "Bo‘z", "Buloqboshi", "Izboskan", "Jalaquduq",
        "Marhamat", "Oltinko‘l", "Paxtaobod", "Shahrixon", "Ulug‘nor", "Xo‘jaobod"
    ],
    "Farg‘ona": [
        "Farg‘ona sh.", "Beshariq", "Bog‘dod", "Buvayda", "Dang‘ara", "Furqat", "Qo‘qon",
        "Quva", "Quvasoy", "Rishton", "So‘x", "Toshloq", "Uchko‘prik", "Yozyovon"
    ],
    "Namangan": [
        "Namangan sh.", "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Norin", "Pop",
        "To‘raqo‘rg‘on", "Uchqo‘rg‘on", "Uychi", "Yangiqo‘rg‘on"
    ],
    "Samarqand": [
        "Samarqand sh.", "Bulung‘ur", "Ishtixon", "Jomboy", "Kattaqo‘rg‘on", "Narpay",
        "Oqdaryo", "Paxtachi", "Payariq", "Pastdarg‘om", "Tayloq", "Urgut"
    ],
    "Buxoro": [
        "Buxoro sh.", "G‘ijduvon", "Jondor", "Kogon", "Olot", "Peshku", "Qorako‘l",
        "Qorovulbozor", "Romitan", "Shofirkon", "Vobkent"
    ],
    "Qashqadaryo": [
        "Qarshi sh.", "Chiroqchi", "Dehqonobod", "G‘uzor", "Kasbi", "Kitob", "Koson",
        "Mirishkor", "Muborak", "Nishon", "Shahrisabz", "Yakkabog‘"
    ],
    "Surxondaryo": [
        "Termiz sh.", "Angor", "Bandixon", "Boysun", "Denov", "Jarqo‘rg‘on", "Qiziriq",
        "Qumqo‘rg‘on", "Muzrabot", "Oltinsoy", "Sariosiyo", "Sherobod", "Sho‘rchi"
    ],
    "Jizzax": [
        "Jizzax sh.", "Arnasoy", "Baxmal", "Do‘stlik", "Forish", "G‘allaorol", "Mirzacho‘l",
        "Paxtakor", "Yangiobod", "Zafarobod", "Zarbdor", "Zomin", "Sharof Rashidov"
    ],
    "Sirdaryo": [
        "Guliston sh.", "Akaltyn", "Boyovut", "Guliston", "Mirzaobod", "Oqoltin",
        "Sayxunobod", "Sardoba", "Sirdaryo", "Xovos", "Yangier", "Shirin"
    ],
    "Navoiy": [
        "Navoiy sh.", "Karmana", "Qiziltepa", "Konimex", "Navbahor", "Nurota", "Tomdi",
        "Uchquduq", "Xatirchi", "Zarafshon"
    ],
    "Xorazm": [
        "Urganch sh.", "Bog‘ot", "Gurlan", "Hazorasp", "Khiva", "Qo‘shko‘pir", "Shovot",
        "Urganch", "Xonqa", "Yangiariq", "Yangibozor"
    ],
    "Qoraqalpog‘iston": [
        "Nukus sh.", "Amudaryo", "Beruniy", "Chimboy", "Ellikqal‘a", "Kegeyli", "Mo‘ynoq",
        "Qanliko‘l", "Qorao‘zak", "Qo‘ng‘irot", "Shumanay", "Taxtako‘pir", "To‘rtko‘l",
        "Xo‘jayli"
    ]
}

cargo_types = [
    "Meva-sabzavot", "Maishiy texnika", "Kiyim-kechak", "Qurilish mollari",
    "Kitob", "Mebel", "Elektronika", "Boshqa", "Tashlab ketish"
]

def cargo_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ct) for ct in cargo_types[:3]],
            [KeyboardButton(text=ct) for ct in cargo_types[3:6]],
            [KeyboardButton(text=ct) for ct in cargo_types[6:8]],
            [KeyboardButton(text="Boshqa"), KeyboardButton(text="Tashlab ketish")]
        ],
        resize_keyboard=True
    )

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Yana yuk qo‘shish")],
            [KeyboardButton(text="📦 Mening buyurtmalarim")],
            [KeyboardButton(text="👨‍💻 Admin panel")],
            [KeyboardButton(text="🚪 Chiqish")]
        ],
        resize_keyboard=True
    )

def make_inline_keyboard(options, prefix):
    kb = InlineKeyboardBuilder()
    for opt in list(options):
        kb.button(text=opt, callback_data=f"{prefix}:{opt}")
    kb.adjust(1)
    return kb.as_markup()

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class CargoForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_cargo_type = State()
    waiting_for_weight = State()
    waiting_for_size = State()
    waiting_for_comment = State()
    waiting_for_comment_text = State()
    from_region = State()
    from_district = State()
    to_region = State()
    to_district = State()
    ask_photo = State()
    cargo_image = State()
    edit_field = State()
    edit_value = State()

async def save_user_data(user_id, data):
    try:
        async with aiofiles.open(USER_DB, 'r') as f:
            content = await f.read()
            users = json.loads(content) if content else {}
    except FileNotFoundError:
        users = {}
    except Exception:
        users = {}
    users[str(user_id)] = data
    async with aiofiles.open(USER_DB, 'w') as f:
        await f.write(json.dumps(users, indent=4))

async def get_user_data(user_id):
    try:
        async with aiofiles.open(USER_DB, 'r') as f:
            content = await f.read()
            users = json.loads(content) if content else {}
            return users.get(str(user_id))
    except Exception:
        return None

async def save_order(order):
    try:
        async with aiofiles.open(ORDERS_DB, 'r') as f:
            content = await f.read()
            orders = json.loads(content) if content else []
    except FileNotFoundError:
        orders = []
    except Exception:
        orders = []
    orders.append(order)
    async with aiofiles.open(ORDERS_DB, 'w') as f:
        await f.write(json.dumps(orders, indent=4))

async def get_orders():
    try:
        async with aiofiles.open(ORDERS_DB, 'r') as f:
            content = await f.read()
            orders = json.loads(content) if content else []
            return orders
    except Exception:
        return []

user_last_order_time = {}

def order_text(order, idx=None):
    return (
        f"🆔 Buyurtma raqami: {order.get('order_id', (idx+1 if idx is not None else ''))}\n"
        f"📦 <b>Yuk ma'lumotlari</b>:\n"
        f"👤 Ism: {order['name']}\n"
        f"📞 Tel: {order['phone']}\n"
        f"📦 Yuk: {order.get('cargo_type', 'Ko‘rsatilmagan')}, {order['weight']} kg, {order['size']}\n"
        f"📝 {order['comment']}\n"
        f"📍 Qayerdan: {order['from_region']}, {order['from_district']}\n"
        f"🏁 Qayerga: {order['to_region']}, {order['to_district']}\n"
        f"Holat: {order.get('status', 'Yangi')}"
    )

async def delete_order_and_group_messages(idx):
    orders = await get_orders()
    if 0 <= idx < len(orders):
        order = orders[idx]
        group_message_ids = order.get("group_message_ids", {})
        for gid, mid in group_message_ids.items():
            try:
                await bot.delete_message(int(gid), int(mid))
            except Exception:
                pass
        del orders[idx]
        async with aiofiles.open(ORDERS_DB, 'w') as f:
            await f.write(json.dumps(orders, indent=4))
        return True
    return False

async def edit_order_and_group_messages(idx, orders):
    order = orders[idx]
    group_message_ids = order.get("group_message_ids", {})
    text = order_text(order, idx)
    for gid, mid in group_message_ids.items():
        try:
            await bot.edit_message_text(
                text, chat_id=int(gid), message_id=int(mid), parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

@router.message(F.text == "/start")
async def start_cmd(message: Message, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=markup)
    await state.clear()

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.edit_text(
        "👋 Xush kelibsiz! Yuk yuborish uchun boshlaymiz.\n\n"
        "🧾 Ismingizni kiriting:" if lang == "uz" else
        "👋 Добро пожаловать! Начнем оформление груза.\n\n"
        "🧾 Введите ваше имя:"
    )
    await state.set_state(CargoForm.waiting_for_name)

# --- FOYDALANUVCHI BUYURTMALARI ---
@router.message(F.text == "📦 Mening buyurtmalarim")
@router.message(F.text == "/myorders")
async def myorders(message: Message, state: FSMContext):
    orders = await get_orders()
    user_orders = [(i, o) for i, o in enumerate(orders) if o.get("user_id") == message.from_user.id]
    if not user_orders:
        await message.answer("Sizda buyurtmalar yo‘q.", reply_markup=main_menu())
        return
    for idx, order in user_orders:
        text = order_text(order, idx)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"user_edit_{idx}"),
                InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"user_delete_{idx}")
            ]
        ])
        await message.answer(text, reply_markup=markup)

@router.callback_query(F.data.startswith("user_delete_"))
async def user_delete_order(callback: CallbackQuery):
    idx = int(callback.data.split("_")[-1])
    orders = await get_orders()
    if 0 <= idx < len(orders):
        if orders[idx]["user_id"] != callback.from_user.id:
            await callback.answer("Bu buyurtma sizga tegishli emas!", show_alert=True)
            return
        await delete_order_and_group_messages(idx)
        await callback.message.edit_text("🗑 Buyurtma o‘chirildi. Guruhlardan ham o‘chirildi.")
    else:
        await callback.answer("Buyurtma topilmadi.")

@router.callback_query(F.data.startswith("user_edit_"))
async def user_edit_order(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[-1])
    orders = await get_orders()
    if 0 <= idx < len(orders):
        if orders[idx]["user_id"] != callback.from_user.id:
            await callback.answer("Bu buyurtma sizga tegishli emas!", show_alert=True)
            return
        await state.update_data(edit_idx=idx, edit_mode="user")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Yuk turi", callback_data="user_editfield_cargo_type")],
            [InlineKeyboardButton(text="Og‘irligi", callback_data="user_editfield_weight")],
            [InlineKeyboardButton(text="O‘lchami", callback_data="user_editfield_size")],
            [InlineKeyboardButton(text="Izoh", callback_data="user_editfield_comment")]
        ])
        await callback.message.answer("Qaysi maydonni tahrirlashni xohlaysiz?", reply_markup=markup)
        await state.set_state(CargoForm.edit_field)
    else:
        await callback.answer("Buyurtma topilmadi.")

@router.callback_query(F.data.startswith("user_editfield_"))
async def user_editfield_choose(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[-1]
    await state.update_data(edit_field=field)
    await callback.message.answer("Yangi qiymatni kiriting:")
    await state.set_state(CargoForm.edit_value)

@router.message(CargoForm.edit_value)
async def edit_field_save(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("edit_idx")
    field = data.get("edit_field")
    mode = data.get("edit_mode")
    orders = await get_orders()
    if idx is not None and field and 0 <= idx < len(orders):
        if mode == "user" and orders[idx]["user_id"] != message.from_user.id:
            await message.answer("Bu buyurtma sizga tegishli emas!")
            await state.clear()
            return
        orders[idx][field] = message.text
        await edit_order_and_group_messages(idx, orders)
        async with aiofiles.open(ORDERS_DB, 'w') as f:
            await f.write(json.dumps(orders, indent=4))
        await message.answer("✏️ Ma’lumot yangilandi va guruhlarda ham yangilandi.", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📦 Mening buyurtmalarim")]],
            resize_keyboard=True
        ))
    else:
        await message.answer("Buyurtma topilmadi.", reply_markup=main_menu())
    await state.clear()

# --- ADMIN PANEL ---
@router.message(F.text == "👨‍💻 Admin panel")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz!")
        return
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Buyurtmalar ro‘yxati")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="👤 Foydalanuvchilar")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💻 Admin paneliga xush kelibsiz!", reply_markup=markup)

@router.message(F.text == "⬅️ Orqaga")
async def back_from_admin(message: Message):
    await message.answer("Admin paneldan chiqdingiz.", reply_markup=main_menu())

@router.message(F.text == "📋 Buyurtmalar ro‘yxati")
async def show_orders(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz!")
        return
    orders = await get_orders()
    if not orders:
        await message.answer("Buyurtmalar yo‘q.")
        return
    for idx, order in enumerate(orders):
        text = order_text(order, idx)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"admin_edit_{idx}"),
                InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"admin_delete_{idx}")
            ],
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{idx}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{idx}")
            ],
            [
                InlineKeyboardButton(text="👤 Foydalanuvchiga yozish", callback_data=f"admin_msg_{order['user_id']}")
            ]
        ])
        await message.answer(text, reply_markup=markup)

@router.callback_query(F.data.startswith("admin_delete_"))
async def admin_delete_order(callback: CallbackQuery):
    idx = int(callback.data.split("_")[-1])
    orders = await get_orders()
    if 0 <= idx < len(orders):
        user_id = orders[idx]["user_id"]
        await delete_order_and_group_messages(idx)
        await callback.message.edit_text("🗑 Buyurtma o‘chirildi. Guruhlardan ham o‘chirildi.")
        try:
            await bot.send_message(user_id, "Sizning buyurtmangiz admin tomonidan o‘chirildi.")
        except:
            pass
    else:
        await callback.answer("Buyurtma topilmadi.")

@router.callback_query(F.data.startswith("admin_edit_"))
async def admin_edit_order(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[-1])
    orders = await get_orders()
    if 0 <= idx < len(orders):
        await state.update_data(edit_idx=idx, edit_mode="admin")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Yuk turi", callback_data="admin_editfield_cargo_type")],
            [InlineKeyboardButton(text="Og‘irligi", callback_data="admin_editfield_weight")],
            [InlineKeyboardButton(text="O‘lchami", callback_data="admin_editfield_size")],
            [InlineKeyboardButton(text="Izoh", callback_data="admin_editfield_comment")]
        ])
        await callback.message.answer("Qaysi maydonni tahrirlashni xohlaysiz?", reply_markup=markup)
        await state.set_state(CargoForm.edit_field)
    else:
        await callback.answer("Buyurtma topilmadi.")

@router.callback_query(F.data.startswith("admin_editfield_"))
async def admin_editfield_choose(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[-1]
    await state.update_data(edit_field=field)
    await callback.message.answer("Yangi qiymatni kiriting:")
    await state.set_state(CargoForm.edit_value)

@router.callback_query(F.data.startswith("admin_msg_"))
async def admin_msg_user(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(msg_user_id=user_id)
    await callback.message.answer("Foydalanuvchiga yuboriladigan xabar matnini kiriting:")
    await state.set_state("admin_send_msg")

class AdminStates(StatesGroup):
    select_user = State()
    select_order = State()
    edit_field = State()
    edit_value = State()

@router.message(F.state == "admin_send_msg")
async def admin_send_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("msg_user_id")
    if user_id:
        try:
            await bot.send_message(user_id, f"👨‍💻 Admindan xabar:\n\n{message.text}")
            await message.answer("Xabar foydalanuvchiga yuborildi.", reply_markup=main_menu())
        except Exception:
            await message.answer("Xabar yuborib bo‘lmadi (foydalanuvchi botni bloklagan bo‘lishi mumkin).", reply_markup=main_menu())
    await state.clear()

@router.callback_query(F.data.startswith("approve_"))
async def approve_order_cb(callback: CallbackQuery):
    idx = int(callback.data.split("_")[1])
    orders = await get_orders()
    if 0 <= idx < len(orders):
        orders[idx]["status"] = "Tasdiqlandi"
        await edit_order_and_group_messages(idx, orders)
        async with aiofiles.open(ORDERS_DB, 'w') as f:
            await f.write(json.dumps(orders, indent=4))
        await callback.message.edit_text("✅ Buyurtma tasdiqlandi va guruhlarda ham yangilandi.")
        try:
            await bot.send_message(orders[idx]["user_id"], "Sizning buyurtmangiz tasdiqlandi!")
        except:
            pass
    else:
        await callback.answer("Buyurtma topilmadi.")

@router.callback_query(F.data.startswith("reject_"))
async def reject_order_cb(callback: CallbackQuery):
    idx = int(callback.data.split("_")[1])
    orders = await get_orders()
    if 0 <= idx < len(orders):
        orders[idx]["status"] = "Rad etildi"
        await edit_order_and_group_messages(idx, orders)
        async with aiofiles.open(ORDERS_DB, 'w') as f:
            await f.write(json.dumps(orders, indent=4))
        await callback.message.edit_text("❌ Buyurtma rad etildi va guruhlarda ham yangilandi.")
        try:
            await bot.send_message(orders[idx]["user_id"], "Sizning buyurtmangiz rad etildi.")
        except:
            pass
    else:
        await callback.answer("Buyurtma topilmadi.")

@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz!")
        return
    orders = await get_orders()
    users = set()
    for order in orders:
        users.add(order.get("user_id"))
    await message.answer(
        f"📦 Buyurtmalar soni: <b>{len(orders)}</b>\n"
        f"👤 Unikal foydalanuvchilar: <b>{len(users)}</b>"
    )

@router.message(F.text == "👤 Foydalanuvchilar")
async def show_users(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz!")
        return
    try:
        async with aiofiles.open(USER_DB, 'r') as f:
            content = await f.read()
            users = json.loads(content) if content else {}
    except Exception:
        users = {}
    if not users:
        await message.answer("Foydalanuvchilar topilmadi.")
        return
    text = "👤 Foydalanuvchilar ro‘yxati:\n"
    for uid, data in users.items():
        text += f"ID: <code>{uid}</code> | {data.get('name','-')} | {data.get('phone','-')}\n"
    await message.answer(text)

# --- BUYURTMA QO‘SHISH ---
@router.message(CargoForm.waiting_for_name)
async def ask_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True
    )
    await message.answer("📞 Telefon raqamingizni yuboring yoki yozing:", reply_markup=markup)
    await state.set_state(CargoForm.waiting_for_phone)

@router.message(CargoForm.waiting_for_phone)
async def ask_cargo_type(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+998" + phone[-9:]
    else:
        phone = message.text.replace(" ", "")
    if not phone.startswith("+998") or not phone[1:].isdigit() or len(phone) != 13:
        await message.answer("❌ Noto‘g‘ri format. +998901234567 ko‘rinishida yuboring.")
        return
    await state.update_data(phone=phone)
    await message.answer(
        "📦 Yuk turini tanlang yoki yozing (majburiy emas):",
        reply_markup=cargo_type_keyboard()
    )
    await state.set_state(CargoForm.waiting_for_cargo_type)

@router.message(CargoForm.waiting_for_cargo_type)
async def ask_weight(message: Message, state: FSMContext):
    text = message.text
    if text == "Tashlab ketish":
        await state.update_data(cargo_type="Ko‘rsatilmagan")
    elif text == "Boshqa":
        await message.answer("Yuk turini o‘zingiz yozing:")
        return
    elif text in cargo_types:
        await state.update_data(cargo_type=text)
    else:
        await state.update_data(cargo_type=text)
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Shart emas")]],
        resize_keyboard=True
    )
    await message.answer("⚖️ Yuk og‘irligini kiriting (kg) yoki 'Shart emas' tugmasini bosing:", reply_markup=markup)
    await state.set_state(CargoForm.waiting_for_weight)

@router.message(CargoForm.waiting_for_weight)
async def ask_size(message: Message, state: FSMContext):
    weight = message.text
    if weight.lower() == "shart emas":
        weight = "Ko‘rsatilmagan"
    await state.update_data(weight=weight)
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Shart emas")]],
        resize_keyboard=True
    )
    await message.answer("📏 Yuk o‘lchamini kiriting (masalan: 1x2x0.5 m) yoki 'Shart emas' tugmasini bosing:", reply_markup=markup)
    await state.set_state(CargoForm.waiting_for_size)

@router.message(CargoForm.waiting_for_size)
async def ask_comment(message: Message, state: FSMContext):
    size = message.text
    if size.lower() == "shart emas":
        size = "Ko‘rsatilmagan"
    await state.update_data(size=size)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ha", callback_data="comment_yes")],
        [InlineKeyboardButton(text="Yo‘q", callback_data="comment_no")]
    ])
    await message.answer("📝 Qo‘shimcha izoh yoki talablaringiz bormi?", reply_markup=markup)
    await state.set_state(CargoForm.waiting_for_comment)

@router.callback_query(F.data == "comment_yes")
async def comment_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Izoh yoki talablaringizni yozing:")
    await state.set_state(CargoForm.waiting_for_comment_text)

@router.callback_query(F.data == "comment_no")
async def comment_no(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="Yo‘q")
    await callback.message.edit_text("📍 Yukni qayerdan yuborasiz?", reply_markup=make_inline_keyboard(list(regions_data.keys()), "from_region"))
    await state.set_state(CargoForm.from_region)

@router.message(CargoForm.waiting_for_comment_text)
async def comment_text(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await message.answer("📍 Yukni qayerdan yuborasiz?", reply_markup=make_inline_keyboard(list(regions_data.keys()), "from_region"))
    await state.set_state(CargoForm.from_region)

@router.message(CargoForm.waiting_for_comment)
async def ask_from_region(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await message.answer("📍 Yukni qayerdan yuborasiz?", reply_markup=make_inline_keyboard(list(regions_data.keys()), "from_region"))
    await state.set_state(CargoForm.from_region)

@router.callback_query(F.data.startswith("from_region"))
async def from_region_selected(callback: CallbackQuery, state: FSMContext):
    region = callback.data.split(":", 1)[1]
    if region not in regions_data:
        await callback.answer("Noto‘g‘ri viloyat!")
        return
    await state.update_data(from_region=region)
    await callback.message.edit_text("📍 Qaysi tumandan?", reply_markup=make_inline_keyboard(list(regions_data[region]), "from_district"))
    await state.set_state(CargoForm.from_district)

@router.callback_query(F.data.startswith("from_district"))
async def from_district_selected(callback: CallbackQuery, state: FSMContext):
    district = callback.data.split(":", 1)[1]
    data = await state.get_data()
    region = data.get("from_region")
    if not region or district not in regions_data.get(region, []):
        await callback.answer("Noto‘g‘ri tuman!")
        return
    await state.update_data(from_district=district)
    await callback.message.edit_text("🏁 Yuk qayerga yuboriladi?", reply_markup=make_inline_keyboard(list(regions_data.keys()), "to_region"))
    await state.set_state(CargoForm.to_region)

@router.callback_query(F.data.startswith("to_region"))
async def to_region_selected(callback: CallbackQuery, state: FSMContext):
    region = callback.data.split(":", 1)[1]
    if region not in regions_data:
        await callback.answer("Noto‘g‘ri viloyat!")
        return
    await state.update_data(to_region=region)
    await callback.message.edit_text("🏁 Qaysi tuman?", reply_markup=make_inline_keyboard(list(regions_data[region]), "to_district"))
    await state.set_state(CargoForm.to_district)

@router.callback_query(F.data.startswith("to_district"))
async def to_district_selected(callback: CallbackQuery, state: FSMContext):
    district = callback.data.split(":", 1)[1]
    data = await state.get_data()
    region = data.get("to_region")
    if not region or district not in regions_data.get(region, []):
        await callback.answer("Noto‘g‘ri tuman!")
        return
    await state.update_data(to_district=district)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Ha, rasm yuboraman", callback_data="photo_yes")],
        [InlineKeyboardButton(text="❌ Yo‘q, rasm yo‘q", callback_data="photo_no")]
    ])
    await callback.message.edit_text("📷 Yuk rasmini yubormoqchimisiz?", reply_markup=markup)
    await state.set_state(CargoForm.ask_photo)

@router.callback_query(F.data == "photo_yes")
async def ask_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📷 Yuk rasmini yuboring:")
    await state.set_state(CargoForm.cargo_image)

@router.callback_query(F.data == "photo_no")
async def skip_photo(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await finish_order(callback.message, state, photo=None)
    await callback.answer("Buyurtma rasmiz qabul qilindi!")

@router.message(CargoForm.cargo_image)
async def receive_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❗ Rasm yuboring.")
        return
    await finish_order(message, state, photo=message.photo[-1].file_id)

async def finish_order(message, state, photo=None):
    data = await state.get_data()
    now = time.time()
    last_time = user_last_order_time.get(message.from_user.id, 0)
    if now - last_time < 60:
        await message.answer("❗ Siz 1 daqiqada faqat 1 ta buyurtma yuborishingiz mumkin.")
        return
    user_last_order_time[message.from_user.id] = now

    orders = await get_orders()
    order_id = len(orders) + 1
    text = order_text(data | {"order_id": order_id}, len(orders))
    order = {
        "order_id": order_id,
        "user_id": message.from_user.id,
        "name": data['name'],
        "phone": data['phone'],
        "cargo_type": data.get('cargo_type', 'Ko‘rsatilmagan'),
        "weight": data['weight'],
        "size": data['size'],
        "comment": data['comment'],
        "from_region": data['from_region'],
        "from_district": data['from_district'],
        "to_region": data['to_region'],
        "to_district": data['to_district'],
        "status": "Yangi",
        "group_message_ids": {}
    }
    for gid in GROUP_IDS:
        try:
            if photo:
                sent = await bot.send_photo(gid, photo, caption=text)
            else:
                sent = await bot.send_message(gid, text)
            order["group_message_ids"][str(gid)] = sent.message_id
        except Exception:
            pass
    await save_order(order)
    await message.answer(
        "✅ Yuk ma’lumoti yuborildi.\n\n📦 Buyurtma holatini ko‘rish uchun 'Mening buyurtmalarim' tugmasini bosing.",
        reply_markup=main_menu()
    )
    await state.clear()

@router.message(F.text == "➕ Yana yuk qo‘shish")
async def restart(message: Message, state: FSMContext):
    user_data = await get_user_data(message.from_user.id)
    if user_data:
        await state.update_data(**user_data)
        await message.answer(
            "📦 Yuk turini tanlang yoki yozing (majburiy emas):",
            reply_markup=cargo_type_keyboard()
        )
        await state.set_state(CargoForm.waiting_for_cargo_type)
    else:
        await message.answer("🧾 Ismingizni kiriting:", reply_markup=main_menu())
        await state.set_state(CargoForm.waiting_for_name)

@router.message(F.text == "🚪 Chiqish")
async def exit_bot(message: Message, state: FSMContext):
    await message.answer("👋 Rahmat! Agar yana yuk yubormoqchi bo‘lsangiz /start buyrug‘ini bosing.", reply_markup=main_menu())
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())