"""
Модуль для обработки запросов пользователя в боте для заказа еды.

Этот модуль содержит обработчики команд и событий, связанных с меню, корзиной покупок, редактированием товаров в корзине,
и обработкой платежей. Он включает:
- Приветственное сообщение и доступ к основному меню при запуске бота.
- Возможность добавлять, редактировать и удалять товары из корзины.
- Показ содержимого корзины и оформление заказа с суммой покупки.
- Возможность очистки корзины и оплаты заказа.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import app.keyboard as kb

router = Router()

# Старт
@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обрабатывает команду /start.

    Отправляет пользователю приветственное сообщение с его именем и предоставляет доступ к основному меню.

    Args:
        message (Message): Объект сообщения от пользователя, содержащий команду /start.
    """
    await message.answer(
        text=f'Здравствуйте, {message.from_user.first_name}\nЧтобы сделать заказ, нажмите "Меню"',
        reply_markup=await kb.main()
    )

# Списки с полным меню
selected_Основное_меню = ['Суп', 'Гарнир', 'Салат', 'Мясное блюдо', '🔙Выбор раздела']
selected_Суп = ['Крем-суп из тыквы', 'Том Ям', 'Минестроне', 'Борщ', '🔙Основное меню']
selected_Салат = ['Цезарь с курицей', 'Греческий салат', 'Оливье', 'Салат с тунцом', '🔙Основное меню']
selected_Мясное_блюдо = ['Стейк из говядины', 'Куриное филе', 'Свинина в соусе BBQ', 'Котлеты по-домашнему', '🔙Основное меню']
selected_Гарнир = ['Картофельное пюре', 'Рис с овощами', 'Гречневая каша', 'Овощи на гриле', '🔙Основное меню']
selected_Комплексные_обеды = ['Традиционный уют', 'Средиземноморский вкус', 'Гурманский рай', '🔙Выбор раздела']
selected_Напитки_и_десерты = ['Горячие напитки', 'Холодные напитки', 'Десерты', '🔙Выбор раздела']
selected_Горячие_напитки = ['Американо', 'Капучино', 'Чай чёрный/зелёный', 'Какао с маршмеллоу', '🔙Напитки и десерты']
selected_Холодные_напитки = ['Домашний лимонад', 'Морс клюквенный', 'Айсти с лимоном', 'Апельсиновый фреш', '🔙Напитки и десерты']
selected_Десерт = ['Чизкейк', 'Тирамису', 'Шоколадный фондан', 'Ягодный тарт', '🔙Напитки и десерты']

# Словарь с продуктами и ценами
products = {
    'Крем-суп из тыквы': 250,
    'Том Ям': 250,
    'Минестроне': 220,
    'Борщ': 200,
    'Цезарь с курицей': 150,
    'Греческий салат': 120,
    'Оливье': 180,
    'Салат с тунцом': 120,
    'Стейк из говядины': 350,
    'Куриное филе': 200,
    'Свинина в соусе BBQ': 250,
    'Котлеты по-домашнему': 200,
    'Картофельное пюре': 150,
    'Рис с овощами': 140,
    'Гречневая каша': 130,
    'Овощи на гриле': 180,
    'Традиционный уют': 950,
    'Средиземноморский вкус': 1070,
    'Гурманский рай': 1350,
    'Американо': 100,
    'Капучино': 150,
    'Чай чёрный/зелёный': 80,
    'Какао с маршмеллоу': 180,
    'Домашний лимонад': 150,
    'Морс клюквенный': 120,
    'Айсти с лимоном': 130,
    'Апельсиновый фреш': 200,
    'Чизкейк': 300,
    'Тирамису': 280,
    'Шоколадный фондан': 350,
    'Ягодный тарт': 250
}


user_cart = {} # Корзина пользователя
order_counter = 1 # Номер заказа


# Добавление в корзину
async def add_to_cart(user_id, product_name):
    """
    Добавляет товар в корзину пользователя.

    Если товар уже есть в корзине, увеличивает его количество на 1.
    Если товара нет в корзине, добавляет его с количеством 1.

    Args:
        user_id (int): ID пользователя, чья корзина будет обновлена.
        product_name (str): Название товара, который добавляется в корзину.
    """
    # Если у пользователя нет корзины, создаем её
    if user_id not in user_cart:
        user_cart[user_id] = {}

    # Если товар уже есть в корзине, увеличиваем количество
    if product_name in user_cart[user_id]:
        user_cart[user_id][product_name]['quantity'] += 1
    else:
        # Если товара нет, добавляем его с количеством 1
        user_cart[user_id][product_name] = {'price': products[product_name], 'quantity': 1}


