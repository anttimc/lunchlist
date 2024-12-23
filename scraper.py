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
 """<a href="#vl" title="Vähälaktoosinen" class="diet diet-vl">vl   </a>""":  """<span style="color:blue"> VL </span>""",
 """<a href="#l" title="Laktoositon" class="diet diet-l">l  </a>""": """<span style="color:blue"> L </span>""",
 """<a href="#g" title="Gluteeniton" class="diet diet-g">g </a>""": """<span style="color:orange"> G </span>""",
 """<a href="#m" title="Maidoton" class="diet diet-m">m</a>""": """<span style="color:blue"> M </span>""",
 """ veg """: """<span style="color:green"> Veg </span>""",
 """<span class="allergen">l</span>""": """<span style="color:blue">L </span>""",
 """<span class="allergen">g</span>""": """<span style="color:orange"> G </span>""",
 """<span class="allergen">ve</span>""": """<span style="color:green"> Veg </span>""",
 """ veg""": """<span style="color:green"> Veg </span>""",
 """ ve""": """<span style="color:green"> Veg </span>""",
}

def get_menu(url, day_of_week=0):
    try:
        page = requests.get(url)
    except requests.exceptions.ConnectionError:
        return E.DIV(E.P('lounaat.info unreachable'))
    tree = html.fromstring(page.content)
    menu = tree.xpath("//*[@id='menu']")
    return menu[0][day_of_week]

def get_bax_menu(week_number, day_of_week=0):
    url = 'https://kanresta.fi/ravintolat/ravintola-bax/'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    menu = tree.xpath(f"//*[@id='week-{week_number}']//div[@class='weekday-block']")
    try:
        element = menu[day_of_week]
    except Exception:
        return E.DIV(E.P(E.B('Not available'))) 
    for el in element[1:]:
        el.tag = 'li'
    return E.DIV(
        E.P(E.B(element[0].text)),
        E.UL(*element[1:])
    )


def get_akseli_menu(day_of_week=0):
    url = 'https://www.ninankeittio.fi/helsinki-ilmala-akseli/'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    menu = tree.xpath("//*[@id='lounaslista']/div/div/div[2]/div/div[2]")[0]
    # The menu is a list of paragraphs and lists
    # The fist paragrah is the week, next ones day + lunchlist
    return E.DIV(*menu[1 + 2*day_of_week:1 + 2*(day_of_week+1)])


def get_lang(item, lang='fi'):
    return item[lang] if item[lang] is not None else ''

def parse_dylan_json(json_dict, day_of_week, lang='fi'):
    menu = json_dict['data']['week']['days'][day_of_week+1]['lunches']
    day_name = json_dict['data']['week']['days'][day_of_week+1]['dayName'][lang]
    return E.DIV(
        E.P(E.B(day_name)),
        E.UL(*[E.LI(
        get_lang(lunch['title'], lang) + ' ' + lunch['normalPrice']['price'] + ('€'  if lunch['normalPrice']['price'] != '' else ''),
        ) for lunch in menu[1:]])
    )


def get_dylan_luft_menu(day_of_week=0):
    url = 'https://europe-west1-luncher-7cf76.cloudfunctions.net/api/v1/week/5843f3ec-6a2c-49ba-ba3e-b384f6c996f1/active?language=fi'
    json_dict = requests.get(url).json()
    return E.DIV(
        parse_dylan_json(json_dict, day_of_week, 'fi'),
        parse_dylan_json(json_dict, day_of_week, 'en')
    )

def get_menus(names, day_of_week, week_number):
    menus = {}
    for name in names:
        menus[name] = (
            get_bax_menu(week_number, day_of_week) if name == 'bax' else
            get_akseli_menu(day_of_week) if name == 'ravintola-akseli' else
            get_dylan_luft_menu(day_of_week) if name == 'dylan-luft' else
            get_menu(get_url(name), day_of_week=day_of_week)
        )
    return menus

def create_menu_page(menus, weekday_name=0):
    menu_page = E.HTML(
        E.HEAD(
            E.TITLE(f'Lunch: {weekday_name}'),
            E.LINK(rel='stylesheet', href='bax.css', type='text/css', media='all'),
            E.META(name='viewport', content="width=device-width, initial-scale=1")
        ),
        E.BODY(*[
            E.DIV(
            E.H1(display_names[key]),
            value
            ) for key, value in menus.items()
        ])
    )
    return menu_page


if __name__ == '__main__':
    weekday = min(datetime.datetime.today().weekday(), 4)
    weekday_name = datetime.datetime.today().strftime("%A")
    week_number = datetime.datetime.today().isocalendar().week

    menu_page = create_menu_page(
        get_menus(
            ['ravintola-akseli', 'bax', 'dylan-luft'],
            day_of_week=weekday,
            week_number=week_number
            ), 
        weekday_name,
        )


    menu_str = html.tostring(menu_page, pretty_print=True, encoding='utf-8').decode('utf-8')

    #for key, value in dietary_mappings.items():
    #    menu_str = menu_str.replace(key, value)
    
    with open('index.html', 'w') as f:
       f.write(menu_str)
