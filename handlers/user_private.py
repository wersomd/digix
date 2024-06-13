from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Specialist, ClientQuery
from database.orm_query import orm_get_specialists_category
from kbds.reply import MAIN_BTNS, SPECIALIST_CATEGORIES, WORK_FORMAT_KB, GENDER_KB, CANCEL_KB
from logic.pdf_reader import extract_text_from_pdf
from logic.recomendation_ai import compare_texts
from states.states import FindSpecialist, AddSpecialist, Vacancies
from logic.vacancy_parsing import get_vacancies

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я Digix.Ai — ваш персональный ассистент в поиске онлайн-специалистов👨‍💻",
                         reply_markup=MAIN_BTNS
                         )


@user_private_router.message(or_f(Command('vacancy'), (F.text.lower() == 'вакансии 💼')))
async def vacancy_cmd(message: types.Message, state: FSMContext):
    await message.answer('Какая вакансия вас интересует?', reply_markup=CANCEL_KB)
    await state.set_state(Vacancies.vacancy_query)


@user_private_router.message(Vacancies.vacancy_query, F.text)
async def send_vacancies(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await cancel_handler(message, state)
        return
    await state.update_data(vacancy_query=message.text)
    await message.answer('Ищем подходящих вакансий для вас...')

    user_data = await state.get_data()
    query = user_data['vacancy_query']
    vacancies = get_vacancies(query)

    if vacancies:

        for vacancy in vacancies[:5]:
            response = (f"Название: {vacancy['title']}\n"
                        f"Компания: {vacancy['company']}\n"
                        f"Город: {vacancy['city']}\n"
                        f"Ссылка: {vacancy['link']}")
            await message.answer(response, reply_markup=MAIN_BTNS)
    else:
        await message.answer("Вакансий по вашему запросу не найдено.", reply_markup=MAIN_BTNS)

    await state.clear()


@user_private_router.message(or_f(Command('find_specialist'), (F.text.lower() == 'я ищу специалистов 🔍')))
async def find_specialist_cmd(message: types.Message, state: FSMContext):
    await message.answer('Какая сфера вас интересует? ',
                         reply_markup=SPECIALIST_CATEGORIES)
    await state.set_state(FindSpecialist.query_category)


@user_private_router.message(FindSpecialist.query_category,
                             or_f((F.text.lower() == 'it'),
                                  (F.text.lower() == 'цифровой маркетинг'),
                                  (F.text.lower() == 'графический и веб-дизайн'),
                                  (F.text.lower() == 'копирайтинг и контент-создание'),
                                  (F.text.lower() == 'виртуальные ассистенты'),
                                  (F.text.lower() == 'переводы'),
                                  (F.text.lower() == 'образование и обучение'),
                                  (F.text.lower() == 'финансовые услуги'),
                                  (F.text.lower() == 'консультирование'),
                                  (F.text.lower() == 'it-поддержка и сетевые технологии')))
async def find_specialist_query(message: types.Message, state: FSMContext):
    await state.update_data(query_category=message.text)
    await message.answer(
        'Введите нужные Вам качество с описанием специалиста, чтобы наш ИИ смог найти для вас нужного специалиста: ',
        reply_markup=CANCEL_KB)
    await state.set_state(FindSpecialist.query)


@user_private_router.message(FindSpecialist.query, F.text)
async def answer_for_client(message: types.Message, session: AsyncSession, state: FSMContext):
    if message.text.lower() == 'отмена':
        await cancel_handler(message, state)
        return
    await state.update_data(query=message.text)
    await message.answer('Ищем подходящих специалистов для вас...')

    data = await state.get_data()
    query_category = data.get('query_category')
    client_query = data.get('query')

    specialists = await orm_get_specialists_category(session, query_category)

    query_obj = ClientQuery(
        query_category=query_category,
        query=client_query
    )

    session.add(query_obj)
    await session.commit()

    if not specialists:
        await message.answer('К сожалению, в выбранной категории нет подходящих специалистов.', reply_markup=MAIN_BTNS)
    else:
        sorted_ids, sorted_scores = await compare_texts(client_query, [
            (spec.id, spec.specialization, spec.full_name, spec.city, spec.age, spec.gender, spec.cv_text) for spec in
            specialists])
        if not sorted_ids:
            await message.answer('К сожалению, не найдено специалистов, соответствующих вашему запросу.',
                                 reply_markup=MAIN_BTNS)
        else:
            for spec_id, relevance_score in zip(sorted_ids, sorted_scores):
                specialist = next(
                    spec for spec in specialists if spec.id == spec_id)
                await message.answer_document(
                    specialist.cv,
                    caption=f"""
                    <strong>{specialist.specialization}</strong>
                    \nФИО: {specialist.full_name}
                    \nГород: {specialist.city}
                    \nВозраст: {specialist.age}
                    \n<strong>Этот кандидат вам подходят на {relevance_score * 100:.2f}%</strong>
                    """
                )

    await state.clear()


@user_private_router.message(StateFilter('*'), Command("отмена"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddSpecialist.specialist_for_change:
        AddSpecialist.specialist_for_change = None

    await state.clear()
    await message.answer("Действия отменены", reply_markup=MAIN_BTNS)


@user_private_router.message(StateFilter('*'), Command("назад"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddSpecialist.specialization:
        await message.answer('Предыдущего шага нет, или введите профессию или напишите "отмена"')
        return

    previous = None
    for step in AddSpecialist.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Ок, вы вернулись к прошлому шагу \n {AddSpecialist.texts[previous.state]}')
            return
        previous = step

    await message.answer(f"Ок, вы вернулись к прошлому шагу", reply_markup=MAIN_BTNS)
    await state.clear()


@user_private_router.message(State(None), or_f(Command('specialist'), (F.text.lower() == 'я специалист 👨🏼‍💻')))
async def specialist_cmd(message: types.Message, state: FSMContext):
    await message.answer('Для добавление в базу специалистов Digix 🔍\nВам нужно пройти 3-x этапную проверку 🔐')
    await message.answer('Выберите категорию: ', reply_markup=SPECIALIST_CATEGORIES)
    await state.set_state(AddSpecialist.spec_category)


@user_private_router.message(AddSpecialist.spec_category)
async def add_spec_category(message: types.Message, state: FSMContext):
    await state.update_data(spec_category=message.text)
    await message.answer("Введите профессию: ", reply_markup=CANCEL_KB)
    await state.set_state(AddSpecialist.specialization)


@user_private_router.message(AddSpecialist.specialization, F.text)
async def add_specialization(message: types.Message, state: FSMContext):
    await state.update_data(specialization=message.text)
    await message.answer("Введите ФИО: ")
    await state.set_state(AddSpecialist.full_name)


@user_private_router.message(AddSpecialist.specialization)
async def add_specialization_incorrect(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите текст название специализации")


@user_private_router.message(AddSpecialist.full_name, F.text)
async def add_fullname(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Напишите свой город: ")
    await state.set_state(AddSpecialist.city)


@user_private_router.message(AddSpecialist.full_name)
async def add_fullname_incorrect(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите ФИО")


@user_private_router.message(AddSpecialist.city, F.text)
async def add_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Напишите свой возраст: ")
    await state.set_state(AddSpecialist.age)


@user_private_router.message(AddSpecialist.city)
async def add_city_incorrect(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите город")


@user_private_router.message(AddSpecialist.age, F.text)
async def add_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Отправьте пол: ", reply_markup=GENDER_KB)
    await state.set_state(AddSpecialist.gender)


@user_private_router.message(AddSpecialist.age)
async def add_age_incorrect(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите пол")


@user_private_router.message(AddSpecialist.gender, F.text)
async def add_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("Выберите формат работы: ", reply_markup=WORK_FORMAT_KB)
    await state.set_state(AddSpecialist.work_format)


@user_private_router.message(AddSpecialist.gender)
async def add_gender_incorrect(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, введите пол")


@user_private_router.message(AddSpecialist.work_format, F.text)
async def add_work_format(message: types.Message, state: FSMContext):
    await state.update_data(work_format=message.text)
    await message.answer("Отправьте CV(PDF): ", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddSpecialist.cv)


@user_private_router.message(AddSpecialist.work_format)
async def add_work_format_incorrect(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, выберите формат работы")


@user_private_router.message(AddSpecialist.cv, F.document)
async def add_cv(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.document.mime_type != 'application/pdf':
        await message.answer("Пожалуйста, отправьте резюме в формате PDF.")
    else:
        file_id = message.document.file_id

        try:
            bot = message.bot  # Получаем экземпляр бота из сообщения
            cv_text = await extract_text_from_pdf(file_id, bot)
        except ValueError as e:
            await message.answer(f"Ошибка при загрузке PDF: {str(e)}")
            return

        await state.update_data(cv=file_id, cv_text=cv_text)
        data = await state.get_data()
        cv_file_id = data.get('cv')

        required_fields = ['spec_category', 'specialization',
                           'full_name', 'city', 'age', 'gender', 'work_format', 'cv']
        if not all(field in data for field in required_fields):
            await message.answer("Некоторые данные отсутствуют, пожалуйста, заполните все поля.")
            return

        # Создание объекта, если все данные на месте
        obj = Specialist(
            spec_category=data.get('spec_category'),
            specialization=data.get('specialization'),
            full_name=data.get('full_name'),
            city=data.get('city'),
            age=int(data.get('age')),
            gender=data.get('gender'),
            work_format=data.get('work_format'),
            cv=cv_file_id,
            cv_text=data.get('cv_text')
        )

        session.add(obj)
        await session.commit()
        await state.clear()

        await message.answer(
            "Поздравляем, Вы успешно добавлены в базу специалистов ✅", reply_markup=MAIN_BTNS)


@user_private_router.message(AddSpecialist.cv)
async def incorrect_input(message: types.Message):
    await message.answer("Вы ввели не допустимые данные, отправьте файл")
