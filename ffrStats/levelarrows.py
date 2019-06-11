"""
Scrapes all song list pages to collect each level's arrow count.
"""

from bs4 import BeautifulSoup
import json
import mechanize

OUTPUT_FILENAME = 'levelarrows.json'

class Browser:
    def __init__(self):
        """Initialize mechanize browser"""
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0')]

    def get(self, page):
        url = 'http://www.flashflashrevolution.com/FFRStats/FFRSongs.php?page=' + str(page) + '&order_by=songname&order=ASC'
        print('GET ' + url)
        data = self.br.open(url)
        return BeautifulSoup(data, 'html.parser', from_encoding='iso-8859-1')

br = Browser()
data = {}
page = 1

while True:
    tables = br.get(page)('table', class_='data')

    if len(tables) == 0:
        break

    for table in tables:
        name = table.find('span', class_='name').text
        arrows = int(table.find('td', class_='info').text.split()[-3].replace(',', ''))
        data[name] = arrows

    page += 1

open(OUTPUT_FILENAME, 'w').write(json.dumps(data, indent=4, sort_keys=True))
print('Stats written to ' + OUTPUT_FILENAME)