# Отображение корзины
async def show_cart(user_id):
    """
    Отображает содержимое корзины пользователя.

    Формирует строку с описанием товаров в корзине, их количестве, цене и общей сумме.

    Args:
        user_id (int): ID пользователя, чья корзина отображается.

    Returns:
        str: Строка с описанием содержимого корзины.
    """
    # Проверяем, есть ли корзина у пользователя и есть ли товары в корзине
    if user_id not in user_cart or not user_cart[user_id]:
        return 'Ваша корзина пуста.'

    cart_text = '🛒 Ваша корзина:\n'
    total_price = 0

    # Формируем описание каждого товара в корзине
    for product, info in user_cart[user_id].items():
        quantity = info['quantity']
        price = info['price']
        cart_text += f'• {product} - {quantity} шт. x {price} руб = {quantity * price} руб\n'
        total_price += quantity * price

    # Добавляем общую сумму товаров
    cart_text += f'\n💰 Общая сумма: {total_price} руб'
    return cart_text


# Хендлеры для перехода в корзину
@router.message(F.text == 'Корзина')
async def cart_handler(message: Message):
    """
    Обрабатывает запрос пользователя на отображение корзины.

    Отправляет пользователю информацию о содержимом корзины с кнопками управления корзиной.

    Args:
        message (Message): Сообщение пользователя, содержащего запрос на отображение корзины.
    """
    cart_info = await show_cart(message.from_user.id)
    await message.reply(text=str(cart_info), reply_markup=await kb.cart_buttons())


@router.callback_query(F.data == 'selected_Перейти_в_корзину')
async def cart_handler(callback: CallbackQuery):
    """
    Обрабатывает нажатие кнопки для перехода в корзину.

    Отправляет информацию о корзине в ответ на callback запрос.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для перехода в корзину.
    """
    cart_info = await show_cart(callback.from_user.id)
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.cart_buttons())


# Выбор товара для редактирования
@router.callback_query(F.data == 'edit_quantity')
async def edit_quantity_handler(callback: CallbackQuery):
    """
    Обрабатывает запрос на редактирование количества товара в корзине.

    Проверяет, есть ли товары в корзине пользователя, и предлагает выбрать товар для редактирования.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для редактирования товара.
    """
    if callback.from_user.id not in user_cart or not user_cart[callback.from_user.id]:
        await callback.answer('Ваша корзина пуста.')
        return
    # Предлагаем выбрать товар для редактирования
    await callback.message.edit_text(
        text='Выберите товар для редактирования:',
        reply_markup=await kb.create_edit_quantity_buttons(user_cart[callback.from_user.id])
    )


# Изменение количества товара
@router.callback_query(F.data.startswith('edit_'))
async def edit_product_handler(callback: CallbackQuery):
    """
    Обрабатывает изменение количества товара в корзине.

    Позволяет увеличить или уменьшить количество товара в корзине.

    Args:callback (CallbackQuery): Callback запрос от пользователя для изменения количества товара.
    """
    # Извлекаем название товара из callback data
    product = callback.data.split('_', 1)[1]

    # Отправляем сообщение с кнопками для изменения количества
    await callback.message.edit_text(
        text=f'Изменение количества для {product}:',
        reply_markup=await kb.quantity_buttons(product)
    )


# Увеличение количества товара в корзине
@router.callback_query(F.data.startswith('increase_'))
async def increase_quantity(callback: CallbackQuery):
    """
    Обрабатывает запрос на увеличение количества товара в корзине.

    Изменяет количество выбранного товара на 1 и обновляет состояние корзины.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для увеличения количества товара.
    """
    # Извлекаем название товара из данных callback
    product = callback.data.split('_', 1)[1]

    # Увеличиваем количество товара на 1
    user_cart[callback.from_user.id][product]['quantity'] += 1

    # Отправляем подтверждение об увеличении количества
    await callback.answer('Количество увеличено.')

    # Обновляем клавиатуру с кнопками для изменения количества товара
    await callback.message.edit_reply_markup(reply_markup=await kb.quantity_buttons(product))


# Уменьшение количества товара в корзине
@router.callback_query(F.data.startswith('decrease_'))
async def decrease_quantity(callback: CallbackQuery):
    """
    Обрабатывает запрос на уменьшение количества товара в корзине.

    Если количество товара больше 1, уменьшает его на 1.
    Если количество товара становится 0, удаляет товар из корзины.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для уменьшения количества товара.
    """
    # Извлекаем название товара из данных callback
    product = callback.data.split('_', 1)[1]

    # Проверяем, если количество товара больше 1, уменьшаем его на 1
    if user_cart[callback.from_user.id][product]['quantity'] > 1:
        user_cart[callback.from_user.id][product]['quantity'] -= 1
    else:
        # Если количество товара 1, удаляем его из корзины
        del user_cart[callback.from_user.id][product]

    # Отправляем подтверждение об изменении количества
    await callback.answer('Количество уменьшено.')

    # Если товар всё ещё есть в корзине, обновляем кнопки
    if product in user_cart[callback.from_user.id]:
        await callback.message.edit_reply_markup(reply_markup=await kb.quantity_buttons(product))
    else:
        # Если товар удалён, отправляем сообщение о его удалении и предлагаем редактирование корзины
        await callback.answer('Товар удалён из корзины.')
        await callback.message.edit_text(text='Выберите товар для редактирования:',
                                         reply_markup=await kb.create_edit_quantity_buttons(
                                             user_cart[callback.from_user.id]))


