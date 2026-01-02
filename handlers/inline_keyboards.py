# handlers/inline_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# Фабрика колбэков для покупки
class BuyCallback(CallbackData, prefix="buy"):
    action: str
    amount: int
    price: float

def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 За покупками", callback_data="buy_start")
    builder.button(text="🛜 Поддержка", callback_data="support")
    #builder.button(text="О нас", url="https://t.me/hellcashchannel")
   # builder.button(text="✅ Отзывы клиентов", callback_data="feedback")
    builder.button(text="ℹ️ Информация", callback_data="info")
    builder.adjust(2,1)
    return builder.as_markup()

def get_packs_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Цена за 1 шт = 10$
    packs = [
        ("1 аккаунт", 1, 10),
        ("3 аккаунта", 3, 30),
        ("5 аккаунтов", 5, 50),
        ("10 аккаунтов", 10, 100),
        ("20 аккаунтов", 20, 200),
        ("30 аккаунтов", 30, 300),
    ]

    for name, qty, price in packs:
        builder.button(
            text=name, 
            callback_data=BuyCallback(action="select", amount=qty, price=price)
        )
    
    builder.button(text="Свое количество", callback_data="buy_custom")
    builder.button(text="🔙 Вернуться назад", callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()

def get_confirm_keyboard(amount: int, price: float, order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Передаем ID заказа в callback
    builder.button(text="🤖 CryptoBot", callback_data=f"pay_crypto_{order_id}")
    builder.button(text="🔙 Главное меню", callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()

def get_payment_keyboard(pay_url: str, invoice_id: int, order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    from config import MANUAL_URL
    
    builder.button(text="Инструкция CryptoBot", url=MANUAL_URL)
    builder.button(text="Оплатить счет", url=pay_url)
    # Передаем и ID счета (invoice_id), и ID заказа (order_id) через разделитель "_"
    builder.button(text="Проверить оплату", callback_data=f"check_pay_{invoice_id}_{order_id}")
    builder.button(text="🔙 Главное меню", callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()

def otziv() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    url_otziv = "https://t.me/hellcashsupport"

    builder.button(text="💬 Написать", url=url_otziv)
    builder.button(text="🔙 Вернуться назад", callback_data="cancel")

    builder.adjust(1)
    return builder.as_markup()

def cancel_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Вернуться назад", callback_data="cancel")

    builder.adjust(1)
    return builder.as_markup()

def channel_button() -> InlineKeyboardMarkup:

    channel_url = "https://t.me/hellcashreviews"

    builder = InlineKeyboardBuilder()
    builder.button(text="Наш канал ⭐", url=channel_url)
    builder.button(text="🔙 Вернуться назад", callback_data="cancel")

    builder.adjust(1)

    return builder.as_markup()
