import requests
from lxml import html
from lxml.html import builder as E
import datetime


def get_url(name):
    return 'https://www.lounaat.info/lounas/' + name + '/helsinki' 

display_names = {
    'ravintola-akseli': 'Ravintola Akseli',
    'bax': 'Båx',
    'dylan-luft': 'Dylan Luft'
}

def get_menu(url, day_of_week=0):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    menu = tree.xpath("//*[@id='menu']")
    return menu[0][day_of_week][1]

def get_menus(names, day_of_week=0):
    menus = {}
    for name in names:
        menus[name] = get_menu(get_url(name))
    return menus

def create_menu_page(menus):
    menu_page = E.HTML(
        E.HEAD(
            E.TITLE('Menu')
        ),
        *[
            E.BODY(
            E.H1(display_names[key]),
            value
            ) for key, value in menus.items()
        ]
    )
    return menu_page

menu_page = create_menu_page(get_menus(
    ['ravintola-akseli', 'bax', 'dylan-luft'],
    datetime.datetime.today().weekday()
    ))

with open('menu.html', 'w') as f:
    f.write(html.tostring(menu_page).decode("utf-8"))
#menu_page.write('menu.html')
