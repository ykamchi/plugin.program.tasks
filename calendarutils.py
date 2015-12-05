import os
import datetime
from datetime import date
import httplib2
import xbmcaddon
from email.mime.text import MIMEText
import utils
import oauth2client
import webbrowser
from oauth2client import client
from oauth2client import tools
from oauth2client import file

libDir = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'lib')
os.sys.path.insert(0, libDir)
import googleapiclient
from googleapiclient import discovery

import tzlocal
from tzlocal import get_localzone



from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


class CalendarConnection(object):
	
	
	
	def __init__(self):
		credentials = self.get_credentials()
		http = credentials.authorize(httplib2.Http())
		self.service = discovery.build('calendar', 'v3', http=http)
		self.calendars = self.getCalendars()
		self.colors = self.getColors()
		eventId_calendarId = {}
		self.date_to_events = {}
		self.calendar_control_to_calendar_name = {}
		
	def getEvents(self, start_calendar_date, end_calendar_date):
		events = []
		self.eventId_calendarId = {}
		self.date_to_events = {}
		
		s = utils.formatDateTime_get_iso(start_calendar_date) + 'Z'
		e = utils.formatDateTime_get_iso(end_calendar_date) + 'Z'
		print str(s) + " --- " + str(e)
		tmp_events=[]
		# Loop over all calendars
		for cal in self.calendars:
			# Check if calendar is enabled
			if self.is_selected(cal['summary']):
				eventsResult = self.service.events().list(calendarId=cal['id'], timeMin=s, timeMax=e, maxResults=100, singleEvents=True, orderBy='startTime').execute()
				tmp_events = eventsResult.get('items', [])
				
				# Save mapping
				for event in tmp_events:
					# Map event id to calendar id
					self.eventId_calendarId[event['id']] = cal['id']
					if not utils.formatDate(event, 'start') in self.date_to_events:
						self.date_to_events[utils.formatDate(event, 'start')] = []
					self.date_to_events[utils.formatDate(event, 'start')].append(event)
				
				events.extend(tmp_events)
		return events
		
	def deleteEvent(self, e):
		self.service.events().delete(calendarId=self.eventId_calendarId[e['id']], eventId=e['id']).execute()
		
	def createEvent(self, e):
		event = self.service.events().insert(calendarId='primary', body=e).execute()

	def updateEvent(self, e):
		event = e
		updated_event = self.service.events().update(calendarId=self.eventId_calendarId[event['id']], eventId=event['id'], body=event).execute()
		
	def getColors(self):
		colorsListResult = self.service.colors().get().execute()
		colors = colorsListResult.get('calendar')
		return colors

	def getCalendars(self):
		calendarListResult = self.service.calendarList().list().execute()
		calendars = calendarListResult['items']
		return calendars

	def getCalendarColor(self, color_id):
		cal_color = str(self.colors[color_id].get('background'))
		while cal_color[0] == '#': cal_color = cal_color[1:]
		return '0xFF'+cal_color

	def is_selected(self, calendar_name):
		tmp = utils.addon.getSetting(calendar_name.encode('utf-8'))
		if not tmp or tmp == '':
			tmp = '1'
		return int(tmp)

	def createNewEventBody(self, start_time, end_time):
		timezone = utils.addon.getSetting('timezone')
		if not timezone:
			timezone = get_localzone() 
		event = {
		  'summary': '',
		  'location': '',
		  'description': '',
		  'start': {
			'dateTime': start_time,
			'timeZone': str(timezone),
		  },
		  'end': {
			'dateTime': end_time,
			'timeZone': str(timezone),
		  },
		  'recurrence': [
		  ],
		  'attendees': [
			{'email': 'yohay.kamchi@gmail.com'},
		  ],
		  'reminders': {
			'useDefault': False,
			'overrides': [
			  {'method': 'email', 'minutes': 24 * 60},
			],
		  },
		}

		return event #= service.events().insert(calendarId='primary', body=event).execute()

	def get_credentials(self):
		store = oauth2client.file.Storage(os.path.join(utils.userpath, 'calendar-quickstart'+utils.username+'.json'))		
		credentials = store.get()
		if not credentials or credentials.invalid:
			print "2"
			client_id = '987683463712-se9dhv6gteobsmlpkgvqptub59fajuiq.apps.googleusercontent.com'
			print "3"
			client_secret = os.path.join(utils.addonpath,'client_secret.json')
			print "4"
			scope = 'https://www.googleapis.com/auth/calendar'
			redirect_uri='urn:ietf:wg:oauth:2.0:oob'
			flow = oauth2client.client.flow_from_clientsecrets(client_secret, scope, redirect_uri)
			auth_uri = flow.step1_get_authorize_url()
			webbrowser.open(auth_uri)
			auth_code = utils.getKeyboardResults("", 'Code')
			credentials = flow.step2_exchange(auth_code)
			store.put(credentials)
		return credentials
		
	def get_credentials_old(self):
		"""Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
			Credentials, the obtained credential.
		"""
		store = oauth2client.file.Storage(os.path.join(utils.userpath, 'calendar-quickstart'+utils.username+'.json'))		
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(os.path.join(utils.addonpath,'client_secret.json'), 'https://www.googleapis.com/auth/calendar')
			flow.user_agent = 'Google Calendar API Quickstart'
			flags = tools.argparser.parse_args(args=[])
			if flags:
				credentials = tools.run_flow(flow, store, flags)
			else: # Needed only for compatability with Python 2.6
				credentials = tools.run(flow, store)
			
		return credentials
	

	