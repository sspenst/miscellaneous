"""
Collects all FFR level rank data given a valid FFR API key and stores
the results in 'output_file'. The reuslts are ordered so that the easiest
and lowest ranking levels that still need to be AAA'd appear first.

Assumes there is an existing file in this directory named 'credentials'
that contains a valid FFR API key in JSON format:
{"key":"YOUR_API_KEY"}

Note that the FFR API is a bit sketchy. The resulting data produced by
this script is not guaranteed to be 100% accurate.
"""

from collections import OrderedDict
from tabulate import tabulate
import json
import os
import requests
import sys

output_file = 'level_ranks.txt'

# check for valid arguments
if len(sys.argv) != 2:
	print('Invalid argument format. Please call this script with the following format:')
	print('\tpython3 api_level_ranks.py <username>')
	sys.exit()

# set up variables
username = sys.argv[1]
api_key = json.loads(open('credentials', 'r').read())['key']
url = 'http://www.flashflashrevolution.com/api/api.php?key=' + api_key + '&action=ranks&username=' + username

# call the API and check for errors
print('[+] Fetching level ranks...')
json_ranks = requests.get(url).json()
if 'error' in json_ranks:
	print('ERROR: Invalid user specified')
	sys.exit()

print('[+] Formatting level ranks...')
levels = []
for level in json_ranks['songs']:
	# extract meaningful data for each level
	difficulty = int(json_ranks['songs'][level]['info']['difficulty'])
	rank = int(json_ranks['songs'][level]['scores']['rank'])
	name = json_ranks['songs'][level]['info']['name']

	if rank != 1:
		levels.append(OrderedDict([('D', difficulty),
			('Rank', rank),
			('Name', name)]))

# sort the level data primarily by difficulty, and secondly by highest rank
sorted_levels = sorted(levels, key=lambda level:level['Rank'], reverse=True)
sorted_levels = sorted(sorted_levels, key=lambda level:level['D'])

with open(output_file, 'w') as f:
    f.write(tabulate(sorted_levels, headers='keys', tablefmt='presto'))

print('[+] Level ranks written to ' + output_file)
