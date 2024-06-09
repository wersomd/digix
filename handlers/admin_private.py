from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_specialist, orm_get_specialists, orm_delete_specialist, orm_get_specialist, \
    orm_update_specialist
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавить специалиста",
    "Специалисты",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    sizes=(2,),
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


class AddSpecialistForAdmin(StatesGroup):
    spec_category = State()
    specialization = State()
    full_name = State()
    city = State()
    age = State()
    gender = State()
    work_format = State()
    cv = State()

    specialist_for_change = None
    texts = {
        'AddSpecialistForAdmin:spec_category': 'Выберите специализацию',
        'AddSpecialistForAdmin:specialization': 'Напишите профессию',
        'AddSpecialistForAdmin:full_name': 'Напишите ФИО',
        'AddSpecialistForAdmin:city': 'Напишите город',
        'AddSpecialistForAdmin:age': 'Напишите возраст',
        'AddSpecialistForAdmin:gender': 'Напишите пол',
        'AddSpecialistForAdmin:work_format': 'Напишите формат работы',
        'AddSpecialistForAdmin:cv': 'Отправьте CV'
    }


@admin_router.message(Command("admin"))
async def add_specialist(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Специалисты")
async def see_specialists(message: types.Message, session: AsyncSession):
    for specialist in await orm_get_specialists(session):
        await message.answer_document(
            specialist.cv,
            caption=f'<strong>{specialist.specialization}\
                </strong>\nФИО: {specialist.full_name}\nГород: {specialist.city}\nВозраст: {specialist.age}',
            reply_markup=get_callback_btns(btns={
                'Удалить специалиста': f'delete_{specialist.id}',
                'Изменить специалиста': f'change_{specialist.id}',
            })
        )
    await message.answer("Ок, вот список специалистов!")


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_specialist(callback: types.CallbackQuery, session: AsyncSession):
    specialist_id = callback.data.split("_")[-1]
    await orm_delete_specialist(session, int(specialist_id))

    await callback.answer('Специалист удален')
    await callback.message.answer('Специалист удален!')


@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def delete_specialist_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    specialist_id = callback.data.split("_")[-1]
    specialist_for_change = await orm_get_specialist(session, int(specialist_id))

    AddSpecialistForAdmin.specialist_for_change = specialist_for_change
    await callback.answer()
    await callback.message.answer(
        "Введите специализацию: ", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSpecialistForAdmin.specialization)


@admin_router.message(StateFilter(None), F.text == "Добавить специалиста")
async def add_specialist(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите профессию: ", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(AddSpecialistForAdmin.specialization)


@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddSpecialistForAdmin.specialist_for_change:
        AddSpecialistForAdmin.specialist_for_change = None

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddSpecialistForAdmin.specialization:
        await message.answer('Предыдущего шага нет, или введите профессию или напишите "отмена"')
        return

    previous = None
    for step in AddSpecialistForAdmin.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Ок, вы вернулись к прошлому шагу \n {AddSpecialistForAdmin.texts[previous.state]}')
            return
        previous = step

    await message.answer(f"ок, вы вернулись к прошлому шагу")


@admin_router.message(AddSpecialistForAdmin.specialization, or_f(F.text, F.text == '.'))
async def add_specialization(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(specialization=AddSpecialistForAdmin.specialist_for_change.specialization)
    else:

        if len(message.text) < 4:
            await message.answer(
                'Название специализации должно быть выше 4 символа. \n Введите заново'
            )
            return

        await state.update_data(specialization=message.text)
    await message.answer("Введите ФИО:")
    await state.set_state(AddSpecialistForAdmin.full_name)


@admin_router.message(AddSpecialistForAdmin.specialization)
async def add_specialization(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите текст название специализации")


@admin_router.message(AddSpecialistForAdmin.full_name, or_f(F.text, F.text == '.'))
async def add_fullname(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(full_name=AddSpecialistForAdmin.specialist_for_change.full_name)
    else:
        await state.update_data(full_name=message.text)
    await message.answer("Напишите свой город: ")
    await state.set_state(AddSpecialistForAdmin.city)


@admin_router.message(AddSpecialistForAdmin.full_name)
async def add_fullname(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите ФИО")


@admin_router.message(AddSpecialistForAdmin.city, or_f(F.text, F.text == '.'))
async def add_city(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(city=AddSpecialistForAdmin.specialist_for_change.city)
    else:
        await state.update_data(city=message.text)
    await message.answer("Напишите свой возраст: ")
    await state.set_state(AddSpecialistForAdmin.age)


@admin_router.message(AddSpecialistForAdmin.city)
async def add_city(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите город")


@admin_router.message(AddSpecialistForAdmin.age, or_f(F.text, F.text == '.'))
async def add_age(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(age=AddSpecialistForAdmin.specialist_for_change.age)
    else:
        try:
            int(message.text)
        except ValueError:
            await message.answer('Отправьте корректное значение!')
            return
        await state.update_data(age=message.text)
    await message.answer("Отправьте пол: ", reply_markup=GENDER_KB)
    await state.set_state(AddSpecialistForAdmin.gender)


@admin_router.message(AddSpecialistForAdmin.age)
async def add_age(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите пол")


@admin_router.message(AddSpecialistForAdmin.gender, or_f(F.text, F.text == '.'))
async def add_gender(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(gender=AddSpecialistForAdmin.specialist_for_change.gender)
    else:
        await state.update_data(gender=message.text)
    await message.answer("Выберите формат работы: ", reply_markup=WORK_FORMAT_KB)
    await state.set_state(AddSpecialistForAdmin.work_format)


@admin_router.message(AddSpecialistForAdmin.gender)
async def add_gender(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите пол")


@admin_router.message(AddSpecialistForAdmin.work_format, or_f(F.text, F.text == '.'))
async def add_work_format(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(work_format=AddSpecialistForAdmin.specialist_for_change.work_format)
    else:
        await state.update_data(work_format=message.text)
    await message.answer("Отправьте CV: ", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddSpecialistForAdmin.cv)


@admin_router.message(AddSpecialistForAdmin.work_format)
async def add_work_format(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, выберите формат работы")


@admin_router.message(AddSpecialistForAdmin.cv, or_f(F.document, F.text == '.'))
async def add_cv(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == '.':
        await state.update_data(cv=AddSpecialistForAdmin.specialist_for_change.cv)

    else:
        await state.update_data(cv=message.document.file_id)

    data = await state.get_data()

    try:
        if AddSpecialistForAdmin.specialist_for_change:
            await orm_update_specialist(session, AddSpecialistForAdmin.specialist_for_change.id, data)
        else:
            await orm_add_specialist(session, data)
        await message.answer('Специалист добавлен!', reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(f'Ошибка: \n{str(e)}', reply_markup=ADMIN_KB)
        await state.clear()

    AddSpecialistForAdmin.specialist_for_change = None


@admin_router.message(AddSpecialistForAdmin.cv)
async def add_cv(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, отправьте файл")