# Обработка оплаты
@router.callback_query(F.data == 'pay_cart')
async def pay_cart_handler(callback: CallbackQuery):
    """
    Обрабатывает запрос на оплату корзины.

    Суммирует стоимость всех товаров в корзине, выводит информацию о заказе
    и подтверждает оплату, после чего очищает корзину.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для оплаты корзины.
    """
    global order_counter
    user_id = callback.from_user.id
    username = callback.from_user.first_name or 'Неизвестно'  # Имя пользователя или 'Неизвестно', если оно не указано
    cart_content = user_cart.get(user_id)

    # Проверка, есть ли товары в корзине
    if not cart_content:
        await callback.answer('Корзина пуста, нечего оплачивать.')
        return

    # Суммируем стоимость товаров в корзине
    total_price = sum(item['quantity'] * item['price'] for item in cart_content.values())

    # Формируем текст с деталями заказа
    order_details = '\n'.join(
        f"- {product}: {info['quantity']} шт. x {info['price']} руб = {info['quantity'] * info['price']} руб"
        for product, info in cart_content.items()
    )

    # Формируем информацию для продавца о новом заказе
    order_info = (f"У вас новый заказ:\n"
                  f"Номер заказа: {order_counter}\n"
                  f"Имя покупателя: {username}\n"
                  f"ID покупателя: {user_id}\n"
                  f"Состав заказа:\n{order_details}\n"
                  f"Общая стоимость: {total_price} руб\n")

    # Выводим информацию о заказе в консоль
    print(order_info)# Очищаем корзину пользователя после оформления заказа
    user_cart[user_id] = {}

    # Увеличиваем номер заказа для следующего
    order_number = order_counter
    order_counter += 1

    # Подтверждаем оплату и отправляем информацию о номере заказа
    await callback.message.edit_text(text=f'Спасибо за оплату! Ваш номер заказа: {order_number}',
                                     reply_markup=await kb.to_new_order())


# Очистка корзины
@router.callback_query(F.data == 'clear_cart')
async def clear_cart_handler(callback: CallbackQuery):
    """
    Обрабатывает запрос на очистку корзины.

    Отображает пользователю подтверждение о том, что корзина будет очищена.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для очистки корзины.
    """
    # Отправляем пользователю подтверждение очистки корзины
    await callback.message.edit_text(text='Вы уверены, что хотите очистить корзину?',
                                     reply_markup=await kb.create_clear_cart_buttons())


# Подтверждение очистки
@router.callback_query(F.data == 'confirm_clear_cart')
async def confirm_clear_cart(callback: CallbackQuery):
    """
    Подтверждает очистку корзины и очищает корзину пользователя.

    После очистки корзины отправляется сообщение о том, что корзина была очищена.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для подтверждения очистки корзины.
    """
    # Очищаем корзину пользователя
    user_cart[callback.from_user.id] = {}

    # Подтверждаем очистку корзины
    await callback.message.edit_text(text='Корзина успешно очищена.',
                                     reply_markup=await kb.added())


# Возврат в корзину
@router.callback_query(F.data == 'back_to_cart')
async def back_to_cart_handler(callback: CallbackQuery):
    """
    Обрабатывает запрос на возврат в корзину.

    Отображает информацию о содержимом корзины и позволяет вернуться к кнопкам корзины.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для возврата в корзину.
    """
    # Отображаем информацию о содержимом корзины
    cart_info = await show_cart(callback.from_user.id)

    # Обновляем сообщение с корзиной
    await callback.message.edit_text(cart_info, reply_markup=await kb.cart_buttons())


# Хендлеры для кнопки "Меню"
@router.message(F.text == 'Меню')
async def menu(message: Message):
    """
    Обрабатывает запрос на отображение меню.

    Отправляет пользователю сообщение с выбором раздела меню.

    Args:
        message (Message): Сообщение пользователя с запросом на меню.
    """
    # Отправляем сообщение с выбором раздела меню
    await message.reply(text='Выберите раздел меню', reply_markup=await kb.options())


# Хендлер для кнопки "Выбор раздела"
@router.callback_query(F.data == 'selected_🔙Выбор_раздела')
async def back_section(callback: CallbackQuery):
    """
    Обрабатывает запрос на возврат в выбор раздела меню.

    Отправляет пользователю сообщение с выбором раздела меню.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для возврата в выбор раздела меню.
    """
    # Отправляем сообщение с выбором раздела меню
    await callback.message.edit_text(text='Выберите раздел меню', reply_markup=await kb.options())


# Хендлер для кнопки "Сделать ещё заказ"
@router.callback_query(F.data == 'selected_Сделать_еще_заказ')
async def new_order(callback: CallbackQuery):
    """
    Обрабатывает запрос на создание нового заказа.

    Отправляет пользователю сообщение с выбором раздела меню для нового заказа.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для создания нового заказа.
    """
    # Отправляем сообщение с выбором раздела меню для нового заказа
    await callback.message.edit_text(text='Выберите раздел меню', reply_markup=await kb.options())


