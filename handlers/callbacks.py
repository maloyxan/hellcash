# handlers/callbacks.py
import os
from pathlib import Path
import random
import string
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandObject
from aiogram.filters import Command
from aiocryptopay import AioCryptoPay, Networks
from aiogram.types import FSInputFile
import database as db
import config
from .inline_keyboards import (
    get_main_menu, get_packs_keyboard, 
    BuyCallback, get_confirm_keyboard, get_payment_keyboard
)
from .inline_keyboards import otziv
from .inline_keyboards import cancel_button
from .inline_keyboards import channel_button

router = Router()

# Инициализация CryptoPay (Mainnet)
cryptopay = AioCryptoPay(token=config.CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)

def generate_accounts_data(quantity: int) -> str:
    """Генерирует список аккаунтов в формате TYAASYRRMGT:7szwcyfjcu"""
    accounts = []
    for _ in range(quantity):
        # Левая часть: 11 заглавных букв
        part1 = ''.join(random.choices(string.ascii_uppercase, k=11))
        # Правая часть: 10 символов (строчные буквы + цифры)
        part2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        accounts.append(f"{part1}:{part2}")
    
    # Соединяем каждый аккаунт с новой строки
    return "\n".join(accounts)



# --- START ---
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    user = await db.get_user(message.from_user.id)
    
    if not user:
        # Регистрация нового пользователя
        support_id = await db.add_user(message.from_user.id, message.from_user.username)
        
        # Уведомление админу
        admin_text = (
            f"🆕 <b>Новый пользователь!</b>\n"
            f"User: @{message.from_user.username}\n"
            f"ID: {message.from_user.id}\n"
            f"Support ID: {support_id}"
        )
        try:
            await bot.send_message(config.ADMIN_ID, admin_text, parse_mode="HTML")
        except:
            pass # Если админ заблочил бота или ошибка ID

    root_dir = Path(__file__).parent.parent 
    photo_path = root_dir / "images" / "bannerhell.jpg"

    if not photo_path.exists():
        print(f"ОШИБКА: Файл не найден по пути {photo_path}")
        # Если фото нет, просто отправим текст, чтобы бот не падал
        await message.answer(MAIN_MENU_TEXT, parse_mode="HTML", reply_markup=get_main_menu())
        return

    photo = FSInputFile(str(photo_path))

    MAIN_MENU_TEXT = (
        "<b>Добро пожаловать в HELL$CASH SHOP ✨</b>\n\n"
        "Устал от <b>некачественных Cash App аккаунтов</b>? "
        "Тебе определенно к нам! ⭐️,\n" 
        "Ведь качество наших аккаунтов зашкаливает!\n\n"
        "Ниже располагается меню, ознакамливайся 🎲"
    )

    await message.answer_photo(
        photo=photo,
        caption=MAIN_MENU_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

# --- ВОЗВРАТ В МЕНЮ ---
#@router.callback_query(F.data == "cancel")
#async def go_to_main_menu(callback: CallbackQuery): 
    #await callback.answer()

   # # Путь к фото
   # photo_path = os.path.join("images", "bannerhell.jpg") 
   # photo = FSInputFile(photo_path)

    #MAIN_MENU_TEXT = (
   #     "<b>Добро пожаловать в HELL$CASH SHOP ✨</b>\n\n"
   #     "Устал от <b>некачественных Cash App аккаунтов</b>? "
     #   "Тебе определенно к нам! ⭐️,\n" 
     #   "Ведь качество наших аккаунтов зашкаливает!\n\n"
    #    "Ниже располагается меню, ознакамливайся 🎲"
  #  )

   # # 1. Удаляем текущее текстовое сообщение
  #  await callback.message.delete()
#
 #   # 2. Отправляем новое сообщение с фото
  #  await callback.message.answer_photo(
  #      photo=photo,
  #      caption=MAIN_MENU_TEXT,
  #      parse_mode="HTML",
  #      reply_markup=get_main_menu()
  #  )


  # --- ВОЗВРАТ В МЕНЮ ---
@router.callback_query(F.data == "cancel")
async def go_to_main_menu(callback: CallbackQuery): 
    await callback.answer()

    # Динамически определяем путь к папке проекта
    # Path(__file__).parent.parent.parent — это выход из handlers -> mainbot -> в HellShop
    root_dir = Path(__file__).parent.parent 
    photo_path = root_dir / "images" / "bannerhell.jpg"

    MAIN_MENU_TEXT = (
        "<b>Добро пожаловать в HELL$CASH SHOP ✨</b>\n\n"
        "Устал от <b>некачественных Cash App аккаунтов</b>? "
        "Тебе определенно к нам! ⭐️,\n" 
        "Ведь качество наших аккаунтов зашкаливает!\n\n"
        "Ниже располагается меню, ознакамливайся 🎲"
    )

    # Проверяем, существует ли файл, чтобы бот не «упал» снова
    if photo_path.exists():
        photo = FSInputFile(str(photo_path))
        
        # 1. Удаляем текущее текстовое сообщение
        await callback.message.delete()

        # 2. Отправляем новое сообщение с фото
        await callback.message.answer_photo(
            photo=photo,
            caption=MAIN_MENU_TEXT,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    else:
        # Если фото не найдено, просто редактируем текст, чтобы не было ошибки
        print(f"Критическая ошибка: Файл не найден по пути {photo_path}")
        await callback.message.edit_text(
            MAIN_MENU_TEXT + "\n\n(Ошибка: баннер не найден)",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )

# --- ШАГ 1: ВЫБОР КОЛИЧЕСТВА ---
@router.callback_query(F.data == "buy_start")
async def buy_step_one(callback: CallbackQuery):
    await callback.answer()
    
    text = (
        "<code>Шаг 1 из 3... Выбор количества для покупки</code>\n\n"
        "<b>Решил купить аккаунты? Ты на верном пути! ✈️</b>\n"
        "Наши преимущества перед другими сервисами:\n\n"
        "- Мы гарантируем возврат в случаи невалидности 🔮\n"
        "- Готовы предоставить платежные системы высшего уровня 💾\n"
        "- Удобные способы оплаты 📥\n"
        "- Быстрая тех поддержка, готовая вам помочь в любой момент 📞\n\n"
        "Кхм, перейдем к количеству\n\n"
        "1 Аккаунт - 10$ 💰"
    )
    
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_packs_keyboard())

# --- ШАГ 2: ПОДТВЕРЖДЕНИЕ ---
@router.callback_query(BuyCallback.filter(F.action == "select"))
async def buy_step_two(callback: CallbackQuery, callback_data: BuyCallback):
    await callback.answer()
    
    amount = callback_data.amount
    price = callback_data.price
    
    # Создаем предварительный заказ в БД
    order_id = await db.create_order(
        telegram_id=callback.from_user.id,
        item_name="Cash App Accounts",
        quantity=amount,
        amount=price
    )
    
    text = (
        "<code>Шаг 2 из 3... Оплата товара</code>\n\n"
        "<b>Ты почти у цели вот твой заказ, все ли верно? ✅</b>\n"
        f"🔹 Товар: <i>Cash App Accounts</i>\n"
        f"🔹 Количество: <i>{amount} штук</i>\n"
        f"🔹 Сумма заказа: <i>{price}$</i>\n"
        f"🔹 Номер сделки: <i>{order_id}</i>\n\n"
        "Почти все готово, осталось оплатить заказ, выбери ниже способ пополнения ✔️"
    )
    
    await callback.message.edit_text(
        text, 
        parse_mode="HTML", 
        reply_markup=get_confirm_keyboard(amount, price, order_id)
    )

# --- ШАГ 3: СОЗДАНИЕ СЧЕТА CRYPTOBOT ---
@router.callback_query(F.data.startswith("pay_crypto_"))
async def buy_step_three_payment(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    order = await db.get_order(order_id)
    
    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    price = order[4]
    amount = order[3]
    
    try:
        invoice = await cryptopay.create_invoice(asset='USDT', amount=price)
        
        # Уведомление Админу
        try:
            await bot.send_message(
                config.ADMIN_ID, 
                f"🧾 <b>Создан счет!</b>\nUser: @{callback.from_user.username}\nСумма: {price}$", 
                parse_mode="HTML"
            )
        except: pass

        text = (
            "Шаг 2 из 3... Оплата товара\n\n"
            "Решил использовать CryptoBot? Нет проблем, перепроверь информацию ниже ⬇️\n"
            f"🔹 ID заказа: {invoice.invoice_id}\n"
            f"🔹 Товар: Cash App Accounts\n"
            f"🔹 Количество: {amount} штук\n"
            f"🔹 Сумма заказа: {price}$\n"
            f"🔹 Номер сделки: {order_id}\n\n"
            "Все верно? Внизу тебя ждет счет, после его пополнения жми кнопку проверить оплату ⏭️"
        )
        
        await callback.message.edit_text(
            text, 
            parse_mode="HTML",
            # ТУТ ИЗМЕНЕНИЕ: передаем и invoice.invoice_id и order_id
            reply_markup=get_payment_keyboard(invoice.bot_invoice_url, invoice.invoice_id, order_id)
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка создания счета: {e}", show_alert=True)

# --- ПРОВЕРКА ОПЛАТЫ ---
@router.callback_query(F.data.startswith("check_pay_"))
async def check_payment_handler(callback: CallbackQuery, bot: Bot):
    # Разбираем данные из кнопки: check_pay_{invoice_id}_{order_id}
    data_parts = callback.data.split("_")
    invoice_id = int(data_parts[2])
    order_id = int(data_parts[3])
    
    try:
        invoices = await cryptopay.get_invoices(invoice_ids=[invoice_id])
        if not invoices:
             await callback.answer("Счет не найден.", show_alert=True)
             return
             
        invoice = invoices[0]
        
        if invoice.status == 'paid': # Если оплачено
            # 1. Получаем данные заказа из БД, чтобы знать количество
            order = await db.get_order(order_id)
            if not order:
                await callback.answer("Ошибка: заказ не найден в базе.", show_alert=True)
                return
            
            quantity = order[3] # Количество штук
            
            # 2. Генерируем товар
            accounts_list = generate_accounts_data(quantity)
            
            # 3. Обновляем статус в БД и статистику
            await db.update_order_status(order_id, "completed")
            await db.increment_user_deals(callback.from_user.id)
            
            # 4. Отправляем товар пользователю
            # Используем тег <pre>, чтобы можно было скопировать все аккаунты одним кликом
            success_text = (
                "✅ <b>Оплата прошла успешно!</b>\n"
                "🛒 Вот ваш заказ:\n\n"
                f"<pre>{accounts_list}</pre>\n\n"
                "Спасибо за покупку! Ждем вас снова."
            )
            
            await callback.message.edit_text(success_text, parse_mode="HTML", reply_markup=get_main_menu())
            
            # 5. Уведомление Админу с суммой
            admin_text = (
                f"💰 <b>Успешная оплата!</b>\n"
                f"User: @{callback.from_user.username} (ID: {callback.from_user.id})\n"
                f"Сумма: {invoice.amount} {invoice.asset}\n"
                f"Выдано аккаунтов: {quantity} шт."
            )
            try:
                await bot.send_message(config.ADMIN_ID, admin_text, parse_mode="HTML")
            except: pass
            
        else:
             await callback.answer(f"Оплата еще не поступила. Статус: {invoice.status}", show_alert=True)
             
    except Exception as e:
        await callback.answer(f"Ошибка проверки: {e}", show_alert=True)
        print(f"Error checking payment: {e}")

@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    await callback.answer()
    
    # 1. Получаем данные пользователя из БД
    user = await db.get_user(callback.from_user.id)
    
    # В таблице users порядок полей: id, telegram_id, username, support_id, deals_count
    # Значит support_id лежит под индексом 3
    support_id = user[3]
    
    # Юзернейм менеджера из конфига
    manager = config.SUPPORT_USERNAME

    # 2. Формируем текст
    # Используем <code> для копирования номера
    text = (
        "🛎️ <b>Нужна помощь? Обращайся правильно!</b>\n"
        f"🔹 Твой номер обращения: <code>{support_id}</code>\n"
        f"🔹 Менеджер поддержки: @{manager}\n\n"
        "📌 <b>Правила обращения:</b>\n"
        "✅ Будь вежлив и точен – опиши проблему четко и без лишних сообщений.\n"
        "✅ Не спрашивай о статусе чека – обработка занимает до 15 минут.\n"
        "✅ Нет спаму! Одно подробное сообщение > 10 коротких.\n\n"
        "🚀 Мы решим вопрос быстро, если ты следуешь этим простым правилам.\n\n"
        f"👉 Просто перешли этот номер (<code>{support_id}</code>) менеджеру – и жди ответа!\n\n"
        "P.S. Чем точнее опишешь проблему, тем быстрее получишь решение. 😉"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=otziv()
    )

@router.callback_query(F.data == "info")
async def info_handler(callback: CallbackQuery):
    await callback.answer()
    
    # Ссылка-заглушка для синего копируемого текста
    title_text = "ℹ️ Информация о сервисе HELL$CASH"
    
    text = (
        f'<code><a href="https://t.me/share/url?url={title_text}">{title_text}</a></code>\n\n'
        "<b>HELL$CASH SHOP</b> — это ваш надежный поставщик качественных аккаунтов Cash App. "
        "Мы работаем на рынке более 2-х лет и знаем всё о безопасности и стабильности.\n\n"
        
        "🛡 <b>Наши гарантии:</b>\n"
        "• Валидность товара на момент покупки — 100%.\n"
        "• Замена аккаунта в течение 24 часов, если обнаружен брак.\n"
        "• Полная анонимность ваших данных и транзакций.\n\n"
        
        "📦 <b>О товаре:</b>\n"
        "Все аккаунты проходят ручную проверку. Формат выдачи позволяет сразу приступить к работе. "
        "Мы используем только чистые прокси и лучшие софты для брута.\n\n"
        
        "🔄 <b>Правила возврата:</b>\n"
        "Возврат или замена возможны только при невалиде аккаунта."
        "Это защищает нас от мошенничества и гарантирует вам честный результат.\n\n"
        
        "💡 <b>Совет:</b>\n"
        "Перед сдачей аккаунтов уточните у скупа: Новый ли лендинг? Это поможет вам избежать лишних невалидов."
    )

    # Используем ту же кнопку возврата, что и в поддержке, или создаем новую
    await callback.message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=cancel_button() # Используем кнопку "Назад"
    )

@router.callback_query(F.data == "feedback")
async def info_handler(callback: CallbackQuery):
    await callback.answer()

    textrev = (
    "🔍 <b>Хочешь убедиться в нашей надежности?</b>\n" # пометка аааа
    "📢 Присоединяйся к нашему официальному каналу:\n\n"

    "<b>Здесь ты найдешь:</b>\n"
    "✅ Реальные отзывы покупателей с пруфами\n"
    "✅ Акции и конкурсы с крутыми призами\n"
    "✅ Свежие анонсы обновлений и спецпредложений\n\n"

    "Подпишись сейчас – не упусти выгоду! 🎁\n\n"

    "Мы ценим твое доверие! 😊"
    )

    await callback.message.answer(
        textrev,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=channel_button() # Используем кнопку "Назад"
    )

@router.message(Command("giveaccount"))
async def admin_give_account(message: Message, command: CommandObject):
    # 1. Проверка на админа
    if message.from_user.id != config.ADMIN_ID:
        return # Игнорируем, если пишет не админ

    # 2. Получаем количество из аргумента (если не указано, то 1)
    quantity = 1
    if command.args and command.args.isdigit():
        quantity = int(command.args)

    # 3. Генерируем тестовые данные (используем нашу функцию из прошлых шагов)
    # Если функция generate_accounts_data в другом файле, не забудьте импорт
    accounts_list = generate_accounts_data(quantity)

    # 4. Формируем текст выдачи
    success_text = (
        "✅ <b>Оплата прошла успешно!</b>\n"
        "🛒 Вот ваш заказ:\n\n"
        f"<pre>{accounts_list}</pre>\n\n"
        "Спасибо за покупку! Ждем вас снова."
    )

    # 5. Отправляем сообщение
    await message.answer(
        success_text, 
        parse_mode="HTML", 
        reply_markup=get_main_menu()
    )

# Заглушка для Custom Amount
@router.callback_query(F.data == "buy_custom")
async def buy_custom(callback: CallbackQuery):
    await callback.answer("Для покупки своего количества напишите в поддержку!", show_alert=True)