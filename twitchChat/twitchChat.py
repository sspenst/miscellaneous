"""
Outputs twitch chat for the specified channel.

Assumes there is an existing file in this directory named 'credentials'
that contains a username and password in JSON format:
{"NICK":"YOUR_USERNAME","PASS":"oauth:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}

Your OAuth token can be found here: http://www.twitchapps.com/tmi/
"""

import json
import socket
import string

channel = "couragejd"

# Set all the variables necessary to connect to Twitch IRC
HOST = "irc.twitch.tv"
PORT = 6667
readbuffer = ""
MODT = False
credentials = json.loads(open('credentials', 'r').read())

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((HOST, PORT))
s.send("PASS " + credentials["PASS"] + "\r\n")
s.send("NICK " + credentials["NICK"] + "\r\n")
s.send("JOIN #" + channel + " \r\n")

while True:
	readbuffer = readbuffer + s.recv(1024)
	temp = string.split(readbuffer, "\n")
	readbuffer = temp.pop()
	
	for line in temp:
		# Checks whether the message is PING because its a method of Twitch to check if you're afk
		if (line[0] == "PING"):
			s.send("PONG %s\r\n" % line[1])
		else:
			# Splits the given string so we can work with it better
			parts = string.split(line, ":")
			
			if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
				try:
					username = parts[1].split("!")[0]
				except:
					username = ""
			
				try:
					# Sets the message variable to the actual message sent
					message = parts[2][:len(parts[2]) - 1]
				except:
					message = ""
				
				# Only print after twitch is done announcing stuff (MODT = Message of the day)
				if MODT:
					print(username + " : " + message)
					
				# Set MODT to True after the last announcement message
				for l in parts:
					if "End of /NAMES list" in l:
						MODT = True
