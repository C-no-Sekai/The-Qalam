from bs4 import BeautifulSoup
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from db_setup import DBSetup
import os


def get_programs(link):
    results = {}
    r = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    for table in soup.find_all('tbody'):
        for row in table.find_all('tr'):
            temp = row.find('td')
            try:
                if temp.text and 'XXX' not in temp.text:
                    results[temp.text] = [temp.find_next_sibling('td').text,
                                          eval(temp.find_next_sibling('td').find_next_sibling('td').text)]
            except Exception as e:
                print('[-] Error: ', temp.text, link)
    return results


if __name__ == '__main__':
    if not os.path.exists('subjects.json'):
        r = requests.get('https://nust.edu.pk/academics/undergraduate', headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        links = [x.get('href') for x in soup.find_all('a', {'target': '_blank'}) if 'program' in x.get('href')]

        final = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(get_programs, links)
        for result in results:
            final.update(result)

        print(len(final))
        with open('subjects.json', 'w') as f:
            json.dump(final, f)

    # Feed into the db
    with open('subjects.json', 'r') as f:
        data = json.load(f)

    db = DBSetup('my_db.db')
    for program, subjects in data.items():
        db.add_subject(program, subjects[0].lower(), subjects[1])

