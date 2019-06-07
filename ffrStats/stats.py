"""
Collects all FFR level rank data (excluding token level ranks) given a
user's credentials and stores the results in 'output_file'. The reuslts
are ordered so that the easiest and lowest ranking levels that still
need to be AAA'd appear first.

Assumes there is an existing file in this directory named 'credentials'
that contains a username and password in JSON format:
{'username':'YOUR_USERNAME','password':'YOUR_PASSWORD'}
"""

from bs4 import BeautifulSoup
from collections import OrderedDict
from tabulate import tabulate
import json
import mechanize
import re
import sys
import time

difficulties = [
    ('Brutal', 100),
    ('Guru', 85),
    ('Master', 70),
    ('Very Challenging', 60),
    ('Challenging', 50),
    ('Very Difficult', 42),
    ('Difficult', 34),
    ('Tricky', 26),
    ('Standard', 18),
    ('Easy', 11),
    ('Very Easy', 7),
    ('Beginner', 4),
    ('Easiest', 1),
    ('Zero', 0)
]

def get_difficulty_index(d):
    for i in range(len(difficulties)):
        if d >= difficulties[i][1]:
            return i

class Totals:
    """Class to keep track of scores"""
    def __init__(self):
        self.total = 0
        self.aaa = 0
        self.fc = 0

    def add_levelrank(self, levelrank):
        self.total += 1
        if levelrank.fc:
            self.fc += 1
        if levelrank.isAAA():
            self.aaa += 1

class Tier:
    """Class to keep track of per-tier_total data"""
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.perfect = 0

class Levelrank:
    """A row of levelrank data"""
    def __init__(self, row, cols):
        self.rank = int(row[cols['rank']].string.replace(',', ''))
        self.d = int(row[cols['d']].string)
        self.level = row[cols['level']].string
        self.score = int(row[cols['score']].string.replace(',', '').replace('*', ''))
        self.fc = '*' in row[cols['score']].string
        self.p = int(row[cols['p']].string.replace(',', ''))
        self.g = int(row[cols['g']].string.replace(',', ''))
        self.a = int(row[cols['a']].string.replace(',', ''))
        self.m = int(row[cols['m']].string.replace(',', ''))
        self.b = int(row[cols['b']].string.replace(',', ''))
        self.c = int(row[cols['c']].string.replace(',', ''))
        self.played = int(row[cols['played']].string.replace(',', ''))

    def isAAA(self):
        return self.fc and self.p == self.c and self.b == 0

def printAAAsAndFCs(totals, f):
    # TODO: options for colors
    if totals.aaa != totals.total and (totals.aaa != 0 or totals.fc == totals.total):
        f.write(' %d/%d [color=#D95819]AAAs[/color]' % (totals.aaa, totals.total))
    if totals.fc != totals.total:
        f.write(' %d/%d [color=#009900]FCs[/color]' % (totals.fc, totals.total))
    f.write('\n')

def extract_levelranks(raw_data):
    # get table columns
    cols = {}
    for i, th in enumerate(raw_data('tr')[0]('th')):
        if th.span:
            # remove arrow from table headers
            th.span.extract()
        cols[th.string.lower()] = i

    return [Levelrank(tr('td'), cols) for tr in raw_data('tr')[1:]]

def format_data(levelranks, output_filename, title, write_ld):
    # per-difficulty distribution
    dd = [Totals() for _ in range(len(difficulties))]
    # per-level distribution
    ld = {}

    for levelrank in levelranks:
        dd[get_difficulty_index(levelrank.d)].add_levelrank(levelrank)
        if levelrank.d not in ld:
            ld[levelrank.d] = Totals()
        ld[levelrank.d].add_levelrank(levelrank)

    # TODO: probably move this writing part out of this function, or refactor this somehow
    with open(output_filename, 'a') as f:
        f.write('[b][u]' + title + '[/u][/b]\n\n')

        for i in range(len(difficulties)-1, -1, -1):
            if dd[i].aaa == dd[i].total:
                continue
            f.write('[color=#FF9900]%s[/color]:' % difficulties[i][0])
            printAAAsAndFCs(dd[i], f)
        f.write('\n')

        if (write_ld):
            for d, t in sorted(ld.items(), key=lambda x:x[0]):
                if t.aaa == t.total:
                    continue
                f.write('[color=#FF9900]%d[/color]:' % d)
                printAAAsAndFCs(t, f)
            f.write('\n')

credentials = json.loads(open('credentials', 'r').read())

# get the username that the stats will be retrieved for
stats_username = credentials['username']
if len(sys.argv) == 2:
    stats_username = sys.argv[1]
elif len(sys.argv) != 1:
    print('Invalid argument format. Please call this script with the following format:')
    print('\tpython3 stats.py <OPTIONAL:stats_username>')
    sys.exit()

# TODO: provide an option for which random thought is used, and throw an error if the thought is invalid?
random_thought_id = '234639'

# URLs
url_base = 'http://www.flashflashrevolution.com'
url_levelrank = url_base + '/levelrank.php?sub=' + stats_username
url_tokenlevelrank = url_base + '/levelrank_special.php?sub=' + stats_username
url_tiers = url_base + '/FFRStats/level_tiers.php'
url_post = url_base + '/profile/edit/thoughts/' + random_thought_id

class Browser:
    def __init__(self):
        """Initialize mechanize browser"""
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0')]

    def login(self):
        print('[+] GET ' + url_base)
        self.br.open(url_base)

        print('[+] Logging in with credentials...')
        self.br.select_form(nr=0)
        self.br.form['vb_login_username'] = credentials['username']
        self.br.form['vb_login_password'] = credentials['password']
        self.br.submit()

        # TODO: check if credentials are correct here rather than throwing an error later on
        # also "Logged in successful / unsuccessful print statements"

    def get(self, url):
        print('[+] GET ' + url)
        data = self.br.open(url)
        return BeautifulSoup(data, 'html.parser', from_encoding='iso-8859-1')

    def post_stats(self, body):
        print('[+] GET ' + url_post)
        self.br.open(url_post)
        self.br.select_form(nr=0)
        self.br.form['blog_title'] = 'Stats'
        self.br.form['blog_post'] = body
        self.br.submit()
        print('[+] Stats posted to ' + random_thought_id)

br = Browser()
br.login()

output_filename = time.strftime('stats-%Y-%m-%d-%H-%M-%S.txt')
print('[+] Writing stats to ' + output_filename)

levelranks = extract_levelranks(br.get(url_levelrank))
format_data(levelranks, output_filename, 'Public Level Stats', True)

tokenlevelranks = extract_levelranks(br.get(url_tokenlevelrank))
format_data(tokenlevelranks, output_filename, 'Token Level Stats', False)

br.post_stats(open(output_filename, 'r').read())

##### TIERS #####

tier_mains = br.get(url_tiers).find_all('div', class_='tier_main')
tiers = {}

for tier_main in tier_mains:
    tier_earned = int(tier_main.find_all('span', class_='tier_earned')[0].string)
    tier_total = int(tier_main.find_all('span', class_='tier_total')[0].string)

    if tier_total not in tiers:
        tiers[tier_total] = Tier()

    tiers[tier_total].count += 1
    tiers[tier_total].sum += tier_earned

    if tier_earned == tier_total:
        tiers[tier_total].perfect += 1

print(tabulate(sorted([[t, tiers[t].perfect, tiers[t].count, tiers[t].sum, tiers[t].count * t] for t in tiers], key=lambda x:x[0]),
    headers=['D', 'Perfect', 'Count', 'Earned', 'Total']))
