from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

async def main():
    return ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню'), KeyboardButton(text='Корзина')]
],
    input_field_placeholder='Выберите:')

async def options():
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Основное меню', callback_data='selected_Основное_меню')],
    [InlineKeyboardButton(text='Напитки и десерты', callback_data='selected_Напитки_и_десерты')],
    [InlineKeyboardButton(text='Комплексные обеды', callback_data='selected_Комплексные_обеды')],
])

async def added():
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Перейти в корзину', callback_data='selected_Перейти_в_корзину')],
    [InlineKeyboardButton(text='🔙Выбор раздела', callback_data='selected_🔙Выбор_раздела')]
])

async def to_new_order():
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сделать еще заказ', callback_data='selected_Сделать_еще_заказ')]
])

async def create_buttons(option):
    buttons = []
    for text in option:
        callback_data = f'selected_{text}'.replace(' ', '_')
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def cart_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать количество', callback_data='edit_quantity')],
        [InlineKeyboardButton(text='Оплатить', callback_data='pay_cart')],
        [InlineKeyboardButton(text='Очистить корзину', callback_data='clear_cart')],
    ])

async def quantity_buttons(product):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='➕', callback_data=f'increase_{product}'),
         InlineKeyboardButton(text='➖', callback_data=f'decrease_{product}')],
        [InlineKeyboardButton(text='🔙В корзину', callback_data='back_to_cart')],
    ])

async def create_edit_quantity_buttons(cart):
    buttons = [
        [InlineKeyboardButton(text=str(product), callback_data=f'edit_{product}')]
        for product in cart
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='back_to_cart')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def create_clear_cart_buttons():
    buttons = [
        [InlineKeyboardButton(text='Да', callback_data='confirm_clear_cart')],
        [InlineKeyboardButton(text='Нет', callback_data='back_to_cart')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