# Хендлер для кнопки "Основное меню"
@router.callback_query(F.data == 'selected_Основное_меню')
async def main_menu(callback: CallbackQuery):
    """
    Обрабатывает запрос на отображение основного меню.

    Отправляет пользователю сообщение с выбором категорий основного меню.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения основного меню.
    """
    # Отправляем сообщение о выбранном основном меню
    await callback.answer(text='Вы выбрали основное меню')

    # Отправляем сообщение с выбором категорий основного меню
    await callback.message.edit_text(text='Выберите категорию:',reply_markup=await kb.create_buttons(selected_Основное_меню))


# Хендлер для кнопки "🔙 Основное меню"
@router.callback_query(F.data == 'selected_🔙Основное_меню')
async def main_menu(callback: CallbackQuery):
    """
    Обрабатывает запрос на возвращение в основное меню.

    Отправляет пользователю сообщение с выбором категорий основного меню.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для возврата в основное меню.
    """
    # Отправляем сообщение о выбранном основном меню
    await callback.answer(text='Вы выбрали основное меню')

    # Отправляем сообщение с выбором категорий основного меню
    await callback.message.edit_text(text='Выберите категорию:',
                                     reply_markup=await kb.create_buttons(selected_Основное_меню))


# Хендлер для кнопки "Напитки и десерты"
@router.callback_query(F.data == 'selected_Напитки_и_десерты')
async def drinks_desserts(callback: CallbackQuery):
    """
    Обрабатывает запрос на отображение меню напитков и десертов.

    Отправляет пользователю сообщение с выбором напитков и десертов.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения меню напитков и десертов.
    """
    # Отправляем сообщение о выбранных напитках и десертах
    await callback.answer(text='Вы выбрали напитки и десерты')

    # Отправляем сообщение с выбором напитков или десертов
    await callback.message.edit_text(text='Выберите напиток или десерт:',
                                     reply_markup=await kb.create_buttons(selected_Напитки_и_десерты))


# Хендлер для кнопки "🔙 Напитки и десерты"
@router.callback_query(F.data == 'selected_🔙Напитки_и_десерты')
async def drinks_desserts(callback: CallbackQuery):
    """
    Обрабатывает запрос на возвращение в меню напитков и десертов.

    Отправляет пользователю сообщение с выбором напитков и десертов.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для возврата в меню напитков и десертов.
    """
    # Отправляем сообщение о выбранных напитках и десертах
    await callback.answer(text='Вы выбрали напитки и десерты')

    # Отправляем сообщение с выбором напитков или десертов
    await callback.message.edit_text(text='Выберите напиток или десерт:',
                                     reply_markup=await kb.create_buttons(selected_Напитки_и_десерты))


@router.callback_query(F.data == 'selected_Комплексные_обеды')
async def set_meals(callback: CallbackQuery):
    """
    Обрабатывает запрос на отображение комплексных обедов.

    Отправляет пользователю список доступных комплексных обедов с описанием и ценами.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для выбора комплексных обедов.
    """
    # Отправляем пользователю информацию о комплексных обедах
    await callback.answer(text='Вы выбрали комплексные обеды')
    await callback.message.edit_text(text='''Комплексный обед №1 - 
Традиционный уют
Состав:
1. Борщ (400 мл)
2. Цезарь с курицей (200 г)
3. Куриное филе (200 г)
4. Картофельное пюре (200 г)

Цена: 950 руб.

Комплексный обед №2 - 
Средиземноморский вкус
Состав:
1. Крем-суп из тыквы (300 мл)
2. Греческий салат (250 г)
3. Свинина в соусе BBQ (250 г)
4. Рис с овощами (180 г)

Цена: 1070 руб.

Комплексный обед №3 - 
Гурманский рай
Состав:
1. Том Ям (350 мл)
2. Салат Оливье (220 г)
3. Стейк из говядины (250 г)
4. Овощи на гриле (220 г)

Цена: 1350 руб.''', reply_markup=await kb.create_buttons(selected_Комплексные_обеды))


