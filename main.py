from aiogram import Bot, Dispatcher, executor
import os
from dotenv import load_dotenv
from aiogram.types import Message, CallbackQuery, LabeledPrice
from work import *
from keyboards import *
load_dotenv()


bot = Bot(os.getenv('TOKEN'))

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    chat_id = message.from_user.id
    """Надо попробовать вытащить из базы пользователя
    Если его нет - зарегестрировать
    Если он есть - показать ему главное меню"""
    user = first_select_user(chat_id)
    if user:  # Есть ли что-то в переменной?
        await message.answer('Авторизация прошла успешно')
        await main_menu(message)
    else:
        text = f"""Здравствуйте, {message.from_user.full_name} вас привествуйет The World Garb
Для продолжения зарегестрируйтесь, отправив свой контакт 👇👇👇"""
        await message.answer(text, reply_markup=generate_phone_number())


@dp.message_handler(content_types=['contact'])
async def register(message: Message):
    chat_id = message.from_user.id
    full_name = message.from_user.full_name
    phone = message.contact.phone_number
    register_user(chat_id, full_name, phone)
    create_cart(chat_id)
    await message.answer('Регистрация прошла успешно')
    await main_menu(message)


async def main_menu(message: Message):
    await message.answer('Выберите что хотите сделать', reply_markup=generate_main_menu())


# @dp.message_handler(lambda message: '✅ Сделать заказ' in message.text)
@dp.message_handler(regexp=r'✅ Сделать заказ')
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer('Выберите категорию товара: ', reply_markup=generate_categories_menu(categories))


@dp.callback_query_handler(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
    # category_1
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    products = get_products_by_category(category_id)
    message_id = call.message.message_id
    await bot.edit_message_text(text='Выберите стиль: ',
                                chat_id=call.message.chat.id,
                                message_id=message_id,
                                reply_markup=generate_products_menu(products))


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def get_to_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    categories = get_categories()
    await bot.edit_message_text(text='Выберите категорию: ',
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=generate_categories_menu(categories))


@dp.callback_query_handler(lambda call: 'product' in call.data)
async def show_detail_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    # product_1
    _, product_id = call.data.split('_')
    product_id = int(product_id)
    product = get_product(product_id)
    # print(product)
    await bot.delete_message(chat_id, message_id)
    with open(product[5], mode='rb') as img:
        caption = f'''{product[2]}

Описание: {product[4]}

Цена: {product[3]}

Выбрано: 1 - {product[3]}'''
        await bot.send_photo(chat_id=chat_id,
                             photo=img,
                             caption=caption,
                             reply_markup=generate_product_buttons(product[0], product[1]))


@dp.callback_query_handler(lambda call: 'change' in call.data)
async def change_quantity(call: CallbackQuery):
    _, product_id, quantity = call.data.split('_')
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    product = get_product(product_id)
    caption = f'''{product[2]}

Описание: {product[4]}

Цена: {product[3]} сум

Выбрано: {quantity} - {product[3] * int(quantity)} сум'''
    if int(quantity) >= 1:
        await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption,
                                       reply_markup=generate_product_buttons(product[0], product[1], int(quantity)))


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def back_to_category(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id, message_id)
    _, category_id = call.data.split('_')
    products = get_products_by_category(category_id)
    await bot.send_message(chat_id, 'Выберите продукт: ',
                           reply_markup=generate_products_menu(products))


@dp.callback_query_handler(lambda call: call.data.startswith('cart'))
async def add_product_cart(call: CallbackQuery):  # Функция добавления товара в корзину
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)
    cart_id = get_user_cart_id(chat_id)  # Функция получения корзины
    product = get_product(product_id)  # Функция получения тора для добавления
    final_price = product[3] * quantity  # Вычисление общей стоимости
    # Попытаемся закинуть товар, если был - то обновим ему количество
    if insert_or_update_cart_product(cart_id, product[2], quantity, final_price):
        # Если товар новый - вернулось True
        await bot.answer_callback_query(call.id, 'Продукт успешно добавлен')
    else:
        await bot.answer_callback_query(call.id, 'Количество успешно изменено')


@dp.message_handler(regexp=r'🛒 Корзина')
async def show_cart(message: Message, edit_message=False):  # Функция вывода корзины
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)  # Получение id корзины пользователя
    try:
        update_total_product_total_price(cart_id)  # Обновление общего количества товаров и цены
    except Exception as e:  # Если ошибка - то выведем сообщение
        print(e)
        await message.answer('Корзина не доступна. Обратитесь в поддержку')
        return

    total_products, total_price = get_total_products_price(cart_id)

    cart_products = get_cart_products(cart_id)  # Вывод товаров данной корзины
    text = 'Ваша корзина: \n\n'
    i = 0
    for cart_product_id, product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''

    text += f'''Общее количество продуктов: {0 if total_products == None else total_products}
Общая стоимость товаров: {0 if total_price == None else total_price}'''

    if edit_message:
        await bot.edit_message_text(text, chat_id, message.message_id,
                                    reply_markup=generate_cart_product(cart_id, cart_products))
    else:
        await bot.send_message(chat_id, text,
                               reply_markup=generate_cart_product(cart_id, cart_products))


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete(call: CallbackQuery):
    # delete_1
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)

    delete_cart_product(cart_product_id)
    await bot.answer_callback_query(call.id, 'Продукт успешно удален')
    await show_cart(message=call.message, edit_message=True)


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)
    total_products, total_price = get_total_products_price(cart_id)

    cart_products = get_cart_products(cart_id)  # Вывод товаров данной корзины
    text = 'Ваш заказ: \n\n'
    i = 0
    for cart_product_id, product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''

    text += f'''Общее количество продуктов: {0 if total_products is None else total_products}
Общая стоимость товаров: {0 if total_price is None else total_price}'''

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Заказ №{cart_id}',
        description=text,
        payload='bot-defined invoice payload',
        provider_token='398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065',
        currency='UZS',
        prices=[
            LabeledPrice(label='Общая стоимость', amount=int(total_price * 100)),
            LabeledPrice(label='Доставка', amount=1500000)
        ]
    )
    add_order(cart_id, chat_id, text, total_price)
    await bot.send_message(chat_id, 'Заказ оплачен')
    print(text)


@dp.message_handler(regexp=r'📒 История заказов')
async def history(message: Message):
    chat_id = message.chat.id
    history = select_order(chat_id)
    # print(history)
    # for order_id, order_description, order_price, user_id in history:
    for item in history:

        # print("=====")
        # print(item)
        text_history = f'''Номер заказа:{item[0]}
        {item[3]}'''
        await bot.send_message(chat_id, text_history)


executor.start_polling(dp)
