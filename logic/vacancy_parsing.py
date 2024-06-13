import requests
from bs4 import BeautifulSoup


def get_vacancies(query):
    vacancy_core_url = f'https://hh.kz/search/vacancy?text={query}&area=40'
    print(vacancy_core_url)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    page = requests.get(vacancy_core_url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    vacancies = soup.find_all(
        "div", class_='serp-item_link vacancy-card-container--OwxCdOj5QlSlCBZvSggS vacancy-card_simple--xFe6Vn6pgjyHcFozfcLy')

    results = []
    for vacancy in vacancies:
        vacancy_link_tag = vacancy.find("a", class_='bloko-link')
        vacancy_link = vacancy_link_tag['href'] if vacancy_link_tag else None

        vacancy_title = vacancy_link_tag.text if vacancy_link_tag else 'Нет информации'

        vacancy_city_tag = vacancy.find(
            "span", class_='bloko-text', attrs={'data-qa': 'vacancy-serp__vacancy-address'})
        vacancy_city = vacancy_city_tag.text if vacancy_city_tag else 'Нет информации'

        company_name_tag = vacancy.find(
            "a", class_='bloko-link', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        company_name = company_name_tag.text if company_name_tag else 'Нет информации'

        results.append({
            'link': vacancy_link,
            'title': vacancy_title,
            'city': vacancy_city,
            'company': company_name
        })

    return results
