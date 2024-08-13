import json
import time
import traceback
from datetime import timedelta

from libs import configuration
from libs import soup


def result_setup():
    return {"provincies": dict()}


def result_set_provincie(root, name, url):
    if not name in root["provincies"]:
        root["provincies"][name] = {
            "url": configuration.settings['url'] + url,
            "gemeenten": dict()
        }


def result_set_gemeente(root, provincie, name, url):
    if not name in root["provincies"][provincie]["gemeenten"]:
        root["provincies"][provincie]["gemeenten"][name] = {
            "url": configuration.settings['url'] + url,
            "plaatsen": dict()
        }


def result_set_plaats(root, provincie, gemeente, name, url):
    if not name in root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"]:
        root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][name] = {
            "url": configuration.settings['url'] + url,
            "postbussen": dict(),
            "wijken": dict()
        }


def result_set_postbus(root, provincie, gemeente, plaats, name, url):
    if not name in root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["postbussen"]:
        root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["postbussen"][name] = \
            configuration.settings['url'] + url


def result_set_wijk(root, provincie, gemeente, plaats, name, url):
    if not name in root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["wijken"]:
        print(f"write wijk [{name}]")
        root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["wijken"][name] = {
            "url": configuration.settings['url'] + url,
            "buurten": dict()
        }


def result_set_buurt(root, provincie, gemeente, plaats, wijk, name, url):
    if not name in root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["wijken"][wijk]["buurten"]:
        print(f"write buurt [{name}]")
        root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["wijken"][wijk]["buurten"][name] = {
            "url": configuration.settings['url'] + url,
            "postcodes": dict()
        }


def result_set_postcode(root, provincie, gemeente, plaats, wijk, buurt, name, straat, nummers, url):
    print(f"Saving postcode [{name}]")
    if not name in \
           root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["wijken"][wijk]["buurten"][buurt][
               'postcodes']:
        root["provincies"][provincie]["gemeenten"][gemeente]["plaatsen"][plaats]["wijken"][wijk]["buurten"][buurt][
            "postcodes"][name] = {"straat": straat, "nummers": nummers, "url": configuration.settings['url'] + url}


def scrape_postcode(root, provincie, gemeente, plaats, postcode, url):
    print(f"Lading postcode: [{postcode}]")
    page = soup.get_soup(configuration.settings['url'] + url)
    table = page.find('table')
    rows = table.findAll('tr')
    postcode_result = dict()

    for row in rows:
        header = str(row.find('th').text).strip()
        value = row.find('td')
        value_href = value.find('a')

        if header == 'Straat':
            if not value_href or str(value).strip() == 'Hoort bij postbussen':
                result_set_postbus(root, provincie, gemeente, plaats, postcode, url)
            else:
                postcode_result['straat'] = value_href

        elif header == 'Buurt':
            postcode_result['buurt'] = value_href

        elif header == 'Wijk':
            postcode_result['wijk'] = value_href

    if 'straat' in postcode_result:
        wijk_naam = str(postcode_result['wijk'].text).strip()
        buurt_naam = str(postcode_result['buurt'].text).strip()
        adress = str(postcode_result['straat'].text).strip().replace(" - ", "-").rsplit(' ', 1)

        result_set_wijk(root, provincie, gemeente, plaats, wijk_naam, postcode_result['wijk']['href'])
        result_set_buurt(root, provincie, gemeente, plaats, wijk_naam, buurt_naam, postcode_result['buurt']['href'])
        result_set_postcode(root, provincie, gemeente, plaats, wijk_naam, buurt_naam, postcode,
                            adress[0].strip(),
                            adress[1].strip(),
                            postcode_result['straat']['href'])

    with open("output/postal_codes.json", 'w') as outfile:
        json.dump(root, outfile, sort_keys=True, indent=4)


def scrape_postcodes(root, provincie, gemeente, plaats, url):
    page = soup.get_soup(configuration.settings['url'] + url)
    table = page.find('table', id="postcodes-table")
    rows = table.findAll('tr')
    for row in rows:
        columns = row.findAll('td')
        if columns:
            href_postcode = columns[0].find('a')
            postcode = str(href_postcode.text).strip().replace(" ", "")
            scrape_postcode(root, provincie, gemeente, plaats, postcode, href_postcode['href'])


def scrape_postal_gemeente(root, provincie, gemeente, plaats, url):
    page = soup.get_soup(configuration.settings['url'] + url)
    sections = page.findAll('section')
    for section in sections:
        if section.find('h2') and str(section.find('h2').text).startswith('Postcodenummers van'):
            for href_postcode in section.findAll('a'):
                scrape_postcodes(root, provincie, gemeente, plaats, href_postcode['href'])


def scrape_postal_gemeenten(gemeenten):
    results = result_setup()
    for gemeente in gemeenten:
        print(f"Start scraping {gemeente['name']}")
        page = soup.get_soup(configuration.settings['url'] + gemeente['url'])
        table = page.find('table')
        rows = table.find_all('tr')

        href_provincie = rows[0].find('a')
        provincie = str(href_provincie.text).strip()

        result_set_provincie(results, provincie, href_provincie['href'])
        result_set_gemeente(results, provincie, gemeente['name'], gemeente['url'])

        for href_plaats in rows[3].findAll('a'):
            plaats = str(href_plaats.text).strip()
            result_set_plaats(results, provincie, gemeente['name'], plaats, href_plaats['href'])
            scrape_postal_gemeente(results, provincie, gemeente['name'], plaats, href_plaats['href'])

    with open("output/postal_codes.json", 'w') as outfile:
        json.dump(results, outfile, sort_keys=True, indent=4)


def scrape_postal_provinces(provinces):
    results = result_setup()
    for province in provinces:
        print(f"Start scraping {province['name']}")
        page = soup.get_soup(configuration.settings['url'] + province['url'])
        result_set_provincie(results, province['name'], province['url'])

        table = page.find('table', id="postcodes-table")
        rows = table.findAll('tr')
        for row in rows:
            columns = row.findAll('td')
            if columns:
                href_postcode = columns[0].find('a')
                href_gemeente = columns[1].find('a')
                href_plaats = columns[2].find('a')

                gemeente = str(href_gemeente.text).strip()
                result_set_gemeente(results, province['name'], gemeente, href_gemeente['href'])

                plaats = str(href_plaats.text).strip()
                result_set_plaats(results, province['name'], gemeente, plaats, href_plaats['href'])
                scrape_postcodes(results, province['name'], gemeente, plaats, href_postcode['href'])

    with open("output/postal_codes.json", 'w') as outfile:
        json.dump(results, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    start_time = time.time()
    print('Starting scraping postal codes')

    try:
        configuration.init()
        if configuration.settings:
            if configuration.settings['gemeenten']:
                scrape_postal_gemeenten(configuration.settings['gemeenten'])
            elif configuration.settings['provinces']:
                scrape_postal_provinces(configuration.settings['provinces'])
    except:
        traceback.print_exc()

    print("--- %s duration ---" % timedelta(seconds=round(time.time() - start_time, 2)))
