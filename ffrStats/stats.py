"""
Collects all FFR level rank data (excluding token level ranks) given a
user's credentials and stores the results in 'output_file'. The reuslts
are ordered so that the easiest and lowest ranking levels that still
need to be AAA'd appear first.

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

# colors
HEX_D = "FF9900"
HEX_EQ = "AA66DD"
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
        self.passed = 0
        self.tpearned = 0
        self.tptotal = 0
        self.eqt = 0

    def add_levelrank(self, levelrank):
        self.total += 1
        if levelrank.isAAA():
            self.aaa += 1
        if levelrank.isSDG():
            self.sdg += 1
        if levelrank.fc:
            self.fc += 1
        if levelrank.passed():
            self.passed += 1
            #self.eqt += levelrank.AAAeq()

    def to_string(self, show_eq):
        s = ''
        # print average AAA equivalency
        if show_eq:
            s += ' %.2f [color=#%s]EQ[/color]' % (self.eqt / self.passed, HEX_EQ)
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
        if self.passed != self.total:
            s += ' %d/%d [color=#%s]Passed[/color]' % (self.passed, self.total, HEX_PASS)
        # print tier points total if there are tier points remaining
        if self.tpearned != self.tptotal:
            s += ' %d/%d [color=#%s]TPs[/color]' % (self.tpearned, self.tptotal, HEX_TP)
        return s + '\n'

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
        self.arrows = levelarrows[self.level]

    def isAAA(self):
        return self.fc and self.p == self.c and self.b == 0

    def isSDG(self):
        return self.passed() and self.score > PERFECT_SCORE * (self.arrows - 10) + GOOD_SCORE * 10

    def passed(self):
        return self.p + self.g + self.a + self.m == self.arrows

    def NGC(self):
        return self.g + 1.8 * self.a + 2.4 * self.m + 0.2 * self.b

    def AAAeq(self):
        a0 = 17678803623.9633
        a1 = 733763392.922176
        a2 = 28163834.4879901
        a3 = -434698.513947563
        a4 = 3060.24243867853
        delta = a0 + a1 * self.d + a2 * self.d * self.d + a3 * math.pow(self.d, 3) + a4 * math.pow(self.d, 4)
        lamb = 18206628.7286425
        alpha = 9.97503967400340
        beta = 0.0193296437339205
        return (self.d + alpha) * math.pow((delta - self.NGC() * lamb) / delta, 1 / beta) - alpha

class Leveltierpoints:
    """Tier points for a level"""
    def __init__(self, earned, total, d):
        self.earned = earned
        self.total = total
        self.d = d

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
    totals = Totals()

    for levelrank in levelranks:
        dd[get_difficulty_index(levelrank.d)].add_levelrank(levelrank)
        if levelrank.d not in ld:
            ld[levelrank.d] = Totals()
        ld[levelrank.d].add_levelrank(levelrank)
        totals.add_levelrank(levelrank)

    for level, tiers in leveltiers.items():
        levelranklist = list(filter(lambda x: x.level == level, levelranks))

        if len(levelranklist) == 0:
            continue

        levelrank = levelranklist[0]
        total = len(tiers)
        points = total

        for tier in tiers:
            if tier != 'Passed' and levelrank.score >= int(tier):
                break
            elif tier == 'Passed' and levelrank.passed():
                break
            points -= 1

        dd[get_difficulty_index(levelrank.d)].tpearned += points
        dd[get_difficulty_index(levelrank.d)].tptotal += total
        ld[levelrank.d].tpearned += points
        ld[levelrank.d].tptotal += total
        totals.tpearned += points
        totals.tptotal += total

    # TODO: probably move this writing part out of this function, or refactor this somehow
    with open(output_filename, 'a') as f:
        f.write('[b][u]' + title + '[/u][/b]\n\n')

        for i in range(len(DIFFICULTIES)-1, -1, -1):
            if dd[i].aaa == dd[i].total:
                continue
            f.write('[color=#%s]%s[/color]:%s' % (HEX_D, DIFFICULTIES[i][0], dd[i].to_string(False)))
        f.write('\n')

        if (write_ld):
            # consecutive = 0
            # start_d = 0

            for d, t in sorted(ld.items(), key=lambda x:x[0]):
                if t.aaa == t.total:
                #     if start_d == 0:
                #         start_d = d
                #     consecutive += t.aaa
                    continue
                # elif consecutive > 0:
                #     f.write('[color=#%s]%d[/color]-[color=#%s]%d[/color]: %d/%d [color=#%s]AAAs[/color]\n' % (HEX_D, start_d, HEX_D, d-1, consecutive, consecutive, HEX_AAA))
                #     consecutive = 0
                #     start_d = 0
                f.write('[color=#%s]%d[/color]:%s' % (HEX_D, d, t.to_string(False)))
            f.write('\n')

        f.write('[color=#%s]AAAs[/color]: %d/%d %.1f%%\n' % (HEX_AAA, totals.aaa, totals.total, 100 * totals.aaa / totals.total))
        f.write('[color=#%s]SDGs[/color]: %d/%d %.1f%%\n' % (HEX_SDG, totals.sdg, totals.total, 100 * totals.sdg / totals.total))
        f.write('[color=#%s]FCs[/color]: %d/%d %.1f%%\n' % (HEX_FC, totals.fc, totals.total, 100 * totals.fc / totals.total))
        f.write('[color=#%s]Passed[/color]: %d/%d %.1f%%\n' % (HEX_PASS, totals.passed, totals.total, 100 * totals.passed / totals.total))
        f.write('[color=#%s]TPs[/color]: %d/%d %.1f%%\n' % (HEX_TP, totals.tpearned, totals.tptotal, 100 * totals.tpearned / totals.tptotal))
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

levelarrows = json.loads(open('levelarrows.json', 'r').read())
leveltiers = json.loads(open('leveltiers.json', 'r').read())

output_filename = time.strftime('stats-%Y-%m-%d-%H-%M-%S.txt')
print('[+] Writing stats to ' + output_filename)

levelranks = extract_levelranks(br.get(url_levelrank))
format_data(levelranks, output_filename, 'Public Level Stats', True)

tokenlevelranks = extract_levelranks(br.get(url_tokenlevelrank))
format_data(tokenlevelranks, output_filename, 'Token Level Stats', False)

##### TIERS #####

alllevelranks = levelranks + tokenlevelranks

leveltierpoints = []
tiertotals = set()

for level, tiers in leveltiers.items():
    levelrank = list(filter(lambda x: x.level == level, alllevelranks))[0]
    total = len(tiers)
    earned = total

    for tier in tiers:
        if tier != 'Passed' and levelrank.score >= int(tier):
            break
        elif tier == 'Passed' and levelrank.passed():
            break
        earned -= 1

    # if total == 7:
    #     print('%d/%d %d %s' % (earned, total, levelrank.d, levelrank.level))

    leveltierpoints.append(Leveltierpoints(earned, total, levelrank.d))
    tiertotals.add(total)

with open(output_filename, 'a') as f:
    f.write('[b][u]Tier Point Stats[/u][/b]\n')

    for tiertotal in sorted(tiertotals):
        lts = list(filter(lambda x: x.total == tiertotal, leveltierpoints))
        earned = sum(lt.earned for lt in lts)
        total = sum(lt.total for lt in lts)
        if earned != total:
            f.write('\n[color=#%s]/%d[/color]: %d/%d [color=#%s]TPs[/color]' % (HEX_D, tiertotal, earned, total, HEX_TP))

    totalaaas = len(list(filter(lambda x: x.isAAA(), alllevelranks)))
    extratierpoints = max(int(100 * totalaaas / len(alllevelranks)) - 49, 0)
    maxextratierpoints = 50

    f.write('\n[color=#%s]+[/color]: %d/%d [color=#%s]TPs[/color]' % (HEX_D, extratierpoints, maxextratierpoints, HEX_TP))

    earnedtierpoints = sum(l.earned for l in leveltierpoints) + extratierpoints
    totaltierpoints = sum(l.total for l in leveltierpoints) + maxextratierpoints
    
    f.write('\n\n[color=#%s]TPs[/color]: %d/%d %.1f%%' % (HEX_TP, earnedtierpoints, totaltierpoints, 100 * earnedtierpoints / totaltierpoints))

br.post_stats(open(output_filename, 'r').read())
