from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple = (2,),
):
    """
    get_keyboard(
        'Я ищу специалиста',
        'Я специалист',
        'Payments',
        'Delivery',
        'Send phone',
        placeholder='Что вас интересует?',
        request_contact=4,
        sizes=(2, 2, 1)
    )
    """

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))

        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)


MAIN_BTNS = get_keyboard(
    'Я ищу специалистов 🔍',
    'Я специалист 👨🏼‍💻',
    'Вакансии 💼',
    placeholder='Что вас интересует 🔍',
    sizes=(1,)
)

SPECIALIST_CATEGORIES = get_keyboard(
    'IT',
    'Цифровой маркетинг',
    'Графический и веб-дизайн',
    'Копирайтинг и контент-создание',
    'Виртуальные ассистенты',
    'Переводы',
    'Образование и обучение',
    'Финансовые услуги',
    'Консультирование',
    'IT-поддержка и сетевые технологии',
    'Отмена',
    sizes=(1,)
)

WORK_FORMAT_KB = get_keyboard(
    'Full-Time',
    'Temporary',
    placeholder='Выберите формат работы',
    sizes=(1, 1),
)

GENDER_KB = get_keyboard(
    'Мужской',
    'Женский',
    placeholder='Выберите пол',
    sizes=(1, 1)
)

CITIES_LIST_KB = get_keyboard(
    'Алматы',
    'Астана',
    'Шымкент',
    'Актобе',
    'Караганда',
    'Тараз',
    'Усть-Каменогорск',
    'Павлодар',
    'Атырау',
    'Семей',
    'Кызылорда',
    'Актау',
    'Костанай',
    'Уральск',
    'Туркестан',
    'Петропавловск',
    'Кокшетау',
    'Темиртау',
    'Талдыкорган',
    'Экибастуз',
    'Рудный',
    'Жезказган',
    'Жанаозен',
    placeholder='Выберите город',
    sizes=(1,)
)

cancel_kb = get_keyboard(
    'Отмена',
    sizes=(1, )
)
