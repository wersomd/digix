import requests
from bs4 import BeautifulSoup


def get_vacancies(query):
    vacancy_core_url = f"https://hh.kz/search/vacancy?text={query}&area=40"
    print(vacancy_core_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    page = requests.get(vacancy_core_url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    vacancies = soup.find_all(
        "div", class_="vacancy-info--ieHKDTkezpEj0Gsx")

    results = []
    for vacancy in vacancies:
        vacancy_link_tag = vacancy.find("a", class_="magritte-link___b4rEM_4-3-13 magritte-link_style_neutral___iqoW0_4-3-13 magritte-link_enable-visited___Biyib_4-3-13")
        vacancy_link = vacancy_link_tag["href"] if vacancy_link_tag else "Нету ссылки"

        vacancy_title = vacancy_link_tag.text if vacancy_link_tag else "Нет информации"

        vacancy_city_tag = vacancy.find(
            "span", class_="magritte-text___pbpft_3-0-19 magritte-text_style-primary___AQ7MW_3-0-19 magritte-text_typography-label-3-regular___Nhtlp_3-0-19", attrs={"data-qa": "vacancy-serp__vacancy-address"})
        vacancy_city = vacancy_city_tag.text if vacancy_city_tag else "Нет информации"

        company_name_tag = vacancy.find(
            "a", class_="magritte-link___b4rEM_4-3-13 magritte-link_style_neutral___iqoW0_4-3-13", attrs={"data-qa": "vacancy-serp__vacancy-employer"})
        company_name = company_name_tag.text if company_name_tag else "Нет информации"

        results.append({
            "link": vacancy_link,
            "title": vacancy_title,
            "city": vacancy_city,
            "company": company_name
        })

    return results
