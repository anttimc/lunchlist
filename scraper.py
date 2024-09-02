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


dietary_mappings = {
 """<a href="#vl" title="Vähälaktoosinen" class="diet diet-vl">vl   </a>""":  """<span style="color:cyan"> VL </span>""",
 """<a href="#l" title="Laktoositon" class="diet diet-l">l  </a>""": """<span style="color:blue"> L </span>""",
 """<a href="#g" title="Gluteeniton" class="diet diet-g">g </a>""": """<span style="color:orange"> G </span>""",
 """<a href="#m" title="Maidoton" class="diet diet-m">m</a>""": """<span style="color:blue"> M </span>""",
 """ veg """: """<span style="color:green"> Veg </span>""",
}

def get_menu(url, day_of_week=0):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    menu = tree.xpath("//*[@id='menu']")
    return menu[0][day_of_week]

def get_menus(names, day_of_week):
    menus = {}
    for name in names:
        menus[name] = get_menu(get_url(name), day_of_week=day_of_week)
    return menus

def create_menu_page(menus, weekday_name=0):
    menu_page = E.HTML(
        E.HEAD(
            E.TITLE(f'Lunch: {weekday_name}')
        ),
        *[
            E.BODY(
            E.H1(display_names[key]),
            value
            ) for key, value in menus.items()
        ]
    )
    return menu_page


if __name__ == '__main__':
    weekday = min(datetime.datetime.today().weekday(), 4)
    weekday_name = datetime.datetime.today().strftime("%A")

    menu_page = create_menu_page(
        get_menus(
            ['ravintola-akseli', 'bax', 'dylan-luft'],
            weekday
            ), 
        weekday_name
        )


    menu_str = html.tostring(menu_page, pretty_print=True, encoding='utf-8').decode('utf-8')

    for key, value in dietary_mappings.items():
        menu_str = menu_str.replace(key, value)
    
    with open('index.html', 'w') as f:
       f.write(menu_str)