@router.callback_query(F.data == 'selected_Традиционный_уют')
async def add_1(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление комплексного обеда "Традиционный уют" в корзину.

    Добавляет выбранный обед в корзину пользователя и отображает обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления обеда "Традиционный уют" в корзину.
    """
    # Добавляем обед в корзину
    await add_to_cart(callback.from_user.id, 'Традиционный уют')

    # Получаем и отображаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление в корзину и обновляем сообщение
    await callback.answer(text='Традиционный уют добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Средиземноморский_вкус')
async def add_2(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление комплексного обеда "Средиземноморский вкус" в корзину.

    Добавляет выбранный обед в корзину пользователя и отображает обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления обеда "Средиземноморский вкус" в корзину.
    """
    # Добавляем обед в корзину
    await add_to_cart(callback.from_user.id, 'Средиземноморский вкус')

    # Получаем и отображаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление в корзину и обновляем сообщение
    await callback.answer(text='Средиземноморский вкус добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Гурманский_рай')
async def add_3(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление комплексного обеда "Гурманский рай" в корзину.

    Добавляет выбранный обед в корзину пользователя и отображает обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления обеда "Гурманский рай" в корзину.
    """
    # Добавляем обед в корзину
    await add_to_cart(callback.from_user.id, 'Гурманский рай')

    # Получаем и отображаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление в корзину и обновляем сообщение
    await callback.answer(text='Гурманский рай добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Суп')
async def soup(callback: CallbackQuery):
    """
    Обрабатывает запрос пользователя на выбор супов.

    Отправляет пользователю информацию о доступных супах с их описанием, объемом порции и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка супов.
    """
    # Информируем пользователя, что они выбрали супы
    await callback.answer(text='Вы выбрали супы')

    # Отправляем сообщение с деталями супов и кнопками для добавления в корзину
    await callback.message.edit_text(text='''Крем-суп из тыквы
Нежный крем-суп из запечённой тыквы, с добавлением сливок и лёгкими нотками мускатного ореха.
Объем порции: 300 мл
Цена: 250 руб. 

Том Ям
Тайский острый суп с креветками и грибами в кокосовом молоке, с ароматом лайма и лемонграсса
Объем порции: 350 мл
Цена: 250 руб. 

Минестроне
Итальянский овощной суп с пастой или рисом, приготовленный на основе сезонных овощей
Объем порции: 400 мл
Цена: 220 руб. 

Борщ
Классический свекольный суп на мясном бульоне с капустой и картофелем, подаётся со сметаной
Объем порции: 400 мл
Цена: 200 руб. ''', reply_markup=await kb.create_buttons(selected_Суп))


@router.callback_query(F.data == 'selected_Крем-суп_из_тыквы')
async def add_4(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление крем-супа из тыквы в корзину.

    Добавляет крем-суп из тыквы в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления крем-супа из тыквы в корзину.
    """
    # Добавляем крем-суп из тыквы в корзину
    await add_to_cart(callback.from_user.id, 'Крем-суп из тыквы')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Крем-суп из тыквы добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Том_Ям')
async def add_5(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление супа "Том Ям" в корзину.

    Добавляет суп "Том Ям" в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления супа "Том Ям" в корзину.
    """
    # Добавляем суп Том Ям в корзину
    await add_to_cart(callback.from_user.id, 'Том Ям')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Том Ям добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Минестроне')
async def add_6(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление супа "Минестроне" в корзину.

    Добавляет суп "Минестроне" в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления супа "Минестроне" в корзину.
    """
    # Добавляем суп Минестроне в корзину
    await add_to_cart(callback.from_user.id, 'Минестроне')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Минестроне добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Борщ')
async def add_7(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление супа "Борщ" в корзину.

    Добавляет суп "Борщ" в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления супа "Борщ" в корзину.
    """
    # Добавляем суп Борщ в корзину
    await add_to_cart(callback.from_user.id, 'Борщ')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Борщ добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Салат')
async def salad(callback: CallbackQuery):
    """
    Обрабатывает запрос пользователя на выбор салатов.

    Отправляет пользователю информацию о доступных салатах с их описанием, объемом порции и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка салатов.
    """
    # Информируем пользователя, что они выбрали категорию салатов
    await callback.answer(text='Вы выбрали салаты')

    # Отправляем сообщение с деталями салатов и кнопками для добавления в корзину
    await callback.message.edit_text(text='''Цезарь с курицей
Классический салат с куриной грудкой, листьями салата ромэн, пармезаном, сухариками и соусом цезарь.
Объем порции: 200 г
Цена: 150 руб. 

Греческий салат
Свежие овощи (помидоры, огурцы, болгарский перец) с оливками, фетой и орегано, заправленный оливковым маслом.
Объем порции: 250 г
Цена: 120 руб. 

Оливье
Традиционный салат с отварным картофелем, морковью, солёными огурцами, яйцом, горошком и майонезом.
Объем порции: 220 г
Цена: 100 руб. 

Салат с тунцом
Лёгкий салат из микса зелёных листьев, тунца, отварных яиц, черри и оливок с оливковым маслом.
Объем порции: 180 г
Цена: 120 руб. ''', reply_markup=await kb.create_buttons(selected_Салат))


@router.callback_query(F.data == 'selected_Цезарь_с_курицей')
async def add_8(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление салата "Цезарь с курицей" в корзину.

    Добавляет салат "Цезарь с курицей" в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления салата "Цезарь с курицей" в корзину.
    """
    # Добавляем салат Цезарь с курицей в корзину
    await add_to_cart(callback.from_user.id, 'Цезарь с курицей')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Цезарь с курицей добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Греческий_салат')
async def add_9(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление греческого салата в корзину.

    Добавляет греческий салат в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления греческого салата в корзину.
    """
    # Добавляем греческий салат в корзину
    await add_to_cart(callback.from_user.id, 'Греческий салат')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Греческий салат добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Оливье')
async def add_10(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление салата "Оливье" в корзину.

    Добавляет салат "Оливье" в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления салата "Оливье" в корзину.
    """
    # Добавляем салат Оливье в корзину
    await add_to_cart(callback.from_user.id, 'Оливье')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Оливье добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Салат_с_тунцом')
async def add_11(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление салата с тунцом в корзину.

    Добавляет салат с тунцом в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления салата с тунцом в корзину.
    """
    # Добавляем салат с тунцом в корзину
    await add_to_cart(callback.from_user.id, 'Салат с тунцом')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Салат с тунцом добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Мясное_блюдо')
async def meat(callback: CallbackQuery):
    """
    Обрабатывает запрос пользователя на выбор мясных блюд.

    Отправляет пользователю информацию о доступных мясных блюдах с их описанием, объемом порции и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка мясных блюд.
    """
    # Информируем пользователя, что они выбрали мясные блюда
    await callback.answer(text='Вы выбрали мясные блюда')

    # Отправляем сообщение с деталями мясных блюд и кнопками для добавления в корзину
    await callback.message.edit_text(text='Вы выбрали мясные блюда')
    await callback.message.edit_text(text='''Стейк из говядины
Сочный стейк средней прожарки, подается с ароматным травяным маслом или соусом.
Объем порции: 250 г
Цена: 350 руб. 

Куриное филе
Запечённое куриное филе с травами и специями, подаётся с лёгким соусом.
Объем порции: 200 г
Цена: 200 руб. 

Свинина в соусе BBQ
Обжаренные кусочки свинины, тушенные в пряном соусе BBQ до мягкости и сочности.
Объем порции: 250 г
Цена: 250 руб. 

Котлеты по-домашнему
Домашние мясные котлеты из говядины и свинины, обжаренные до золотистой корочки.
Объем порции: 180 г
Цена: 200 руб. ''', reply_markup=await kb.create_buttons(selected_Мясное_блюдо))


@router.callback_query(F.data == 'selected_Стейк_из_говядины')
async def add_12(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление стейка из говядины в корзину.

    Добавляет стейк из говядины в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления стейка из говядины в корзину.
    """
    # Добавляем стейк из говядины в корзину
    await add_to_cart(callback.from_user.id, 'Стейк из говядины')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Стейк из говядины добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Куриное_филе')
async def add_13(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление куриного филе в корзину.

    Добавляет куриное филе в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления куриного филе в корзину.
    """
    # Добавляем куриное филе в корзину
    await add_to_cart(callback.from_user.id, 'Куриное филе')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Куриное филе добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Свинина_в_соусе_BBQ')
async def add_14(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление свинины в соусе BBQ в корзину.

    Добавляет свинину в соусе BBQ в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления свинины в соусе BBQ в корзину.
    """
    # Добавляем свинину в соусе BBQ в корзину
    await add_to_cart(callback.from_user.id, 'Свинина в соусе BBQ')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Свинина в соусе BBQ добавлена в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Котлеты_по-домашнему')
async def add_15(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление котлет по-домашнему в корзину.

    Добавляет котлеты по-домашнему в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления котлет по-домашнему в корзину.
    """
    # Добавляем котлеты по-домашнему в корзину
    await add_to_cart(callback.from_user.id, 'Котлеты по-домашнему')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Котлеты по-домашнему добавлены в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Домашний_лимонад')
async def add_24(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление домашнего лимонада в корзину.

    Добавляет домашний лимонад в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления домашнего лимонада в корзину.
    """
    # Добавляем домашний лимонад в корзину
    await add_to_cart(callback.from_user.id, 'Домашний лимонад')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Домашний лимонад добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Морс_клюквенный')
async def add_25(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление морса клюквенного в корзину.

    Добавляет морс клюквенный в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления морса клюквенного в корзину.
    """
    # Добавляем морс клюквенный в корзину
    await add_to_cart(callback.from_user.id, 'Морс клюквенный')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Морс клюквенный добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Айсти_с_лимоном')
async def add_26(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление Айсти с лимоном в корзину.

    Добавляет Айсти с лимоном в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления Айсти с лимоном в корзину.
    """
    # Добавляем Айсти с лимоном в корзину
    await add_to_cart(callback.from_user.id, 'Айсти с лимоном')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Айсти с лимоном добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Апельсиновый_фреш')
async def add_27(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление апельсинового фреша в корзину.

    Добавляет апельсиновый фреш в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления апельсинового фреша в корзину.
    """
    # Добавляем апельсиновый фреш в корзину
    await add_to_cart(callback.from_user.id, 'Апельсиновый фреш')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Апельсиновый фреш добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Горячие_напитки')
async def hot_drinks(callback: CallbackQuery):
    """
    Обрабатывает запрос пользователя на выбор горячих напитков.

    Отправляет пользователю список горячих напитков с их описанием, объемом и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка горячих напитков.
    """
    # Информируем пользователя, что они выбрали горячие напитки
    await callback.answer(text='Вы выбрали горячие напитки')

    # Отправляем информацию о горячих напитках
    await callback.message.edit_text(text='''Американо
Классический черный кофе средней крепости, приготовленный на основе эспрессо.Объем: 200 мл
Цена: 100 руб. 

Капучино
Кофе с мягким вкусом, покрытый нежной пенкой из взбитого молока.
Объем: 250 мл
Цена: 150 руб. 

Чай чёрный/зелёный
Классический чёрный или зелёный чай, заваренный из натуральных чайных листьев.
Объем: 300 мл
Цена: 80 руб. 

Какао с маршмеллоу
Горячий шоколадный напиток, украшенный мягкими маршмеллоу, для сладкого уюта.
Объем: 250 мл
Цена: 180 руб. ''', reply_markup=await kb.create_buttons(selected_Горячие_напитки))


@router.callback_query(F.data == 'selected_Американо')
async def add_28(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление Американо в корзину.

    Добавляет Американо в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления Американо в корзину.
    """
    # Добавляем Американо в корзину
    await add_to_cart(callback.from_user.id, 'Американо')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Американо добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Капучино')
async def add_29(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление Капучино в корзину.

    Добавляет Капучино в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления Капучино в корзину.
    """
    # Добавляем Капучино в корзину
    await add_to_cart(callback.from_user.id, 'Капучино')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Капучино добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Чай_чёрный/зелёный')
async def add_30(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление Чая чёрного или зелёного в корзину.

    Добавляет Чай чёрный/зелёный в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления чая чёрного/зелёного в корзину.
    """
    # Добавляем Чай чёрный/зелёный в корзину
    await add_to_cart(callback.from_user.id, 'Чай чёрный/зелёный')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Чай чёрный/зелёный добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Какао_с_маршмеллоу')
async def add_31(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление Какао с маршмеллоу в корзину.

    Добавляет Какао с маршмеллоу в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления Какао с маршмеллоу в корзину.
    """
    # Добавляем Какао с маршмеллоу в корзину
    await add_to_cart(callback.from_user.id, 'Какао с маршмеллоу')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Какао с маршмеллоу добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Десерты')
async def desserts(callback: CallbackQuery):
    """
    Отправляет пользователю информацию о десертах, доступных для выбора.

    При выборе десертов, пользователю показывается список доступных десертов с их описанием, объемом и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка десертов.
    """
    # Информируем пользователя о том, что они выбрали десерты
    await callback.answer(text='Вы выбрали десерты')

    # Отправляем информацию о десертах
    await callback.message.edit_text(text='''Чизкейк Нью-Йорк
Классический чизкейк на основе сливочного сыра, с мягкой текстурой и печёной корочкой.
Объем порции: 150 г 
Цена: 300 руб. 

Тирамису
Итальянский десерт с кремом маскарпоне, пропитанный кофе и украшенный какао.
Объем порции: 120 г
Цена: 280 руб. 

Шоколадный фондан
Тёплый шоколадный пирог с жидким центром, подаётся с шариком ванильного мороженого.
Объем порции: 120 г 
Цена: 350 руб. 

Ягодный тарт
Лёгкий пирог с основой из песочного теста и начинкой из свежих ягод и крема.
Объем порции: 130 г 
Цена: 250 руб. ''', reply_markup=await kb.create_buttons(selected_Десерт))


@router.callback_query(F.data == 'selected_Чизкейк')
async def add_20(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление чизкейка в корзину.

    Добавляет чизкейк в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления чизкейка в корзину.
    """
    # Добавляем чизкейк в корзину
    await add_to_cart(callback.from_user.id, 'Чизкейк')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Чизкейк добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Тирамису')
async def add_21(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление тирамису в корзину.

    Добавляет тирамису в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления тирамису в корзину.
    """
    # Добавляем тирамису в корзину
    await add_to_cart(callback.from_user.id, 'Тирамису')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Тирамису добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Шоколадный_фондан')
async def add_22(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление шоколадного фондана в корзину.

    Добавляет шоколадный фондан в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления шоколадного фондана в корзину.
    """
    # Добавляем шоколадный фондан в корзину
    await add_to_cart(callback.from_user.id, 'Шоколадный фондан')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Шоколадный фондан добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Ягодный_тарт')
async def add_23(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление ягодного тарта в корзину.

    Добавляет ягодный тарт в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления ягодного тарта в корзину.
    """
    # Добавляем ягодный тарт в корзину
    await add_to_cart(callback.from_user.id, 'Ягодный тарт')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Ягодный тарт добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Холодные_напитки')
async def cold_drinks(callback: CallbackQuery):
    """
    Отправляет пользователю информацию о холодных напитках, доступных для выбора.

    При выборе холодных напитков пользователю показывается список доступных напитков с их описанием, объемом и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка холодных напитков.
    """
    # Информируем пользователя о том, что они выбрали холодные напитки
    await callback.answer(text='Вы выбрали холодные напитки')

    # Отправляем информацию о холодных напитках
    await callback.message.edit_text(text='''Домашний лимонад
Освежающий лимонад с мятой, лимоном и натуральными фруктовыми добавками.
Объем: 300 мл
Цена: 150 руб. 

Морс клюквенный
Классический клюквенный морс, приготовленный из свежих ягод и слегка подслащенный.
Объем: 250 мл
Цена: 120 руб. 

Айсти с лимоном
Холодный черный чай с добавлением свежего лимона и мяты для бодрости.
Объем: 300 мл
Цена: 130 руб. 

Апельсиновый фреш
Свежевыжатый сок из апельсинов для быстрого заряда витаминами и энергией.
Объем: 200 мл
Цена: 200 руб.  ''', reply_markup=await kb.create_buttons(selected_Холодные_напитки))


@router.callback_query(F.data == 'selected_Домашний_лимонад')
async def add_24(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление домашнего лимонада в корзину.

    Добавляет домашний лимонад в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления домашнего лимонада в корзину.
    """
    # Добавляем домашний лимонад в корзину
    await add_to_cart(callback.from_user.id, 'Домашний лимонад')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Домашний лимонад добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Морс_клюквенный')
async def add_25(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление клюквенного морса в корзину.

    Добавляет клюквенный морс в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления морса клюквенного в корзину.
    """
    # Добавляем морс клюквенный в корзину
    await add_to_cart(callback.from_user.id, 'Морс клюквенный')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Морс клюквенный добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Айсти_с_лимоном')
async def add_26(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление айсти с лимоном в корзину.

    Добавляет айсти с лимоном в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления айсти с лимоном в корзину.
    """
    # Добавляем айсти с лимоном в корзину
    await add_to_cart(callback.from_user.id, 'Айсти с лимоном')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Айсти с лимоном добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Апельсиновый_фреш')
async def add_27(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление апельсинового фреша в корзину.

    Добавляет апельсиновый фреш в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления апельсинового фреша в корзину.
    """
    # Добавляем апельсиновый фреш в корзину
    await add_to_cart(callback.from_user.id, 'Апельсиновый фреш')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Апельсиновый фреш добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Горячие_напитки')
async def hot_drinks(callback: CallbackQuery):
    """
    Отправляет пользователю информацию о горячих напитках, доступных для выбора.

    При выборе горячих напитков пользователю показывается список доступных напитков с их описанием, объемом и ценой.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для отображения списка горячих напитков.
    """
    # Информируем пользователя о том, что он выбрал горячие напитки
    await callback.answer(text='Вы выбрали горячие напитки')

    # Отправляем информацию о горячих напитках
    await callback.message.edit_text(text='''Американо
Классический черный кофе средней крепости, приготовленный на основе эспрессо.
Объем: 200 мл
Цена: 100 руб. 

Капучино
Кофе с мягким вкусом, покрытый нежной пенкой из взбитого молока.
Объем: 250 мл
Цена: 150 руб. 

Чай чёрный/зелёный
Классический чёрный или зелёный чай, заваренный из натуральных чайных листьев.
Объем: 300 мл
Цена: 80 руб. 

Какао с маршмеллоу
Горячий шоколадный напиток, украшенный мягкими маршмеллоу, для сладкого уюта.
Объем: 250 мл
Цена: 180 руб. ''', reply_markup=await kb.create_buttons(selected_Горячие_напитки))


@router.callback_query(F.data == 'selected_Американо')
async def add_28(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление американо в корзину.

    Добавляет американо в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления американо в корзину.
    """
    # Добавляем американо в корзину
    await add_to_cart(callback.from_user.id, 'Американо')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Американо добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Капучино')
async def add_29(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление капучино в корзину.

    Добавляет капучино в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления капучино в корзину.
    """
    # Добавляем капучино в корзину
    await add_to_cart(callback.from_user.id, 'Капучино')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Капучино добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Чай_чёрный/зелёный')
async def add_30(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление чая чёрного или зелёного в корзину.

    Добавляет чай чёрный/зелёный в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления чая чёрного/зелёного в корзину.
    """
    # Добавляем чай чёрный/зелёный в корзину
    await add_to_cart(callback.from_user.id, 'Чай чёрный/зелёный')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Чай чёрный/зелёный добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Какао_с_маршмеллоу')
async def add_31(callback: CallbackQuery):
    """
    Обрабатывает запрос на добавление какао с маршмеллоу в корзину.

    Добавляет какао с маршмеллоу в корзину пользователя и отправляет обновленную информацию о корзине.

    Args:
        callback (CallbackQuery): Callback запрос от пользователя для добавления какао с маршмеллоу в корзину.
    """
    # Добавляем какао с маршмеллоу в корзину
    await add_to_cart(callback.from_user.id, 'Какао с маршмеллоу')

    # Получаем обновленную информацию о корзине
    cart_info = await show_cart(callback.from_user.id)

    # Подтверждаем добавление и обновляем сообщение
    await callback.answer(text='Какао с маршмеллоу добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())
