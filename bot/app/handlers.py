from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import app.keyboard as kb

router = Router()

# Старт
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text=f'Здравствуйте, {message.from_user.first_name}\nЧтобы сделать заказ, нажмите "Меню"', reply_markup=await kb.main())

# Списки с полным меню
selected_Основное_меню = ['Суп', 'Гарнир', 'Салат', 'Мясное блюдо', '🔙Выбор раздела']
selected_Суп = ['Крем-суп из тыквы', 'Том Ям', 'Минестроне', 'Борщ', '🔙Основное меню']
selected_Салат = ['Цезарь с курицей', 'Греческий салат', 'Оливье', 'Салат с тунцом', '🔙Основное меню']
selected_Мясное_блюдо = ['Стейк из говядины', 'Куриное филе', 'Свинина в соусе BBQ', 'Котлеты по-домашнему', '🔙Основное меню']
selected_Гарнир = ['Картофельное пюре', 'Рис с овощами', 'Гречневая каша', 'Овощи на гриле', '🔙Основное меню']
selected_Комплексные_обеды = ['Традиционный уют', 'Средиземноморский вкус', 'Гурманский рай', '🔙Выбор раздела']
selected_Напитки_и_десерты = ['Горячие напитки', 'Холодные напитки', 'Десерты', '🔙Выбор раздела']
selected_Горячие_напитки = ['Американо', 'Капучино', 'Чай', 'Какао с маршмеллоу', '🔙Напитки и десерты']
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
    'Чай': 80,
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
    if user_id not in user_cart:
        user_cart[user_id] = {}
    if product_name in user_cart[user_id]:
        user_cart[user_id][product_name]['quantity'] += 1
    else:
        user_cart[user_id][product_name] = {'price': products[product_name], 'quantity': 1}

# Отображение корзины
async def show_cart(user_id):
    if user_id not in user_cart or not user_cart[user_id]:
        return 'Ваша корзина пуста.'
    cart_text = '🛒 Ваша корзина:\n'
    total_price = 0
    for product, info in user_cart[user_id].items():
        quantity = info['quantity']
        price = info['price']
        cart_text += f'• {product} - {quantity} шт. x {price} руб = {quantity * price} руб\n'
        total_price += quantity * price
    cart_text += f'\n💰 Общая сумма: {total_price} руб'
    return cart_text

# Хендлеры для перехода в корзину
@router.message(F.text == 'Корзина')
async def cart_handler(message: Message):
    cart_info = await show_cart(message.from_user.id)
    await message.reply(text=str(cart_info), reply_markup=await kb.cart_buttons())

@router.callback_query(F.data == 'selected_Перейти_в_корзину')
async def cart_handler(callback: CallbackQuery):
    cart_info = await show_cart(callback.from_user.id)
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.cart_buttons())

# Выбор товара для редактирования
@router.callback_query(F.data == 'edit_quantity')
async def edit_quantity_handler(callback: CallbackQuery):
    if callback.from_user.id not in user_cart or not user_cart[callback.from_user.id]:
        await callback.answer('Ваша корзина пуста.')
        return
    await callback.message.edit_text(text='Выберите товар для редактирования:',
                                     reply_markup=await kb.create_edit_quantity_buttons(user_cart[callback.from_user.id]))

# Изменение количества товара
@router.callback_query(F.data.startswith('edit_'))
async def edit_product_handler(callback: CallbackQuery):
    product = callback.data.split('_', 1)[1]
    await callback.message.edit_text(text=f'Изменение количества для {product}:',
                                     reply_markup=await kb.quantity_buttons(product))

# +
@router.callback_query(F.data.startswith('increase_'))
async def increase_quantity(callback: CallbackQuery):
    product = callback.data.split('_', 1)[1]
    user_cart[callback.from_user.id][product]['quantity'] += 1
    await callback.answer('Количество увеличено.')
    await callback.message.edit_reply_markup(reply_markup=await kb.quantity_buttons(product))

# -
@router.callback_query(F.data.startswith('decrease_'))
async def decrease_quantity(callback: CallbackQuery):
    product = callback.data.split('_', 1)[1]
    if user_cart[callback.from_user.id][product]['quantity'] > 1:
        user_cart[callback.from_user.id][product]['quantity'] -= 1
    else:
        del user_cart[callback.from_user.id][product]
    await callback.answer('Количество уменьшено.')
    if product in user_cart[callback.from_user.id]:
        await callback.message.edit_reply_markup(reply_markup=await kb.quantity_buttons(product))
    else:
        await callback.answer('Товар удалён из корзины.') # Если количество <0, то товар удаляется из корзины
        await callback.message.edit_text(text='Выберите товар для редактирования:',
                                         reply_markup=await kb.create_edit_quantity_buttons(user_cart[callback.from_user.id]))

