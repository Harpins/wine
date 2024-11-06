import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from collections import defaultdict
from datetime import date
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas


def count_passed_years(first_year: int):
    this_year = date.today().year
    return abs(this_year-first_year)


def correct_years_text_case(years_passed):
    if years_passed < 10:
        years_stringed = '0' + str(years_passed)
    else:
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
    return groupped_wines
    

def create_parser():
    parser = argparse.ArgumentParser(
        description='''Установите входные параметры:
        -p  Путь к xlsx файлу, default='wine.xlsx'
        -s  Название листа с таблицей, default='Sheet1'
        -y  Год основания винодельни, default=1920'''
    )
    parser.add_argument(
        '-p',
        '--table_path', 
        help='Путь к xlsx файлу', 
        type=str, 
        default='wine.xlsx',
    )
    parser.add_argument(
        '-s',
        '--sheet_name', 
        help='Название листа с таблицей', 
        type=str, default='Sheet1',
    )
    parser.add_argument(
        '-y',
        '--foundation_year', 
        help='Год основания винодельни', 
        type=int, 
        default=1920
    )
    return parser
    

def main():
    
    parser = create_parser()
    args = parser.parse_args()
    table_path = args.table_path
    sheet_name = args.sheet_name
    foundation_year = args.foundation_year
   
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    years_passed = count_passed_years(foundation_year)

    wines_table = pandas.read_excel(
        table_path, 
        sheet_name=sheet_name, 
        na_values=['N/A', 'NA'], 
        keep_default_na=False,
    )
    wines_data = wines_table.to_dict(orient='records')
    groupped_wines = group_wines(wines_data)

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
