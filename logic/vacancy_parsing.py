import requests
from bs4 import BeautifulSoup


def get_vacancies(query):
    # Формируем URL запроса с учетом введенного пользователем запроса
    vacancy_core_url = f'https://hh.kz/search/vacancy?text={query}&area=160'

    # Заголовки для HTTP запроса
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Выполняем HTTP запрос к странице с вакансиями
    page = requests.get(vacancy_core_url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Извлекаем информацию о вакансиях
    vacancies = soup.find_all(
        "div", class_='serp-item serp-item_simple serp-item_link serp-item-redesign')

    results = []
    for vacancy in vacancies:
        # Извлекаем ссылку на вакансию
        vacancy_link_tag = vacancy.find("a", class_='bloko-link')
        vacancy_link = vacancy_link_tag['href'] if vacancy_link_tag else None

        # Извлекаем название вакансии
        vacancy_title = vacancy_link_tag.text if vacancy_link_tag else None

        # Извлекаем город
        vacancy_city_tag = vacancy.find(
            "span", class_='fake-magritte-primary-text--qmdoVdtVX3UWtBb3Q7Qj')
        vacancy_city = vacancy_city_tag.text if vacancy_city_tag else None

        # Извлекаем название компании
        company_name_tag = vacancy.find(
            "span", class_='company-info-text--O32pGCRW0YDmp3BHuNOP')
        company_name = company_name_tag.text if company_name_tag else None

        results.append({
            'link': vacancy_link,
            'title': vacancy_title,
            'city': vacancy_city,
            'company': company_name
        })

    return results