# Оплата
@router.callback_query(F.data == 'pay_cart')
async def pay_cart_handler(callback: CallbackQuery):
    global order_counter
    user_id = callback.from_user.id
    username = callback.from_user.first_name or 'Неизвестно'
    cart_content = user_cart.get(user_id)

    if not cart_content:
        await callback.answer('Корзина пуста, нечего оплачивать.')
        return

    total_price = sum(item['quantity'] * item['price'] for item in cart_content.values())
    order_details = '\n'.join(
        f"- {product}: {info['quantity']} шт. x {info['price']} руб = {info['quantity'] * info['price']} руб"
        for product, info in cart_content.items()
    )

    # Вывод информации о заказе продавцу
    order_info = (f"У вас новый заказ:\n"
          f"Номер заказа: {order_counter}\n"
          f"Имя покупателя: {username}\n"
          f"ID покупателя: {user_id}\n"
          f"Состав заказа:\n{order_details}\n"
          f"Общая стоимость: {total_price} руб\n")

    print(order_info)

    user_cart[user_id] = {}
    order_number = order_counter
    order_counter += 1

    await callback.message.edit_text(text=f'Спасибо за оплату! Ваш номер заказа: {order_number}',
                                     reply_markup=await kb.to_new_order())

# Очистка корзины
@router.callback_query(F.data == 'clear_cart')
async def clear_cart_handler(callback: CallbackQuery):
    await callback.message.edit_text(text='Вы уверены, что хотите очистить корзину?',
                                     reply_markup=await kb.create_clear_cart_buttons())

# Подтверждение очистки
@router.callback_query(F.data == 'confirm_clear_cart')
async def confirm_clear_cart(callback: CallbackQuery):
    user_cart[callback.from_user.id] = {}
    await callback.message.edit_text(text='Корзина успешно очищена.')

@router.callback_query(F.data == 'back_to_cart')
async def back_to_cart_handler(callback: CallbackQuery):
    cart_info = await show_cart(callback.from_user.id)
    await callback.message.edit_text(cart_info, reply_markup=await kb.cart_buttons())

# Хендлеры для кнопки меню
@router.message(F.text == 'Меню')
async def menu(message: Message):
    await message.reply(text='Выберите раздел меню', reply_markup=await kb.options())

@router.callback_query(F.data == 'selected_🔙Выбор_раздела')
async def back_section(callback: CallbackQuery):
    await callback.message.edit_text(text='Выберите раздел меню', reply_markup=await kb.options())

@router.callback_query(F.data == 'selected_Сделать_еще_заказ')
async def new_order(callback: CallbackQuery):
    await callback.message.edit_text(text='Выберите раздел меню', reply_markup=await kb.options())

