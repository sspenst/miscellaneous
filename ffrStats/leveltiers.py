"""
Scrapes all tier requirement data.

Assumes there is an existing file in this directory named
'credentials.json' that contains a username and password:
{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}
"""

from bs4 import BeautifulSoup
import json
import mechanize

OUTPUT_FILENAME = 'leveltiers.json'

# URLs
URL_BASE = 'http://www.flashflashrevolution.com'
URL_TIERS = URL_BASE + '/FFRStats/level_tiers.php'

credentials = json.loads(open('credentials.json', 'r').read())

class Browser:
    def __init__(self):
        """Initialize mechanize browser"""
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0')]

    def login(self):
        print('GET ' + URL_BASE)
        self.br.open(URL_BASE)

        print('Logging in with credentials...')
        self.br.select_form(nr=0)
        self.br.form['vb_login_username'] = credentials['username']
        self.br.form['vb_login_password'] = credentials['password']
        self.br.submit()

        if 'invalid' in str(self.br.response().read()):
            print('Invalid username or password. Please update credentials.json')
        else:
            print('Login successful!')

    def get(self, url):
        print('GET ' + url)
        data = self.br.open(url)
        return BeautifulSoup(data, 'html.parser', from_encoding='iso-8859-1')

br = Browser()
br.login()

tiers = {}

for tier_main in br.get(URL_TIERS)('div', class_='tier_main'):
    name = tier_main.find('div', class_='tier_details')('div')[0].text
    leveltiers = [li.text.split()[2].replace(',', '') for li in tier_main.find('ul', class_='tier_req_list')('li')]
    tiers[name] = leveltiers

open(OUTPUT_FILENAME, 'w').write(json.dumps(tiers, indent=4, sort_keys=True))
print('Stats written to ' + OUTPUT_FILENAME)
