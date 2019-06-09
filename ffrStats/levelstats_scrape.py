"""
Scrapes all levelstats pages to collect each level's note count.
"""

from bs4 import BeautifulSoup
import json
import mechanize

OUTPUT_FILENAME = 'levelstats.json'

# URLs
URL_BASE = 'http://www.flashflashrevolution.com'
URL_LEVELSTATS_BASE = URL_BASE + '/levelstats.php?level='

class Browser:
    def __init__(self):
        """Initialize mechanize browser"""
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0')]

    def get(self, url):
        print('GET ' + url)
        data = self.br.open(url)
        return BeautifulSoup(data, 'html.parser', from_encoding='iso-8859-1')

br = Browser()
songs = int(br.get(URL_BASE).find(id='user_control_links').text.split()[0].replace(',', ''))
data = {}
total = 0
level = 0

while total < 2:
    level += 1
    levelstats = br.get(URL_LEVELSTATS_BASE + str(level))

    # check h2 tags (there will be two if the level exists)
    h2 = levelstats('h2')
    if (len(h2)) > 1:
        name = h2[1].string
        notes = int(levelstats('table')[3]('td')[3].string)
        data[name] = notes
        total += 1
        print('%d: %s - %d' % (total, name, notes))

open(OUTPUT_FILENAME, 'w').write(json.dumps(data, indent=4, sort_keys=True))
print('Stats written to ' + OUTPUT_FILENAME)