# Хендлеры разделов меню
@router.callback_query(F.data == 'selected_Основное_меню')
async def main_menu(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали основное меню')
    await callback.message.edit_text(text='Выберите категорию:',
                                     reply_markup=await kb.create_buttons(selected_Основное_меню))

@router.callback_query(F.data =='selected_🔙Основное_меню')
async def main_menu(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали основное меню')
    await callback.message.edit_text(text='Выберите категорию:',
                                     reply_markup=await kb.create_buttons(selected_Основное_меню))

@router.callback_query(F.data == 'selected_Напитки_и_десерты')
async def drinks_desserts(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали напитки и десерты')
    await callback.message.edit_text(text='Выберите напиток или десерт:',
                                     reply_markup=await kb.create_buttons(selected_Напитки_и_десерты))

@router.callback_query(F.data == 'selected_🔙Напитки_и_десерты')
async def drinks_desserts(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали напитки и десерты')
    await callback.message.edit_text(text='Выберите напиток или десерт:',
                                     reply_markup=await kb.create_buttons(selected_Напитки_и_десерты))

@router.callback_query(F.data == 'selected_Комплексные_обеды')
async def set_meals(callback: CallbackQuery):
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
    await add_to_cart(callback.from_user.id, 'Традиционный уют')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Традиционный уют добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Средиземноморский_вкус')
async def add_2(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Средиземноморский вкус')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Средиземноморский вкус добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Гурманский_рай')
async def add_3(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Гурманский рай')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Гурманский рай добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Суп')
async def soup(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали супы')
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
    await add_to_cart(callback.from_user.id, 'Крем-суп из тыквы')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Крем-суп из тыквы добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Том_Ям')
async def add_5(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Том Ям')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Том Ям добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Минестроне')
async def add_6(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Минестроне')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Минестроне добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Борщ')
async def add_7(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Борщ')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Борщ добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Салат')
async def salad(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали салаты')
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
    await add_to_cart(callback.from_user.id, 'Цезарь с курицей')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Цезарь с курицей добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Греческий_салат')
async def add_9(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Греческий салат')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Греческий салат добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Оливье')
async def add_10(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Оливье')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Оливье добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Салат_с_тунцом')
async def add_11(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Салат с тунцом')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Салат с тунцом добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Мясное_блюдо')
async def meat(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали мясные блюда')
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
    await add_to_cart(callback.from_user.id, 'Стейк из говядины')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Стейк из говядины добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Куриное_филе')
async def add_13(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Куриное филе')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Куриное филе добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Свинина_в_соусе_BBQ')
async def add_14(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Свинина в соусе BBQ')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Свинина в соусе BBQ добавлена в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Котлеты_по-домашнему')
async def add_15(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Котлеты по-домашнему')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Котлеты по-домашнему добавлены в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Гарнир')
async def garnish(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали гарниры')
    await callback.message.edit_text(text='''Картофельное пюре
Нежное картофельное пюре с добавлением сливок и масла.
Объем порции: 200 г
Цена: 150 руб. 

Рис с овощами
Белый рис, обжаренный с морковью, горошком и кукурузой, с лёгкими специями.
Объем порции: 180 г
Цена: 140 руб. 

Гречневая каша
Классическая гречневая каша, приготовленная на воде или бульоне, слегка посоленная.
Объем порции: 200 г
Цена: 130 руб. 

Овощи на гриле
Ассорти из обжаренных на гриле овощей: кабачки, баклажаны, перец и грибы, с добавлением специй.
Объем порции: 220 г
Цена: 180 руб. ''', reply_markup=await kb.create_buttons(selected_Гарнир))

@router.callback_query(F.data == 'selected_Картофельное_пюре')
async def add_16(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Картофельное пюре')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Картофельное пюре добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Рис_с_овощами')
async def add_17(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Рис с овощами')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Рис с овощами добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Гречневая_каша')
async def add_18(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Гречневая каша')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Гречневая каша добавлена в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Овощи_на_гриле')
async def add_19(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Овощи на гриле')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Овощи на гриле добавлены в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Десерты')
async def desserts(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали десерты')
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
Цена: 250 руб.''', reply_markup=await kb.create_buttons(selected_Десерт))

@router.callback_query(F.data == 'selected_Чизкейк')
async def add_20(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Чизкейк')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Чизкейк добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Тирамису')
async def add_21(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Тирамису')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Тирамису добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Шоколадный_фондан')
async def add_22(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Шоколадный фондан')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Шоколадный фондан добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Ягодный_тарт')
async def add_23(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Ягодный тарт')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Ягодный тарт добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())


@router.callback_query(F.data == 'selected_Холодные_напитки')
async def cold_drinks(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали холодные напитки')
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
    await add_to_cart(callback.from_user.id, 'Домашний лимонад')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Домашний лимонад добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Морс_клюквенный')
async def add_25(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Морс клюквенный')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Морс клюквенный добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Айсти_с_лимоном')
async def add_26(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Айсти с лимоном')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Айсти с лимоном добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Апельсиновый_фреш')
async def add_27(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Апельсиновый фреш')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Апельсиновый фреш добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Горячие_напитки')
async def hot_drinks(callback: CallbackQuery):
    await callback.answer(text='Вы выбрали горячие напитки')
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
    await add_to_cart(callback.from_user.id, 'Американо')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Американо добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Капучино')
async def add_29(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Капучино')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Капучино добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Чай_чёрный/зелёный')
async def add_30(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Чай чёрный/зелёный')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Чай чёрный/зелёный добавлен в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())

@router.callback_query(F.data == 'selected_Какао_с_маршмеллоу')
async def add_31(callback: CallbackQuery):
    await add_to_cart(callback.from_user.id, 'Какао с маршмеллоу')
    cart_info = await show_cart(callback.from_user.id)
    await callback.answer(text='Какао с маршмеллоу добавлено в корзину!')
    await callback.message.edit_text(text=str(cart_info), reply_markup=await kb.added())
