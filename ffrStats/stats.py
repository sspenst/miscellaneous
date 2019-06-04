"""
Collects all FFR level rank data (excluding token level ranks) given a
user's credentials and stores the results in 'output_file'. The reuslts
are ordered so that the easiest and lowest ranking levels that still
need to be AAA'd appear first.

Assumes there is an existing file in this directory named 'credentials'
that contains a username and password in JSON format:
{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}
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
    ('Easiest', 1)
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

def printAAAsAndFCs(totals, f):
    if totals.aaa != totals.total and totals.aaa != 0:
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

def format_data(levelranks, output_filename):
    # per-difficulty distribution
    dd = [Totals() for _ in range(len(difficulties))]
    # per-level distribution
    ld = {}

    for levelrank in levelranks:
        dd_totals = dd[get_difficulty_index(levelrank.d)]
        if levelrank.d not in ld:
            ld[levelrank.d] = Totals()
        ld_totals = ld[levelrank.d]

        dd_totals.total += 1
        ld_totals.total += 1

        if levelrank.fc:
            dd_totals.fc += 1
            ld_totals.fc += 1
            if levelrank.p == levelrank.c and levelrank.b == 0:
                dd_totals.aaa += 1
                ld_totals.aaa += 1

    with open(output_filename, 'w') as f:
        f.write('[b]Public Level Stats[/b]\n\n')

        for i in range(len(difficulties)-1, -1, -1):
            if dd[i].aaa == dd[i].total:
                continue
            f.write('[color=#FF9900]%s[/color]:' % difficulties[i][0])
            printAAAsAndFCs(dd[i], f)

        f.write('\n')

        for d, t in sorted(ld.items(), key=lambda x:x[0]):
            if t.aaa == t.total:
                continue
            f.write('[color=#FF9900]%d[/color]:' % d)
            printAAAsAndFCs(t, f)

credentials = json.loads(open('credentials', 'r').read())

# get the username that the stats will be retrieved for
stats_username = credentials['username']
if len(sys.argv) == 2:
    stats_username = sys.argv[1]
elif len(sys.argv) != 1:
    print('Invalid argument format. Please call this script with the following format:')
    print('\tpython3 stats.py <OPTIONAL:stats_username>')
    sys.exit()

random_thought_id = '234639'

# URLs
url_base = 'http://www.flashflashrevolution.com'
url_levelrank = url_base + '/levelrank.php?sub=' + stats_username
url_tiers = url_base + '/FFRStats/level_tiers.php'
url_post = url_base + '/profile/edit/thoughts/' + random_thought_id
# TODO: provide an option for which random thought is used, and throw an error if the thought is invalid

def get_browser():
    """initialize mechanize browser"""
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0')]
    return br

def login(br):
    print('[+] GET ' + url_base)
    br.open(url_base)

    print('[+] Logging in with credentials...')
    br.select_form(nr=0)
    br.form['vb_login_username'] = credentials['username']
    br.form['vb_login_password'] = credentials['password']
    br.submit()

    # TODO: check if credentials are correct here rather than throwing an error later on
    # also "Logged in successful / unsuccessful print statements"

def post(br, body):
    print('[+] GET ' + url_post)
    br.open(url_post)
    br.select_form(nr=0)
    br.form['blog_title'] = 'Stats'
    br.form['blog_post'] = body
    br.submit()

br = get_browser()
login(br)

print('[+] GET ' + url_levelrank)
data = br.open(url_levelrank)
soup = BeautifulSoup(data, 'html.parser', from_encoding='iso-8859-1')

if soup.table == None:
    print("[+] ERROR: Invalid login credentials")
    exit()

levelranks = extract_levelranks(soup.table)

output_filename = time.strftime("stats-%Y-%m-%d-%H-%M-%S.txt")

format_data(levelranks, output_filename)

# levels = format_data(soup.table, output_filename)

# sort the level data primarily by difficulty, and secondly by lowest rank
# sorted_levels = sorted(levels, key=lambda level:level['Rank'])
# sorted_levels = sorted(sorted_levels, key=lambda level:level['D'])

# with open(output_filename, 'w') as f:
#     f.write(tabulate(sorted_levels, headers='keys', tablefmt='simple'))

print('[+] Stats written to ' + output_filename)

post(br, open(output_filename, 'r').read())

print('[+] Stats posted to ' + random_thought_id)

##### TIERS #####

print('[+] GET ' + url_tiers)
data = br.open(url_tiers)
soup = BeautifulSoup(data, 'html.parser', from_encoding='iso-8859-1')

tier_mains = soup.find_all('div', class_="tier_main")
tiers = {}

for tier_main in tier_mains:
    tier_earned = int(tier_main.find_all('span', class_="tier_earned")[0].string)
    tier_total = int(tier_main.find_all('span', class_="tier_total")[0].string)

    if tier_total not in tiers:
        tiers[tier_total] = Tier()

    tiers[tier_total].count += 1
    tiers[tier_total].sum += tier_earned

    if tier_earned == tier_total:
        tiers[tier_total].perfect += 1

print(tabulate(sorted([[t, tiers[t].perfect, tiers[t].count, tiers[t].sum, tiers[t].count * t] for t in tiers], key=lambda x:x[0]),
    headers=['D', 'Perfect', 'Count', 'Earned', 'Total']))
