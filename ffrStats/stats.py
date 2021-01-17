"""
Collects all FFR level rank and tier point data for a user.
The data is formatted into a collection of stats which are posted 
to the given random thought id.

Assumes there is an existing file in this directory named
'credentials.json' that contains a username and password:
{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}
"""

from bs4 import BeautifulSoup
from collections import OrderedDict
from tabulate import tabulate
import json
import math
import mechanize
import re
import sys
import time

# config
HIDE_ZERO_DIFFICULTY = True
MAX_DIFFICULTY_LEVEL_TOTAL = 102
RANDOM_THOUGHT_ID = '234639'
SHOW_PASSED = False

# URLs
URL_BASE = 'http://www.flashflashrevolution.com'
URL_POST = URL_BASE + '/profile/edit/thoughts/' + RANDOM_THOUGHT_ID

# colors
HEX_D = "FF9900"
HEX_AAA = "D95819"
HEX_SDG = "3774FF"
HEX_FC = "009900"
HEX_PASS = "999999"
HEX_TP = "CF2222"

# raw scoring values
PERFECT_SCORE = 50
GOOD_SCORE = 25
AVERAGE_SCORE = 5
MISS_SCORE = -10
BOO_SCORE = -5

# data
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
LEVEL_ARROWS = json.loads(open('levelarrows.json', 'r').read())
LEVEL_TIERS = json.loads(open('leveltiers.json', 'r').read())

class Browser:
    def __init__(self):
        """Initialize mechanize browser"""
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0')]

    def login(self, credentials):
        print('[+] GET ' + URL_BASE)
        self.br.open(URL_BASE)

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
        print('[+] GET ' + URL_POST)
        self.br.open(URL_POST)
        self.br.select_form(nr=0)
        self.br.form['blog_title'] = time.strftime('Stats - %b %d, %Y')
        self.br.form['blog_post'] = body
        self.br.submit()
        print('[+] Stats posted to random thought ' + RANDOM_THOUGHT_ID)

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
        self.arrows = LEVEL_ARROWS[self.level]
        self.tp = 0
        self.tpmax = 0

        if self.level in LEVEL_TIERS:
            tiers = LEVEL_TIERS[self.level]
            self.tpmax = len(tiers)
            self.tp = self.tpmax

            for tier in tiers:
                if tier != 'Passed' and self.score >= int(tier):
                    break
                elif tier == 'Passed' and self.passed():
                    break
                self.tp -= 1

    def isAAA(self):
        return self.fc and self.p == self.c and self.b == 0

    def isSDG(self):
        return self.passed() and self.score > PERFECT_SCORE * (self.arrows - 10) + GOOD_SCORE * 10

    def passed(self):
        return self.p + self.g + self.a + self.m == self.arrows

class Totals:
    """Used for keeping track of totals"""
    def __init__(self):
        self.total = 0
        self.aaa = 0
        self.sdg = 0
        self.fc = 0
        self.passed = 0
        self.tpearned = 0
        self.tptotal = 0

    def add_levelrank(self, levelrank):
        self.total += 1
        self.tpearned += levelrank.tp
        self.tptotal += levelrank.tpmax
        if levelrank.isAAA():
            self.aaa += 1
        if levelrank.isSDG():
            self.sdg += 1
        if levelrank.fc:
            self.fc += 1
        if levelrank.passed():
            self.passed += 1

    def to_string(self):
        s = ''
        # print AAA count; only print 0 AAAs if all SDGs are complete
        if self.aaa != 0 or self.sdg == self.total:
            s += ' %d/%d [color=#%s]AAAs[/color]' % (self.aaa, self.total, HEX_AAA)
        # print SDG count if there are SDGs remaining
        if self.sdg != self.total:
            s += ' %d/%d [color=#%s]SDGs[/color]' % (self.sdg, self.total, HEX_SDG)
        # print FC count if there are FCs remaining
        if self.fc != self.total:
            s += ' %d/%d [color=#%s]FCs[/color]' % (self.fc, self.total, HEX_FC)
        # print passed count if there are unpassed levels remaining
        if SHOW_PASSED and self.passed != self.total:
            s += ' %d/%d [color=#%s]Passed[/color]' % (self.passed, self.total, HEX_PASS)
        # print tier points total if there are tier points remaining
        if self.tpearned != self.tptotal:
            s += ' %d/%d [color=#%s]TPs[/color]' % (self.tpearned, self.tptotal, HEX_TP)
        return s + '\n'

def extract_levelranks(raw_data):
    # get table columns
    cols = {}
    for i, th in enumerate(raw_data('tr')[0]('th')):
        if th.span:
            # remove arrow from table headers
            th.span.extract()
        cols[th.string.lower()] = i

    return [Levelrank(tr('td'), cols) for tr in raw_data('tr')[1:]]

