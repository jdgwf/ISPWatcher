#ISPWatcher

##Overview
ISPWatcher is a small python script that will watch various websites services via an XML or JSON file and email recipients if the service is down.

Create your controlfile.xml or controlfile.json by either copying the sample or following the from either of the sample files.

##Cronjob Example
I recommend creating a cron job for every 15 minutes.

	#minute hour    mday    month   wday            command
	#-------------------------------------------------------------------------------
	*/15    *       *       *       *       /home/gauthic/bin/ispwatcher/ispwatcher.py >> /home/gauthic/bin/ispwatcher/ispwatcher.log

Don't forget to chmod +x the ispwatcher.py file if you use the above as well as check the path to the python binary that's in the script file declaration on line 1  If all else fails you should be able to:

	#minute hour    mday    month   wday            command
	#-------------------------------------------------------------------------------
	*/15    *       *       *       *       python /home/gauthic/bin/ispwatcher/ispwatcher.py >> /home/gauthic/bin/ispwatcher/ispwatcher.log

###NOTE
**If you are download the new version of ISPwatcher make note in your crontab that the new filename for the script is now all lower case! ispwatcher.py**

##Version History
* 2.0.0 - November 1, 2009 -
	Converted from .NET, hence the 2.0 status
* 2.0.1 - November 21, 2009 -
	Added command line options for help (-h), quiet (-q), test (-t) and version (-v)
* 2.0.2 - November 30, 2011 -
	Removed single ticks around HTTP host emails so that iPhone and other devices will link straight to website from email instead of creating a 404
* 2.1.0 - November 28, 2012 -
	Lower Cased Node Names - no more case sensitive XML
	Streamlined code
	Added active field for active/inactive watched services
	JSON control file support support
	Note that there is NO COMMENTING in standard JSON (although I use an unused _comment field), so XML may still be your preference. I don't foresee support for XML going away.
* 3.0.0. - Dec 17, 2019
	Upgraded to Python3



##TO DO
Error catching for JSON and XML Parsing.
