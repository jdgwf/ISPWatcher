#!/usr/bin/python
########################################################################################
#
# ISPWatcher2
# Jeffrey D. Gordon
# November 1, 2009
#
# - Testing -
# Tested on MacOS Snow Leopard (10.6) and Ubuntu Linux 9.04 and 9.10
#
# - Version History -
# 2.0.0 - November 1, 2009
#	Converted from .NET to Python (hence the 2.0)
# 2.0.1 - November 21, 2009
#	Added command line options for help (-h), quiet (-q), test (-t) and version (-v)
# 2.0.2 - November 30, 2011
#	Removed single ticks around HTTP host emails so that iPhone and other devices will
#	link straight to website from email instead of creating a 404
# 2.1.0 - November 28, 2012
#	Lower Cased Node Names - no more case sensitive XML
# 	JSON control file support support (also lower cased variable names)
#	Streamlined code
########################################################################################
VERSION = "2.1.0"

import datetime
import urllib
import smtplib
import sys, os
import poplib
import imaplib
import getopt
import json

# Global Variables for command line option handling (see VERSION variable above)
SENDEMAILS = 1
CHATTY = 1
MAILSERVER = "smtp.gmail.com"
MAILSERVERPORT = 587
MAILSERVERUSERNAME = ""
MAILSERVERPASSWORD = ""
MAILSERVERSTARTTLS = 1
MAILFROM = ""
MAILSUBJECT = "ISPWatcher2 Failure"
EMAILS = {'':''}

def printversion():
	"""Prints the version of ISPWatcher2

	Returns nothing."""
	print "* ISPWatcher Version " + VERSION
def printusage():
	"""Prints the usage of ISPWatcher2

	Returns nothing."""
	printversion()
	print "\tispwatcher.py -h - Prints help screen"
	print "\tispwatcher.ph -v - Prints Version information"
	print "\tispwatcher.py -t - Outputs only to standard output, sends no emails"
	print "\tispwatcher.py -q - Checks servers quietly"

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvtq" )
except:
	print str(err)
	printusage()
	sys.exit(2)

for o, a in opts:
	if o == "-h":
		printusage()
		sys.exit()
	if o == "-t":
		SENDEMAILS = 0
	if o == "-q":
		CHATTY = 0
	if o == "-v":
		printversion()
		sys.exit()

from xml.dom import minidom

reload(sys)
sys.setdefaultencoding("latin1")

def CheckServerJSON(settings):
#	print settings
	for key, value in settings["options"].items():
		if key.lower() == "mailserver":
			MAILSERVER = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailserver: " + MAILSERVER)

		if key.lower() == "mailserverport":
			MAILSERVERPORT = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailserverport: " + MAILSERVERPORT)

		if key.lower() == "mailserverusername":
			MAILSERVERUSERNAME = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailserverusername: " + MAILSERVERUSERNAME)

		if key.lower() == "mailserverstarttls":
			MAILSERVERSTARTTLS = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailserverstarttls: " + MAILSERVERSTARTTLS)

		if key.lower() == "mailserverpassword":
			MAILSERVERPASSWORD = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailserverpassword: " + MAILSERVERPASSWORD)

		if key.lower() == "mailfrom":
			MAILFROM = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailfrom: " + MAILFROM)

		if key.lower() == "mailsubject":
			MAILSUBJECT = value;
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found JSON configuration mailsubject: " + MAILSUBJECT)

	for server in settings["servers"]:
		sms = "0"
		host = ""
		recipients = []
		watchfor = ""
		warnif = ""
		port = "0"
		type = ""
		active = "1"

		timeoutalert = "0"
		for key, value in server.items():
			key = key.lower()
			if key == "type":
				type = value
			if key == "host":
				host = value
			if key == "recipients":
				recipients.append(value)
			if key == "watchfor":
				watchfor = value
			if key == "warnif":
				warnif = value
			if key == "port":
				port = value
			if key == "timeoutalert":
				timeoutalert = value
			if key == "active":
				active = value

		if type == "http":
			if port == "0":
				port = "80"
			if active == "1":
				CheckHTTPServer(host, port, recipients, watchfor, warnif, sms, timeoutalert)
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
		if type == "smtp":
			if port == "0":
				port = "25"
			if active == "1":
				CheckSMTPServer(host, port, recipients, watchfor, sms, timeoutalert)
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
		if type == "pop3":
			if port == "0":
				port = "110"
			if active == "1":
				CheckPOP3Server(host, port, recipients, watchfor, sms, timeoutalert)
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
		if type == "imap" or type == "imap4":
			if port == "0":
				port = "143"
			if active == "1":
				CheckIMAPServer(host, port, recipients, watchfor, sms, timeoutalert)
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
		if type == "pop3ssl" or type == "popssl":
			if port == "0":
				port = "995"
			if active == "1":
				CheckPOP3SSLServer(host, port, recipients, watchfor, sms, timeoutalert)
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
		if type == "imapssl" or type == "imap4ssl":
			if port == "0":
				port = "993"
			if active == "1":
				CheckIMAPSSLServer(host, port, recipients, watchfor, sms, timeoutalert)
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")