def format_levelranks(levelranks, output_filename, title, write_level_totals):
    # per-difficulty totals
    difficulty_totals = [Totals() for _ in range(len(DIFFICULTIES))]
    # per-level totals
    level_totals = {}
    # grand totals
    totals = Totals()

    # accumulate totals
    for levelrank in levelranks:
        difficulty_totals[get_difficulty_index(levelrank.d)].add_levelrank(levelrank)
        if levelrank.d not in level_totals:
            level_totals[levelrank.d] = Totals()
        level_totals[levelrank.d].add_levelrank(levelrank)
        totals.add_levelrank(levelrank)

    with open(output_filename, 'a') as f:
        f.write('[b][u]' + title + '[/u][/b]\n\n')

        # write per-difficulty totals
        for i in range(len(DIFFICULTIES)-1, -1, -1):
            if HIDE_ZERO_DIFFICULTY and i == len(DIFFICULTIES) - 1:
                continue
            if difficulty_totals[i].aaa == difficulty_totals[i].total:
                continue
            f.write('[color=#%s]%s[/color]:%s' % (HEX_D, DIFFICULTIES[i][0], difficulty_totals[i].to_string()))
        f.write('\n')

        # write per-level totals
        if (write_level_totals):
            for d, t in sorted(level_totals.items(), key=lambda x:x[0]):
                if HIDE_ZERO_DIFFICULTY and d == 0:
                    continue
                if d > MAX_DIFFICULTY_LEVEL_TOTAL:
                    break
                if t.aaa == t.total:
                    continue
                f.write('[color=#%s]%d[/color]:%s' % (HEX_D, d, t.to_string()))
            f.write('\n')

        # write grand totals
        f.write('[color=#%s]AAAs[/color]: %d/%d %.1f%%\n' % (HEX_AAA, totals.aaa, totals.total, 100 * totals.aaa / totals.total))
        f.write('[color=#%s]SDGs[/color]: %d/%d %.1f%%\n' % (HEX_SDG, totals.sdg, totals.total, 100 * totals.sdg / totals.total))
        f.write('[color=#%s]FCs[/color]: %d/%d %.1f%%\n' % (HEX_FC, totals.fc, totals.total, 100 * totals.fc / totals.total))
        if SHOW_PASSED:
            f.write('[color=#%s]Passed[/color]: %d/%d %.1f%%\n' % (HEX_PASS, totals.passed, totals.total, 100 * totals.passed / totals.total))
        f.write('[color=#%s]TPs[/color]: %d/%d %.1f%%\n' % (HEX_TP, totals.tpearned, totals.tptotal, 100 * totals.tpearned / totals.tptotal))
        f.write('\n')

def format_tierpoints(all_levelranks, output_filename):
    tiertotals = set()

    for levelrank in all_levelranks:
        if levelrank.tpmax == 0:
            continue
        tiertotals.add(levelrank.tpmax)

    with open(output_filename, 'a') as f:
        f.write('[b][u]Tier Point Stats[/u][/b]\n')

        for tiertotal in sorted(tiertotals):
            lts = list(filter(lambda x: x.tpmax == tiertotal, all_levelranks))
            earned = sum(lt.tp for lt in lts)
            total = sum(lt.tpmax for lt in lts)
            if earned != total:
                f.write('\n[color=#%s]/%d[/color]: %d/%d [color=#%s]TPs[/color]' % (HEX_D, tiertotal, earned, total, HEX_TP))

        total_aaas = len(list(filter(lambda x: x.isAAA(), all_levelranks)))
        extra_tierpoints = max(int(100 * total_aaas / len(all_levelranks)) - 49, 0)
        max_extra_tierpoints = 50

        f.write('\n[color=#%s]+[/color]: %d/%d [color=#%s]TPs[/color]' % (HEX_D, extra_tierpoints, max_extra_tierpoints, HEX_TP))

        earned_tierpoints = sum(l.tp for l in all_levelranks) + extra_tierpoints
        total_tierpoints = sum(l.tpmax for l in all_levelranks) + max_extra_tierpoints
        
        f.write('\n\n[color=#%s]TPs[/color]: %d/%d %.1f%%' % (HEX_TP, earned_tierpoints, total_tierpoints, 100 * earned_tierpoints / total_tierpoints))


def get_difficulty_index(d):
    for i in range(len(DIFFICULTIES)):
        if d >= DIFFICULTIES[i][1]:
            return i

def main():
    credentials = json.loads(open('credentials.json', 'r').read())

    # get the username that the stats will be retrieved for
    stats_username = credentials['username']
    if len(sys.argv) == 2:
        stats_username = sys.argv[1]
    elif len(sys.argv) != 1:
        print('Invalid argument format. Please call this script with the following format:')
        print('\tpython3 stats.py <OPTIONAL:stats_username>')
        sys.exit()

    br = Browser()
    br.login(credentials)

    output_filename = time.strftime('stats-%Y-%m-%d-%H-%M-%S.txt')
    print('[+] Writing stats to ' + output_filename)

    url_levelrank = URL_BASE + '/levelrank.php?sub=' + stats_username
    levelranks = extract_levelranks(br.get(url_levelrank))
    format_levelranks(levelranks, output_filename, 'Public Level Stats', True)

    url_tokenlevelrank = URL_BASE + '/levelrank_special.php?sub=' + stats_username
    token_levelranks = extract_levelranks(br.get(url_tokenlevelrank))
    format_levelranks(token_levelranks, output_filename, 'Token Level Stats', False)

    all_levelranks = levelranks + token_levelranks
    format_tierpoints(all_levelranks, output_filename)

    br.post_stats(open(output_filename, 'r').read())

if __name__ == "__main__":
    main()
