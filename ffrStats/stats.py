"""
Collects all FFR level rank data (excluding token level ranks) given a
user's credentials and stores the results in 'output_file'. The reuslts
are ordered so that the easiest and lowest ranking levels that still
need to be AAA'd appear first.

Assumes there is an existing file in this directory named
'credentials.json' that contains a username and password:
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

# raw scoring values
PERFECT_SCORE = 50
GOOD_SCORE = 25
AVERAGE_SCORE = 5
MISS_SCORE = -10
BOO_SCORE = -5

DIFFICULTIES = [
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
    for i in range(len(DIFFICULTIES)):
        if d >= DIFFICULTIES[i][1]:
            return i

class Totals:
    """Used for keeping track of totals"""
    def __init__(self):
        self.total = 0
        self.aaa = 0
        self.sdg = 0
        self.fc = 0
        self.unplayed = 0

    def add_levelrank(self, levelrank):
        self.total += 1
        if levelrank.isAAA():
            self.aaa += 1
        if levelrank.isSDG():
            self.sdg += 1
        if levelrank.fc:
            self.fc += 1
        if levelrank.score == 0:
            self.unplayed += 1

    def to_string(self):
        # TODO: options for colors
        s = ''
        # print AAA count; only print 0 AAAs if all SDGs and FCs are complete
        if self.aaa != 0 or (self.sdg == self.total and self.fc == self.total):
            s += ' %d/%d [color=#D95819]AAAs[/color]' % (self.aaa, self.total)
        # print SDG count; only print 0 SDGs if all FCs are complete; only print 100% SDGs if not all FCs are complete
        if (self.sdg != 0 or self.fc == self.total) and (self.sdg != self.total or self.fc != self.total):
            s += ' %d/%d [color=#3774FF]SDGs[/color]' % (self.sdg, self.total)
        # print FC count if there are no FCs remaining
        if self.fc != self.total:
            s += ' %d/%d [color=#009900]FCs[/color]' % (self.fc, self.total)
        # print unplayed count if there are remaining unplayed levels
        if self.unplayed != 0:
            s += ' %d/%d [color=#999999]Unplayed[/color]' % (self.unplayed, self.total)
        return s + '\n'

class Levelrank:
    """A row of levelrank data"""
    def __init__(self, row, cols):
        self.rank = int(row[cols['rank']].string.replace(',', ''))
        self.d = int(row[cols['d']].string)
        self.level = row[cols['level']].string.replace('\\', '') # backslash replace is specifically for 'R/\IN'
        self.score = int(row[cols['score']].string.replace(',', '').replace('*', ''))
        self.fc = '*' in row[cols['score']].string
        self.p = int(row[cols['p']].string.replace(',', ''))
        self.g = int(row[cols['g']].string.replace(',', ''))
        self.a = int(row[cols['a']].string.replace(',', ''))
        self.m = int(row[cols['m']].string.replace(',', ''))
        self.b = int(row[cols['b']].string.replace(',', ''))
        self.c = int(row[cols['c']].string.replace(',', ''))
        self.played = int(row[cols['played']].string.replace(',', ''))
        self.notes = levelstats[self.level]

    def isAAA(self):
        return self.fc and self.p == self.c and self.b == 0

    def isSDG(self):
        return self.passed() and self.score > PERFECT_SCORE * (self.notes - 10) + GOOD_SCORE * 10

    def passed(self):
        return self.p + self.g + self.a + self.m == self.notes

class Tier:
    """Class to keep track of per-tier_total data"""
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.perfect = 0

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
    dd = [Totals() for _ in range(len(DIFFICULTIES))]
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

        for i in range(len(DIFFICULTIES)-1, -1, -1):
            if dd[i].aaa == dd[i].total:
                continue
            f.write('[color=#FF9900]%s[/color]:%s' % (DIFFICULTIES[i][0], dd[i].to_string()))
        f.write('\n')

        if (write_ld):
            for d, t in sorted(ld.items(), key=lambda x:x[0]):
                if t.aaa == t.total:
                    continue
                f.write('[color=#FF9900]%d[/color]:%s' % (d, t.to_string()))
            f.write('\n')

credentials = json.loads(open('credentials.json', 'r').read())

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

        if 'invalid' in str(self.br.response().read()):
            print('[+] Invalid username or password. Please update credentials.json')
        else:
            print('[+] Login successful!')

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

levelstats = json.loads(open('levelstats.json', 'r').read())

output_filename = time.strftime('stats-%Y-%m-%d-%H-%M-%S.txt')
print('[+] Writing stats to ' + output_filename)

levelranks = extract_levelranks(br.get(url_levelrank))
format_data(levelranks, output_filename, 'Public Level Stats', True)

tokenlevelranks = extract_levelranks(br.get(url_tokenlevelrank))
format_data(tokenlevelranks, output_filename, 'Token Level Stats', False)

br.post_stats(open(output_filename, 'r').read())

##### TIERS #####

tier_mains = br.get(url_tiers)('div', class_='tier_main')
tiers = {}

for tier_main in tier_mains:
    tier_earned = int(tier_main('span', class_='tier_earned')[0].string)
    tier_total = int(tier_main('span', class_='tier_total')[0].string)

    if tier_total not in tiers:
        tiers[tier_total] = Tier()

    tiers[tier_total].count += 1
    tiers[tier_total].sum += tier_earned

    if tier_earned == tier_total:
        tiers[tier_total].perfect += 1

print(tabulate(sorted([[t, tiers[t].perfect, tiers[t].count, tiers[t].sum, tiers[t].count * t] for t in tiers], key=lambda x:x[0]),
    headers=['D', 'Perfect', 'Count', 'Earned', 'Total']))
