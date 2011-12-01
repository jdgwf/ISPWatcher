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
# 2.0.2 - November 30, 2011 
#	Removed single ticks around HTTP host emails so that iPhone and other devices will 
#	link straight to website from email instead of creating a 404
# 2.0.1 - November 21, 2008 
#	Added command line options for help (-h), quiet (-q), test (-t) and version (-v)
#
########################################################################################
VERSION = "2.0.2"

import datetime
import urllib
import smtplib
import sys, os
import poplib
import imaplib
import getopt

# Global Variables for command line option handling (see VERSION variable above)
SENDEMAILS = 1
CHATTY = 1
MAILSERVER = "smtp.gmail.com"
MAILSERVERPORT = 587
MAILSERVERUSERNAME = ""
MAILSERVERPASSWORD = ""
MAILSERVERSTARTTLS = 1
MAILFROM = ""
EMAILS = {'':''}

def printversion():
	"""Prints the version of ISPWatcher2

	Returns nothing."""
	print "* ISPWatcher2 Version " + VERSION
def printusage():
	"""Prints the usage of ISPWatcher2

	Returns nothing."""
	printversion()
	print "\tISPWatcher.py -h - Prints help screen"
	print "\tISPWatcher.ph -v - Prints Version information"
	print "\tISPWatcher.py -t - Outputs only to standard output, sends no emails"
	print "\tISPWatcher.py -q - Checks servers quietly"

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

def CheckServer(oServer):
	"""Parses through XML Object of Server and delegates oServer object to otehr functionstype in server type
	

	Returns nothing."""
	global MAILSERVER
	global MAILSERVERPORT
	global MAILSERVERUSERNAME
	global MAILSERVERPASSWORD
	global MAILFROM
	global MAILSERVERSTARTTLS
	type = ""
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if oAttributes.nodeName == "Type":
				type =  oAttributes.childNodes[0].nodeValue
			if oAttributes.nodeName == "MailServer":
				MAILSERVER =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found configuration MailServer: " + MAILSERVER)
			
			if oAttributes.nodeName == "MailServerPort":
				MAILSERVERPORT =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found configuration MailServerPort: " + MAILSERVERPORT)
			
			if oAttributes.nodeName == "MailServerUserName":
				MAILSERVERUSERNAME =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found configuration MailServerUserName: " + MAILSERVERUSERNAME)

			if oAttributes.nodeName == "MailServerStartTLS":
				MAILSERVERSTARTTLS =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found configuration MailServerStartTLS: " + MAILSERVERSTARTTLS)

			if oAttributes.nodeName == "MailServerPassword":
				MAILSERVERPASSWORD =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found configuration MailServerPassword: " + MAILSERVERPASSWORD)
			
			if oAttributes.nodeName == "MailFrom":
				MAILFROM =  oAttributes.childNodes[0].nodeValue
				MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Found configuration MailFrom: " + MAILFROM)


	if type == "http":
		CheckHTTPServer(oServer)
	if type == "smtp":
		CheckSMTPServer(oServer)
	if type == "pop3" or type == "pop":
		CheckPOP3Server(oServer)
	if type == "imap" or type == "imap4":
		CheckIMAPServer(oServer)
	if type == "pop3ssl" or type == "popssl":
		CheckPOP3SSLServer(oServer)
	if type == "imapssl" or type == "imap4ssl":
		CheckIMAPSSLServer(oServer)

def CheckPOP3SSLServer(oServer):
	"""Parses through XML Object of Server and checks server as per type
	

	Returns nothing."""

	sms = "0"
	port = "995"
	host = ""
	recipients = []
	watchfor = ""
	timeoutalert = "0"
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName == "Host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Port":
				port =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName == "WatchFor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "SMS":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "TimeoutAlert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue
	try:
		a = poplib.POP3_SSL(host, int(port))
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to POP3 (SSL) host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to POP3 (SSL) host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "POP3 (SSL) Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M") + " (" + str(sys.exc_info()[0]) + ")", "POP3", sms)