def CheckServerXML(oServer):
	"""Parses through XML Object of Server and delegates oServer object to otehr functionstype in server type

	Returns nothing."""
	global MAILSERVER
	global MAILSERVERPORT
	global MAILSERVERUSERNAME
	global MAILSERVERPASSWORD
	global MAILFROM
	global MAILSERVERSTARTTLS
	global MAILSUBJECT
	type = ""
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if oAttributes.nodeName.lower() == "type":
				type =  oAttributes.childNodes[0].nodeValue
			if oAttributes.nodeName.lower() == "mailserver":
				MAILSERVER =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailServer: " + MAILSERVER)

			if oAttributes.nodeName.lower() == "mailserverport":
				MAILSERVERPORT =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailServerPort: " + MAILSERVERPORT)

			if oAttributes.nodeName.lower() == "mailserverusername":
				MAILSERVERUSERNAME =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailServerUserName: " + MAILSERVERUSERNAME)

			if oAttributes.nodeName.lower() == "mailserverstarttls":
				MAILSERVERSTARTTLS =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailServerStartTLS: " + MAILSERVERSTARTTLS)

			if oAttributes.nodeName.lower() == "mailserverpassword":
				MAILSERVERPASSWORD =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailServerPassword: " + MAILSERVERPASSWORD)

			if oAttributes.nodeName.lower() == "mailfrom":
				MAILFROM =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailFrom: " + MAILFROM)

			if oAttributes.nodeName.lower() == "mailsubject":
				MAILSUBJECT =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found XML configuration MailSubject: " + MAILSUBJECT)


	sms = "0"
	host = ""
	recipients = []
	watchfor = ""
	warnif = ""
	port = "0"
	active = "1"
	timeoutalert = "0"

	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName.lower() == "host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName.lower() == "port":
				port =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName.lower() == "recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName.lower() == "warnif":
				warnif =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName.lower() == "watchfor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName.lower() == "sms":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName.lower() == "timeoutalert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName.lower() == "active":
				active =  oAttributes.childNodes[0].nodeValue

	if type == "http":
		if port == "0":
			port = "80"
		if active == "1":
			CheckHTTPServer(host, port, recipients, watchfor, warnif, sms, timeoutalert)
		else:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
	if type == "smtp":
		if port == "0":
			port = "25"
		if active == "1":
			CheckSMTPServer(host, port, recipients, watchfor, sms, timeoutalert)
		else:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
	if type == "pop3" or type == "pop":
		if port == "0":
			port = "110"
		if active == "1":
			CheckPOP3Server(host, port, recipients, watchfor, sms, timeoutalert)
		else:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
	if type == "imap" or type == "imap4":
		if port == "0":
			port = "143"
		if active == "1":
			CheckIMAPServer(host, port, recipients, watchfor, sms, timeoutalert)
		else:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
	if type == "pop3ssl" or type == "popssl":
		if port == "0":
			port = "995"
		if active == "1":
			CheckPOP3SSLServer(host, port, recipients, watchfor, sms, timeoutalert)
		else:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")
	if type == "imapssl" or type == "imap4ssl":
		if port == "0":
			port = "993"
		if active == "1":
			CheckIMAPSSLServer(host, port, recipients, watchfor, sms, timeoutalert)
		else:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Ignoring inactive server " + type + "://" + host + ":" + port + " - edit config to reenable")

def CheckPOP3SSLServer(host, port, recipients, watchfor, sms, timeoutalert):
	"""Parses through XML Object of Server and checks server as per type


	Returns nothing."""

	try:
		a = poplib.POP3_SSL(host, int(port))
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to POP3 (SSL) host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to POP3 (SSL) host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "POP3 (SSL) Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M") + " (" + str(sys.exc_info()[0]) + ")", "POP3", sms)

def CheckPOP3Server(host, port, recipients, watchfor, sms, timeoutalert):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""

	try:
		a = poplib.POP3(host, int(port), 15)
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to POP3 host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to POP3 host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "POP3 Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M") + " (" + str(sys.exc_info()[0]) + ")", "POP3", sms)

def CheckIMAPSSLServer(host, port, recipients, watchfor, sms, timeoutalert):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""

	try:
		a = imaplib.IMAP4_SSL(host, int(port))
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to IMAP4 (SSL) host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to IMAP4 (SSL) host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "IMAP4 (SSL) Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M"), "IMAP4", sms)

def CheckIMAPServer(host, port, recipients, watchfor, sms, timeoutalert):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""

	try:
		a = imaplib.IMAP4(host, int(port))
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to IMAP4 host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to IMAP4 host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "IMAP4 Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M"), "IMAP4", sms)

