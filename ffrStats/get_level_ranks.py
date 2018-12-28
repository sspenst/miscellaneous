"""
Collects all FFR level rank data (excluding token level ranks) given a
user's credentials and stores the results in 'output_file'. The reuslts
are ordered so that the easiest and lowest ranking levels that still
need to be AAA'd appear first.

Assumes there is an existing file in this directory named 'credentials'
that contains a username and password in JSON format:
{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}
"""

from collections import OrderedDict
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from tabulate import tabulate
import json
import re
import sys

output_file = 'level_ranks.txt'

def get_data(credentials, stats_username):
	"""
	Given a credentials object, returns all level rank data for 'stats_username'.
	"""
	url_base = 'http://www.flashflashrevolution.com'
	url_levelrank = url_base + '/levelrank.php?sub=' + stats_username

	# start the Chrome webdriver
	chrome_options = Options()
	chrome_options.add_argument('--headless')
	driver = webdriver.Chrome(chrome_options=chrome_options)

	print('[+] GET ' + url_base)
	driver.get(url_base)

	# send login credentials and submit the form
	print('[+] Logging in with credentials...')
	driver.find_element_by_name('vb_login_username').send_keys(credentials['username'])
	driver.find_element_by_name('vb_login_password').send_keys(credentials['password'])
	driver.find_element_by_class_name('login-button-fix').click()

	# collect data from login page
	print('[+] GET ' + url_levelrank)
	driver.get(url_levelrank)
	
	# check if the login was successful
	try:
		tbody = driver.find_element_by_xpath('//tbody[1]')
	except NoSuchElementException:
		print("[+] ERROR: Invalid login credentials")
		driver.quit()
		sys.exit()
	
	print('[+] Scraping level ranks...')
	raw_data = tbody.text

	driver.quit()

	return raw_data

def format_data(raw_data):
	"""
	Given raw level rank data, returns a list of OrderedDict objects containing the
	difficulty, rank, and name of all levels that have not been AAA'd.
	"""
	print('[+] Formatting level ranks...')
	lines = raw_data.strip().split('\n')
	levels = []

	for line in lines:
	    # skip entries that are already AAA'd
	    rank = int(re.sub('[,]', '', line.split(' ')[0]))
	    if rank != 1:
	        # extract meaningful data for each level
	        difficulty = int(line.split(' ')[1])
	        name = ' '.join(line.split(' ')[2:-8])
	
	        levels.append(OrderedDict([('D', difficulty),
	            ('Rank', rank),
	            ('Name', name)]))
	
	return levels

credentials = json.loads(open('credentials', 'r').read())

# get the username that the stats will be retrieved for
stats_username = credentials['username']
if len(sys.argv) == 2:
	stats_username = sys.argv[1]
elif len(sys.argv) != 1:
	print('Invalid argument format. Please call this script with the following format:')
	print('\tpython3 get_level_ranks.py <OPTIONAL:stats_username>')
	sys.exit()

raw_data = get_data(credentials, stats_username)
levels = format_data(raw_data)

# sort the level data primarily by difficulty, and secondly by highest rank
sorted_levels = sorted(levels, key=lambda level:level['Rank'], reverse=True)
sorted_levels = sorted(sorted_levels, key=lambda level:level['D'])

with open(output_file, 'w') as f:
    f.write(tabulate(sorted_levels, headers='keys', tablefmt='presto'))

print('[+] Level ranks written to ' + output_file)