def CheckPOP3Server(oServer):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""
	sms = "0"
	port = "110"
	host = ""
	recipients = []
	watchfor = ""
	timeoutalert = "0"
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName == "Host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Port":
				port =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName == "WatchFor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "SMS":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "TimeoutAlert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue
	try:
		a = poplib.POP3(host, int(port), 15)
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to POP3 host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to POP3 host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "POP3 Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M") + " (" + str(sys.exc_info()[0]) + ")", "POP3", sms)

def CheckIMAPSSLServer(oServer):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""
	sms = "0"
	port = "993"
	host = ""
	recipients = []
	watchfor = ""
	timeoutalert = "0"
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName == "Host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Port":
				port =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName == "WatchFor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "SMS":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "TimeoutAlert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue
	try:
		a = imaplib.IMAP4_SSL(host, int(port))
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to IMAP4 (SSL) host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to IMAP4 (SSL) host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "IMAP4 (SSL) Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M"), "IMAP4", sms)

def CheckIMAPServer(oServer):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""
	sms = "0"
	port = "143"
	host = ""
	recipients = []
	watchfor = ""
	timeoutalert = "0"
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName == "Host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Port":
				port =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName == "WatchFor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "SMS":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "TimeoutAlert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue
	try:
		a = imaplib.IMAP4(host, int(port))
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to IMAP4 host '" + host + "' on port " + port)
 	except:
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to IMAP4 host '" + host + "' on port " + port + " Error- " + str(sys.exc_info()[0]))
		CreateEmailMessage(recipients, "IMAP4 Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M"), "IMAP4", sms)

def CheckSMTPServer(oServer):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""
	sms = "0"
	port = "25"
	host = ""
	recipients = []
	watchfor = ""
	timeoutalert = "0"
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName == "Host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Port":
				port =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName == "WatchFor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "SMS":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "TimeoutAlert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue

	try:
		smtpserver = smtplib.SMTP(host, int(port), '', 30)
		smtpserver.ehlo()
		smtpserver.quit()
		MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": Connected successfully to SMTP host '" + host + "' on port " + port)
 	except:
			MakeLog( now.strftime("%Y-%m-%d %H:%M") + ": ERROR can't connect to SMTP host '" + host + "'")
			CreateEmailMessage(recipients, "SMTP Error: Can't connect to '" + host + "' at " +  now.strftime("%Y-%m-%d %H:%M"), "SMTP", sms)


def CheckHTTPServer(oServer):
	"""Parses through XML Object of Server and checks server as per type

	Returns nothing."""
	sms = "0"
	host = ""
	recipients = []
	watchfor = ""
	warnif = ""
	timeoutalert = "0"
	for oAttributes in oServer.childNodes:
		if oAttributes.nodeType != minidom.Node.TEXT_NODE:
			if  oAttributes.nodeName == "Host":
				host =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "Recipients":
				recipients.append(oAttributes.childNodes[0].nodeValue)
			if  oAttributes.nodeName == "WarnIf":
				warnif =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "WatchFor":
				watchfor =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "SMS":
				sms =  oAttributes.childNodes[0].nodeValue
			if  oAttributes.nodeName == "TimeoutAlert":
				timeoutalert =  oAttributes.childNodes[0].nodeValue

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

	MAILSERVERPORT = int(MAILSERVERPORT)

	for recipients in  EMAILS.keys():
		message = EMAILS[recipients]
		if message.lstrip().rstrip() != "" and recipients != "":
			email = """\
From: %s
To: %s
Subject: %s

%s
""" % (MAILFROM, recipients, "ISPWatcher2 Failure", message)

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

dom = minidom.parse(sys.path[0] + "/ControlFile.xml")
for oDocument in dom.childNodes:
	for oServer in oDocument.childNodes:
		CheckServer(oServer)
if SENDEMAILS > 0:
	SendEmails()
else:
	if CHATTY > 0:
		print "* TEST MODE ENABLED - not sending emails"
