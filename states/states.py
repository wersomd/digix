from aiogram.fsm.state import StatesGroup, State


class AddSpecialist(StatesGroup):
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
        'AddSpecialist.spec_category': 'Выберите категорию',
        'AddSpecialist.specialization': 'Введите специализацию',
        'AddSpecialist.full_name': 'Напишите ФИО',
        'AddSpecialist.city': 'Напишите город',
        'AddSpecialist.age': 'Напишите возраст',
        'AddSpecialist.gender': 'Напишите пол',
        'AddSpecialist.work_format': 'Напишите формат работы',
        'AddSpecialist.cv': 'Отправьте CV'
    }


class FindSpecialist(StatesGroup):
    query_category = State()
    query = State()

    texts = {
        'FindSpecialist.query_category': 'Выберите специализацию',
        'FindSpecialist.query': 'Напишите свой запрос',
    }


class Vacancies(StatesGroup):
    vacancy_query = State()

    texts = {
        'Vacancies.vacancy_query': 'Напишите ваш запрос'
    }