def CheckSMTPServer(host, port, recipients, watchfor, sms, timeoutalert):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""

	try:
		smtpserver = smtplib.SMTP(host, int(port), '', 30)
		smtpserver.ehlo()
		smtpserver.quit()
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to SMTP host '" + host + "' on port " + port)
 	except:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to SMTP host '" + host + "'")
			CreateEmailMessage(recipients, "SMTP Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M"), "SMTP", sms)


def CheckHTTPServer(host, port, recipients, watchfor, warnif, sms, timeoutalert):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""
	try:
		page = urllib.urlopen(host)
		pagedata = page.read()
		pagedata = pagedata.lower()
		sms = sms.lower()
		watchfor = watchfor.lower()
		if sms != "true" or sms != "1" or sms != "yes":
			sms = "0"
		if warnif != "":
			if pagedata.find(watchfor) > 0:
				CreateEmailMessage(recipients, "HTTP Error: Found '" + warnif + "' in " + host + " at " +  now.strftime("%Y-%m-%d %H:%M"), "HTTP", sms)
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR '" + warnif + "' was found in HTTP host " + host + "")
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": '" + warnif + "' was found in HTTP host " + host + "")
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": '" + warnif + "' was not found in HTTP host " + host + "")
		if watchfor != "":
			if pagedata.find(watchfor) == -1:
				CreateEmailMessage(recipients, "HTTP Error: Can't find '" + watchfor + "' in " + host + " at " +  now.strftime("%Y-%m-%d %H:%M"), "HTTP", sms)
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR '" + watchfor + "' was NOT found in HTTP host " + host + "")
			else:
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": '" + watchfor + "' was found in HTTP host " + host + "")
	except:
		CreateEmailMessage(recipients, "HTTP Error: Can't connect to " + host + " at " +  now.strftime("%Y-%m-%d %H:%M"), "HTTP", sms)
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Can't connect to HTTP host " + host + "")

def CreateEmailMessage(recipients, message, type, sms):
	"""Creates an email message and stacks them on the EMAILS global variable

	Returns nothing."""
	for emails in recipients:
		for recipient in emails.split(","):
			if recipient in EMAILS:
				EMAILS[recipient] =  EMAILS[recipient] + "\n" + message
			else:
				EMAILS[recipient] =  message

def SendEmails():
	"""Parses through EMAIL global variable and sends error emails via SMTP

	Returns nothing."""
        global MAILSERVER
        global MAILSERVERPORT
        global MAILSERVERSTARTTLS
        global MAILSERVERUSERNAME
        global MAILSERVERPASSWORD
        global MAILFROM
        global MAILSUBJECT

	MAILSERVERPORT = int(MAILSERVERPORT)

	day = now.strftime('%a')
	date = now.strftime('%d %b %Y %X')

	for recipients in  EMAILS.keys():
		message = EMAILS[recipients]
		if message.lstrip().rstrip() != "" and recipients != "":
			email = """\
From: %s
To: %s
Subject: %s
Date: %s

%s
""" % (MAILFROM, recipients, MAILSUBJECT, day + ', ' + date + ' -0000', message)

			server = smtplib.SMTP(MAILSERVER,MAILSERVERPORT)
			if MAILSERVERSTARTTLS > 0:
				server.starttls()
				server.ehlo()
			server.login(MAILSERVERUSERNAME,MAILSERVERPASSWORD)
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Sending Email Message to '" + recipients + "'")
			server.sendmail(MAILFROM,recipients, email)
			server.quit()

def MakeLog(logstring):
	if CHATTY > 0:
		print logstring
now = datetime.datetime.now()
if CHATTY > 0:
	print("Starting ISPWatcher2 at " + now.strftime("%Y-%m-%d %H:%M"))

# Found a JSON File
path = sys.path[0] + "/controlfile.json"
if os.path.isfile(path):
	if CHATTY > 0:
		print "* Using config file " + path
	json_settings = open(path)
	settings = json.load(json_settings)
	json_settings.close()
	CheckServerJSON(settings)
else:
	# Found an XML File
	path = sys.path[0] + "/ControlFile.xml"
	if os.path.isfile(path):
		if CHATTY > 0:
			print "* Using config file " + path
		dom = minidom.parse(path)
		for oDocument in dom.childNodes:
			for oServer in oDocument.childNodes:
				CheckServerXML(oServer)
		if SENDEMAILS > 0:
			SendEmails()
		else:
			if CHATTY > 0:
				print "* TEST MODE ENABLED - not sending emails"
	else:
		path = sys.path[0] + "/controlfile.xml"
		if os.path.isfile(path):
			if CHATTY > 0:
				print "* Using config file " + path
			dom = minidom.parse(path)
			for oDocument in dom.childNodes:
				for oServer in oDocument.childNodes:
					CheckServerXML(oServer)
			if SENDEMAILS > 0:
				SendEmails()
			else:
				if CHATTY > 0:
					print "* TEST MODE ENABLED - not sending emails"
		else:
			print "* No controlfile.json or controlfile.xml was found"
