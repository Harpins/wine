from http.server import HTTPServer, SimpleHTTPRequestHandler
from collections import defaultdict
from datetime import date
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas

FOUNDATION_YEAR = 1920


def count_passed_years(first_year: int):
    this_year = date.today().year
    return abs(this_year-first_year)


def correct_years_text_case(years_passed):
    years_stringed = str(years_passed)
    last_numbers = years_stringed[-2:]
    if last_numbers[1] == '1' and last_numbers[0] != '1':
        return 'год'
    if last_numbers[1] in ['2', '3', '4'] and last_numbers[0] != '1':
        return 'года'
    return 'лет'


def group_wines(wines_list):
    categories = ['Белые вина', 'Красные вина', 'Напитки']
    groupped_wines = defaultdict(list)
    for category in categories:
        for wine in wines_list:
            if wine['wine_category'] == category:
                groupped_wines[category].append(wine)
    return (groupped_wines)


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    years_passed = count_passed_years(FOUNDATION_YEAR)

    wines_table = pandas.read_excel('wine.xlsx', sheet_name='Sheet1', na_values=[
                                    'N/A', 'NA'], keep_default_na=False)
    wines_list = wines_table.to_dict(orient='records')
    groupped_wines = group_wines(wines_list)

    rendered_page = template.render(
        groupped_wines=groupped_wines,
        years_passed=years_passed,
        years_text_case=correct_years_text_case(years_passed),
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
