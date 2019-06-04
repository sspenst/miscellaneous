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

def printAAAsAndFCs(totals, f):
    if totals.aaa != totals.total and totals.aaa != 0:
        f.write(' %d/%d [color=#D95819]AAAs[/color]' % (totals.aaa, totals.total))
    if totals.fc != totals.total:
        f.write(' %d/%d [color=#009900]FCs[/color]' % (totals.fc, totals.total))
    f.write('\n')

def format_data(raw_data, output_filename):
    """
    Given raw level rank data, returns a list of OrderedDict objects containing the
    difficulty, rank, and name of all levels that have not been AAA'd.
    """

    print('[+] Formatting level ranks...')

    # get table columns
    cols = {}
    for i, th in enumerate(raw_data('tr')[0]('th')):
        if th.span:
            # remove arrow from table headers
            th.span.extract()
        cols[th.string] = i

    levels = []

    # per-difficulty distribution
    dd = [Totals() for _ in range(len(difficulties))]
    # per-level distribution
    ld = {}

    for tr in raw_data('tr')[1:]:
        row = tr('td')
        rank = int(row[cols['Rank']].string.replace(',', ''))
        difficulty = int(row[cols['D']].string)

        index = get_difficulty_index(difficulty)
        dd[index].total += 1

        if difficulty not in ld:
            ld[difficulty] = Totals()

        ld[difficulty].total += 1

        # TODO: rank 1 != AAA !!!!! almost always but pls make it accurate
        if rank != 1:
            # keep track of levels that are already AAA'd
            name = row[cols['Level']].string

            levels.append(OrderedDict([('D', difficulty),
                ('Rank', rank),
                ('Name', name)]))
        else:
            dd[index].aaa += 1
            ld[difficulty].aaa += 1

        if '*' in row[cols['Score']].string:
            dd[index].fc += 1
            ld[difficulty].fc += 1

    # print(tabulate([[difficulties[i], dd[i].aaa, dd[i].fc, dd[i].total] for i in range(len(difficulties)-1, -1, -1) if dd[i].aaa != dd[i].total],
    #     headers=['Difficulty', 'AAAs', 'FCs', 'Total']))

    with open(output_filename, 'w') as f:
        for i in range(len(difficulties)-1, -1, -1):
            if dd[i].aaa == dd[i].total:
                continue
            f.write('%s:' % difficulties[i][0])
            printAAAsAndFCs(dd[i], f)

        f.write('\n')

        for d, t in sorted(ld.items(), key=lambda x:x[0]):
            if t.aaa == t.total:
                continue
            f.write('[color=#FF9900]%d[/color]:' % d)
            printAAAsAndFCs(t, f)

    # return levels

credentials = json.loads(open('credentials', 'r').read())

# get the username that the stats will be retrieved for
stats_username = credentials['username']
if len(sys.argv) == 2:
    stats_username = sys.argv[1]
elif len(sys.argv) != 1:
    print('Invalid argument format. Please call this script with the following format:')
    print('\tpython3 stats.py <OPTIONAL:stats_username>')
    sys.exit()

# URLs
url_base = 'http://www.flashflashrevolution.com'
url_levelrank = url_base + '/levelrank.php?sub=' + stats_username
url_tiers = url_base + '/FFRStats/level_tiers.php'
url_post = url_base + '/profile/edit/thoughts/234639'
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

output_filename = time.strftime("stats-%Y-%m-%d-%H-%M-%S.txt")

format_data(soup.table, output_filename)

# levels = format_data(soup.table, output_filename)

# sort the level data primarily by difficulty, and secondly by lowest rank
# sorted_levels = sorted(levels, key=lambda level:level['Rank'])
# sorted_levels = sorted(sorted_levels, key=lambda level:level['D'])

# with open(output_filename, 'w') as f:
#     f.write(tabulate(sorted_levels, headers='keys', tablefmt='simple'))

print('[+] Stats written to ' + output_filename)

post(br, open(output_filename, 'r').read())

print('[+] Stats posted to ' + output_filename)

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
