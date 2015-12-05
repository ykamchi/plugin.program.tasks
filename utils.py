# -*- coding: utf-8 -*-
from datetime import date
import datetime
import pytz
import dateutil.parser
import xbmcgui
import os
import xbmcaddon
from dateutil import relativedelta
import calendarutils
import urllib2,re,httplib2
import googleapiclient
from googleapiclient import discovery
import xbmc
import math



addon 			= xbmcaddon.Addon()
addonname 		= addon.getAddonInfo('name')
addonpath 		= addon.getAddonInfo('path')


media_path 		= os.path.join(addon.getAddonInfo('path'),'resources','media')
if addon.getSetting('media_path'):
	media_path 		= os.path.join(media_path, addon.getSetting('media_path'))
	
username 		= addon.getSetting('username')
userpath 		= xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8') 


ALIGN_LEFT = 0
ALIGN_RIGHT = 1
ALIGN_CENTER = 6
ACTION_PREVIOUS_MENU = 10
 
colors = {'black':'0xff000000','gray':'0xff808080','white':'0xffffffff','aqua':'0xff00ffff','red':'0xffff0000','green':'0xff00ff00','blue':'0xff0000ff','yellow':'0xffffff00','fuchsia':'0xffff00ff','cyan':'0xff00ffff'}
COLOR_LABEL_REGULAR				= colors[addon.getSetting('regular_font_color')]
COLOR_LABEL_SELECTED			= colors[addon.getSetting('selected_font_color')]
COLOR_LABEL_HEADER				= colors[addon.getSetting('header_font_color')]
COLOR_LABEL_FOCUSE				= colors[addon.getSetting('focuse_font_color')]
COLOR_LABEL_LABEL				= colors[addon.getSetting('lable_font_color')]

views = {'day':'day_view','week':'week_view','month':'month_view'}
VIEW_TYPE_DAY					= views['day']
VIEW_TYPE_MONTH					= views['month']
VIEW_TYPE_WEEK					= views['week']
default_view	= views[addon.getSetting('default_view')]

CONTROL_TYPE_TODAY_NAVIGATION	= 'nothing'
CONTROL_TYPE_NOTHING			= 'nothing'
CONTROL_TYPE_DATE				= 'date'
CONTROL_TYPE_DATE_NAVIGATION	= 'date_navigation'
CONTROL_TYPE_YEAR				= 'year'
CONTROL_TYPE_YEAR_NAVIGATION	= 'year_navigation'
CONTROL_TYPE_MONTH				= 'month'
CONTROL_TYPE_MONTH_NAVIGATION	= 'month_navigation'
CONTROL_TYPE_ACTION				= 'action'
CONTROL_TYPE_HOUR				= 'hour'
CONTROL_TYPE_HOUR_NAVIGATION	= 'hour_navigation'
CONTROL_TYPE_MINUTE				= 'minute'
CONTROL_TYPE_MINUTE_NAVIGATION	= 'minute_navigation'
CONTROL_TYPE_EVENT_SUMMARY		= 'event_summary'
CONTROL_TYPE_EVENT_LOCATION		= 'event_location'
CONTROL_TYPE_EVENT_DESCRIPTION	= 'event_description'
CONTROL_TYPE_GOTO				= 'goto'
CONTROL_TYPE_TASK_SLOT			= 'task_slot'
CONTROL_TYPE_TIMEZONE_LIST		= 'timezone_list'
CONTROL_TYPE_TIMEZONE			= 'timezone'
CONTROL_TYPE_CALENDAR			= 'calendar'
CONTROL_TYPE_EVENT				= 'event'
CONTROL_TYPE_BEFORE_NAVIGATION	= 'before_navigation'
CONTROL_TYPE_AFTER_NAVIGATION	= 'after_navigation'
CONTROL_TYPE_VIEW				= 'view'


CONTROL_VALUE_NOTHIG			= 'nav_next'
CONTROL_VALUE_NAVIGATE_NEXT		= 'nav_next'
CONTROL_VALUE_NAVIGATE_PREVIOS	= 'nav_prev'
CONTROL_VALUE_ACTION_OK			= 'ok'
CONTROL_VALUE_ACTION_CANCEL		= 'cancel'
CONTROL_VALUE_ACTION_DELETE		= 'delete'

background		= os.path.join(media_path,'background.jpg')
logo 			= os.path.join(media_path,'logo.png')
task_a 			= os.path.join(media_path,'task_a.jpg')
task_b 			= os.path.join(media_path,'task_b.jpg')
#back_a 			= os.path.join(media_path,'back_a.png')
#back_b 			= os.path.join(media_path,'back_b.png')
btn_delete_a	= os.path.join(media_path,'btn_delete_a.png')
btn_delete_b	= os.path.join(media_path,'btn_delete_b.png')
btn_off 		= os.path.join(media_path,'off.png')
btn_on 			= os.path.join(media_path,'on.png')
pic_m_back 		= os.path.join(media_path,'m.back.png')
pic_m_forward 	= os.path.join(media_path,'m.forward.png')
pic_y_back 		= os.path.join(media_path,'y.back.png')
pic_y_forward	= os.path.join(media_path,'y.forward.png')



class Data(object):
	def __init__(self, type, value):
		self.type = type
		self.value = value
		self.batchAdd = True

def createButton(x, y, w, h, txt):
	return xbmcgui.ControlButton(x, y, w, h, txt, textColor=COLOR_LABEL_REGULAR, focusedColor=COLOR_LABEL_FOCUSE ,font='font10', focusTexture=task_b , noFocusTexture=task_a)
	
def createLabel(x, y, w, h, txt):
	return xbmcgui.ControlLabel(x ,y ,w ,h ,txt , alignment=ALIGN_LEFT, font='font10', textColor=COLOR_LABEL_LABEL)	
	
def getKeyboardResults(val, header):
	keyboard = xbmc.Keyboard(val, header, False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		val = "%s" %(keyboard.getText())
	return val

def getTypeControl(window, control_to_data, type):
	for ctrl in control_to_data.items():
		if ctrl[1].type == type:
			return ctrl[0]
						
def getSelectedControl(window, selected_date, control_to_data):
	for ctrl in control_to_data.items():
		if ctrl[1].value == selected_date and ctrl[1].type == CONTROL_TYPE_DATE:
			return ctrl[0]
			
def buildTime(left_space, top_space, width, hight, hour, minute):
	ret = []
	space = 10
	button_width = (width-space)/6
	button0 = createButton(left_space, top_space, button_width, hight,  "-")
	ret.append([button0, Data(CONTROL_TYPE_HOUR_NAVIGATION, CONTROL_VALUE_NAVIGATE_PREVIOS)])
	button0 = createButton(left_space+button_width, top_space, button_width, hight,  str(hour))
	ret.append([button0, Data(CONTROL_TYPE_HOUR, hour)])
	button0 = createButton(left_space+2*button_width, top_space, button_width, hight,  "+")
	ret.append([button0, Data(CONTROL_TYPE_HOUR_NAVIGATION, CONTROL_VALUE_NAVIGATE_NEXT)])
	
	button0 = createButton(left_space+space+3*button_width, top_space, button_width, hight,  "-")
	ret.append([button0, Data(CONTROL_TYPE_MINUTE_NAVIGATION, CONTROL_VALUE_NAVIGATE_PREVIOS)])
	button0 = createButton(left_space+space+4*button_width, top_space, button_width, hight,  str(minute))
	ret.append([button0, Data(CONTROL_TYPE_MINUTE, minute)])
	button0 = createButton(left_space+space+5*button_width, top_space, button_width, hight,  "+")
	ret.append([button0, Data(CONTROL_TYPE_MINUTE_NAVIGATION, CONTROL_VALUE_NAVIGATE_NEXT)])
	
	
	return ret
	
def buildMonth(left_space, top_space, width, hight, year, month, selected, calCon):		
	ret=[]
	left_space = left_space + 4
	top_space = top_space + 4
	width = width - 8
	hight = hight - 8
	row_space = 10
	column_space = 10
	header_hight = 34+2*row_space
	row_hight = ((hight-header_hight)-(6*row_space))/7
	column_with = (width-(6*column_space))/7
	theDay = date(year, month, 1)	
	d_current = theDay

	
	# get events
	if calCon != None:
		calCon.getEvents(selected, selected+datetime.timedelta(days=31))
	
	# Add Month header controls
	button0 = createButton(left_space, top_space, (column_with*7+column_space*6), 17,  theDay.strftime("%B, %Y"))
	ret.append([button0, Data(CONTROL_TYPE_MONTH, date(year, month, 1))])
	days = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
	x=0
	for day in days:
		button0 = createButton(left_space+x*(column_with+column_space), top_space+17+row_space, column_with, 17,  day)
		ret.append([button0, Data("nothing", "")])
		x = x + 1

	# Add the Day controls
	row = 0
	while d_current.month == theDay.month:
		weekday = (d_current.weekday()+1)%7
		if weekday == 0 and d_current != theDay:
			row = row + 1

		button0 = createButton(left_space+weekday*(column_with+column_space), top_space+header_hight+row*(row_hight+row_space), column_with, row_hight, d_current.strftime("%d"))
		lbl = d_current.strftime("%d")
		if calCon != None:
			if d_current in calCon.date_to_events:
				for tsk in calCon.date_to_events[d_current]:
					tsk_summary = ''
					if 'summary' in tsk:
						tsk_summary = str(tsk['summary'].encode('utf-8'))
					lbl = lbl + "\n" + tsk_summary
		button0.setLabel(lbl, 'font10', textColor = COLOR_LABEL_REGULAR, focusedColor = COLOR_LABEL_FOCUSE)
		
		ret.append([button0, Data(CONTROL_TYPE_DATE, d_current)])
		
#		if d_current.month != d_next.month:
		#row = row + 1
		d_current = d_current + datetime.timedelta(days=1)
	
	
	return ret

def buildWeek(left_space, top_space, width, hight, year, month, selected, before, after, calCon):		
	ret=[]
	left_space = left_space + 4
	top_space = top_space + 4
	width = width - 8
	hight = hight - 8
	row_space = 10
	column_space = 10
	header_hight = 2*row_space
	days = before + after + 1
	row_hight = ((hight-header_hight)-((days-1)*row_space))/days
	column_with = width
	theDay = selected+relativedelta.relativedelta(days=-before)
	d_current = theDay
	lbl_w = 70
	btn_w = (width/2 - 2*lbl_w - 2*column_space)/4
	
	# get events
	if calCon != None:
		calCon.getEvents(selected+datetime.timedelta(days=-before), selected+datetime.timedelta(days=after))
	
	
	# Add Month header controls
	button0 = createButton(left_space, top_space, width/2, 17,  'Arround - '+str(selected))
	ret.append([button0, Data(CONTROL_TYPE_MONTH, selected)])
	
	nav_l = left_space + width/2+column_space
	button0 = createButton(nav_l, top_space, btn_w, 17,  '-')
	ret.append([button0, Data(CONTROL_TYPE_BEFORE_NAVIGATION, CONTROL_VALUE_NAVIGATE_PREVIOS)])

	button0 = createButton(nav_l + btn_w, top_space, lbl_w, 17,  'Before')
	ret.append([button0, Data(CONTROL_TYPE_NOTHING, CONTROL_VALUE_NOTHIG)])

	button0 = createButton(nav_l + lbl_w + btn_w, top_space, btn_w, 17,  '+')
	ret.append([button0, Data(CONTROL_TYPE_BEFORE_NAVIGATION, CONTROL_VALUE_NAVIGATE_NEXT)])

	
	button0 = createButton(nav_l + lbl_w + 2*btn_w + column_space, top_space, btn_w, 17,  '-')
	ret.append([button0, Data(CONTROL_TYPE_AFTER_NAVIGATION, CONTROL_VALUE_NAVIGATE_PREVIOS)])

	button0 = createButton(nav_l + lbl_w + 3*btn_w + column_space, top_space, lbl_w, 17,  'After')
	ret.append([button0, Data(CONTROL_TYPE_NOTHING, CONTROL_VALUE_NOTHIG)])

	button0 = createButton(nav_l + 2*lbl_w + 3*btn_w + column_space, top_space, btn_w, 17,  '+')
	ret.append([button0, Data(CONTROL_TYPE_AFTER_NAVIGATION, CONTROL_VALUE_NAVIGATE_NEXT)])

	columns = days/8+1
	row_per_col = int(days/columns) + (days%columns > 0) 
	# Add the Day controls
	row = 0
	
	column_with = (column_with - (columns-1)*column_space)/columns
	row_hight = ((hight-header_hight)-((row_per_col-1)*row_space))/row_per_col
	col = 0
	while d_current <= selected+datetime.timedelta(days=after):
		if row >= row_per_col:
			row = 0
			col = col + 1
		lbl = d_current.strftime("%B %d %Y (%A)")			
		left_pos = left_space + (column_space + column_with)*(col)
		button0 = createButton(left_pos, top_space+header_hight+row*(row_hight+row_space), column_with, row_hight, lbl)
		if calCon != None:
			if d_current in calCon.date_to_events:
				for tsk in calCon.date_to_events[d_current]:
					tsk_summary = ''
					if 'summary' in tsk:
						tsk_summary = str(tsk['summary'].encode('utf-8'))
					lbl = lbl + "\n" + tsk_summary
		button0.setLabel(lbl, 'font10', textColor = COLOR_LABEL_REGULAR, focusedColor = COLOR_LABEL_FOCUSE)
		
		ret.append([button0, Data(CONTROL_TYPE_DATE, d_current)])
		row = row + 1
		d_current = d_current + datetime.timedelta(days=1)
	return ret
	
def buildOkCancelButtons(left_space, top_space, width, hight):
	ret=[]
	space=10
	btn_width=(width-space)/2
	button0 = xbmcgui.ControlButton(left_space, top_space, btn_width, hight, "Cancel", font='font10')
	ret.append([button0, Data(CONTROL_TYPE_ACTION, CONTROL_VALUE_ACTION_CANCEL)])
	button0 = xbmcgui.ControlButton(left_space+space+btn_width, top_space, btn_width, hight, "Ok", font='font10')
	ret.append([button0, Data(CONTROL_TYPE_ACTION, CONTROL_VALUE_ACTION_OK)])

	return ret

def buildDeleteButton(left_space, top_space, width, hight):
	ret=[]
	button0 = xbmcgui.ControlButton(left_space, top_space, width, hight, '', font='font10', noFocusTexture=btn_delete_a , focusTexture=btn_delete_b)
	ret.append([button0, Data(CONTROL_TYPE_ACTION, CONTROL_VALUE_ACTION_DELETE)])

	return ret

def builTimezoneView(left_space, top_space, width, hight, selected):
	ret = []
	lst = xbmcgui.ControlList(left_space, top_space+10, width-10, hight, font='font10', textColor = COLOR_LABEL_REGULAR, selectedColor = COLOR_LABEL_SELECTED, buttonTexture=task_a , buttonFocusTexture=task_b)
	ret.append([lst, Data(CONTROL_TYPE_TIMEZONE_LIST, CONTROL_VALUE_NOTHIG)])
	
	return ret
	
def buildTaskView(left_space, top_space, width, hight, event):
	ret = []
	left_space = left_space + 4
	top_space = top_space + 4
	width = width - 8
	hight = hight - 8
	row_hight = 28
	row_space = 10
	column_space = 10
	lbl_width = 75
	date_width = (width - 3*column_space - 2*lbl_width)/2
	row = 0
	
	e_start		= str(formatDateTime(event, 'start'))
	e_end		= str(formatDateTime(event, 'end'))
	if not 'summary' in event: event['summary'] = '' 
	if not 'location' in event: event['location'] = '' 
	if not 'description' in event: event['description'] = '' 	
	
	lbl = createLabel(left_space, top_space+row*(row_hight+row_space), lbl_width, row_hight, "Start:")
	ret.append([lbl, Data("nothing", "")])

	startDay = createButton(left_space + lbl_width +column_space, top_space+row*(row_hight+row_space), date_width, row_hight, e_start)
	ret.append([startDay, Data("start_day", e_start)])
	
	lbl = createLabel(left_space + lbl_width + 2*column_space + date_width , top_space+row*(row_hight+row_space), lbl_width, row_hight, "End:")
	ret.append([lbl, Data("nothing", "")])
	
	endDay = createButton(left_space + 2*lbl_width + 3*column_space + date_width, top_space+row*(row_hight+row_space), date_width, row_hight, e_end)
	ret.append([endDay, Data("end_day", e_end)])
	
	row = row + 1
	lbl = createLabel(left_space , top_space+row*(row_hight+row_space), lbl_width, row_hight, "Summary:")
	ret.append([lbl, Data("nothing", "")])
	
	summary = createButton(left_space + lbl_width +column_space , top_space+row*(row_hight+row_space), width - (lbl_width +column_space), row_hight, event['summary'])
	ret.append([summary, Data(CONTROL_TYPE_EVENT_SUMMARY, event['summary'])])

	row = row + 1
	lbl = createLabel(left_space , top_space+row*(row_hight+row_space), lbl_width, row_hight, "Loc:")
	ret.append([lbl, Data("nothing", "")])
	
	location = createButton(left_space + lbl_width +column_space, top_space+row*(row_hight+row_space), width - (lbl_width +column_space), row_hight, event['location'])
	ret.append([location, Data(CONTROL_TYPE_EVENT_LOCATION, event['location'])])

	row = row + 1
	lbl = createLabel(left_space , top_space+row*(row_hight+row_space), lbl_width, row_hight, "Desc:")
	ret.append([lbl, Data("nothing", "")])

	description = createButton(left_space+ lbl_width +column_space, top_space+row*(row_hight+row_space), width - (lbl_width +column_space), row_hight *4, event['description'])
	ret.append([description, Data(CONTROL_TYPE_EVENT_DESCRIPTION, event['description'])])

	row = row + 1
	lbl = createLabel(left_space , top_space+row*(row_hight+row_space)+3*row_hight, lbl_width, row_hight, "Time Zone:")
	ret.append([lbl, Data("nothing", "")])
	
	tz=''
	if 'timeZone' in event['start']:
		tz=event['start']['timeZone']
	location = createButton(left_space + lbl_width +column_space, top_space+row*(row_hight+row_space) + 3*row_hight, width - (lbl_width +column_space), row_hight, tz)
	ret.append([location, Data(CONTROL_TYPE_TIMEZONE, tz)])
#	 'attendees': [
#    {'email': 'lpage@example.com'},
#    {'email': 'sbrin@example.com'},



	return ret
	
def buildDayView(left_space, top_space, width, selected, calCon):
	ret=[]
	left_space = left_space + 4
	top_space = top_space + 4
	
	row_hight = 28
	row_space = 1
	left_shift = 0
	#width = width - 10
	row = 0
	
	#get events
	start_time = datetime.datetime(selected.year, selected.month, selected.day, 0, 0)
	end_time = selected+relativedelta.relativedelta(minutes=1439)
	print str(start_time) + " <-> " + str(end_time)
	events = calCon.getEvents(start_time, end_time)
	
	for hour in range(0, 24):
		#calendar_color = getCalendarColor(calendar['colorId'])
		#calendar_name = calendar['summary']
		cal = createButton(left_space+left_shift, top_space+row*(row_hight+row_space), width, row_hight, str(hour)+":00 - "+str(hour+1)+":00")
		ret.append([cal, Data(CONTROL_TYPE_TASK_SLOT, datetime.datetime(selected.year, selected.month, selected.day, hour, 0))])
		
		row = row + 1
	
	x=0
	for event in events:
		s_hour = formatDateTime_get_hour(event, 'start')
		s_min = formatDateTime_get_minute(event, 'start')
		e_hour = formatDateTime_get_hour(event, 'end')
		e_min = formatDateTime_get_minute(event, 'end')
		
		if formatDate(event, 'start') < selected:
			hight_start = top_space
		else:
			hight_start = int(s_hour) * (row_hight+row_space) + int(row_hight*(float(s_min) / 60)) + top_space
		
		if formatDate(event, 'end') > selected:
			hh = 24*(row_hight+row_space)
		else:
			hh =       int(e_hour) * (row_hight+row_space) + int(row_hight*(float(e_min) / 60)) + top_space - hight_start
			
		if hh == 0:
			hh = 24*(row_hight+row_space)
		event_color = COLOR_LABEL_REGULAR
		if event.get("colorId") != None:
			event_color = calCon.getCalendarColor(event.get("colorId"))
		event_summary = event['summary'] if 'summary' in event else ''
		cal = createButton(left_space+100+x, hight_start, (width-100)/len(events), hh, str(s_hour)+":"+str(s_min)+" - "+str(int(e_hour))+":"+str(int(e_min))+" "+event_summary)
		
		ret.append([cal, Data(CONTROL_TYPE_EVENT, event)])
		x = x + (width-100)/len(events)
	return ret
	
def buildCalendarList(left_space, top_space, width, hight, calCon, window):
	ret=[]
	
	number_of_calendars = len(calCon.calendars)
	row_space = 8
	row_hight = (hight-((number_of_calendars-1)*row_space))/number_of_calendars
	
	column_with = width 
	
	row = 0
	for calendar in calCon.calendars:
		calendar_color = calCon.getCalendarColor(calendar['colorId'])
		calendar_name = calendar['summary']
		cal = xbmcgui.ControlRadioButton(left_space, top_space+row*(row_hight+row_space), column_with, row_hight, calendar_name, focusOnTexture=btn_on, noFocusOnTexture=btn_on, focusOffTexture=btn_off, noFocusOffTexture=btn_off, textColor=calendar_color, font='font10')
		d = Data(CONTROL_TYPE_CALENDAR, "")
		d.batchAdd = False
		ret.append([cal, d])
		window.addControl(cal)
		
		calCon.calendar_control_to_calendar_name[cal.getId()] = calendar_name
		cal.setSelected(calCon.is_selected(calendar_name))
		row = row + 1
	return ret

def buildViewSelection(left_space, top_space, width, hight, calCon, window):
	ret=[]

	number_of_views = len(views)
	row_space = 8
	row_hight = (hight-((number_of_views-1)*row_space))/number_of_views
	column_space = 10
	column_with = (width-2*column_space) / 3
	
	row = 0
	#for k, v in views.items():
	ctrl = createButton(left_space, top_space+row*(row_hight+row_space), column_with, row_hight, 'Day')
	ret.append([ctrl, Data(CONTROL_TYPE_VIEW, VIEW_TYPE_DAY)])
	
	ctrl = createButton(left_space+column_space+column_with, top_space+row*(row_hight+row_space), column_with, row_hight, 'Week')
	ret.append([ctrl, Data(CONTROL_TYPE_VIEW, VIEW_TYPE_WEEK)])

	ctrl = createButton(left_space+2*column_space+2*column_with, top_space+row*(row_hight+row_space), column_with, row_hight, 'Month')
	ret.append([ctrl, Data(CONTROL_TYPE_VIEW, VIEW_TYPE_MONTH)])
#		d.batchAdd = False
#		ret.append([ctrl_view, d])
#		window.addControl(ctrl_view)
			
#		row = row + 1
	
	return ret
	
def buildEventList(left_space, top_space, width, hight, window, events_list):
	ret=[]
	# Add day events control
	lst_events = xbmcgui.ControlList(left_space, top_space, width, hight, selectedColor='0xFF00F030', buttonTexture=task_a, buttonFocusTexture=task_b, font='font10')
	d = Data("list", "")
	d.batchAdd = False
	ret.append([lst_events, d])
	window.addControl(lst_events)
	fillEventsList(events_list, lst_events)
	return ret

		
def fillEventsList(events, list):
	list.reset()
	if not events:
		list.addItem('No Events')
		
	for event in events:
		list.addItem(formatDateTime(event, 'start')+"-"+formatDateTime(event, 'end')+" "+event['summary'])

def buildSmallNavigation(left, top, width, hight, selected_date):
	ret=[]
	lbl_width = 45
	column_space = 1
	
	btn_width = (width - 2*lbl_width - 15*column_space)/4
	row_hight = hight
	
	# Add navigation controls
	btn_c = xbmcgui.ControlButton(left, top, btn_width, row_hight, "", focusTexture=pic_m_back, noFocusTexture=pic_m_back, alignment=ALIGN_CENTER, font='font10')
	ret.append([btn_c, Data(CONTROL_TYPE_MONTH_NAVIGATION, CONTROL_VALUE_NAVIGATE_PREVIOS)])
	
	btn_d = createLabel(left + btn_width+ column_space, top, lbl_width, row_hight, "Month")
	ret.append([btn_d, Data("nothing", "")])
	
	btn_e = xbmcgui.ControlButton(left + btn_width+ 2*column_space + lbl_width, top, btn_width, row_hight, "", focusTexture=pic_m_forward, noFocusTexture=pic_m_forward, alignment=ALIGN_CENTER, font='font10')
	ret.append([btn_e, Data(CONTROL_TYPE_MONTH_NAVIGATION, CONTROL_VALUE_NAVIGATE_NEXT)])
	
	btn_f = xbmcgui.ControlButton(left + 2*btn_width+ 13*column_space + lbl_width, top, btn_width, row_hight, "", focusTexture=pic_y_back, noFocusTexture=pic_y_back, alignment=ALIGN_CENTER, font='font10')
	ret.append([btn_f, Data(CONTROL_TYPE_YEAR_NAVIGATION, CONTROL_VALUE_NAVIGATE_PREVIOS)])
	
	btn_g = createLabel(left + 3*btn_width+ 14*column_space + lbl_width, top, lbl_width, row_hight, "Year")
	ret.append([btn_g, Data("nothing", "")])
	
	btn_h = xbmcgui.ControlButton(left + 3*btn_width+ 15*column_space + 2*lbl_width, top, btn_width, row_hight, "", focusTexture=pic_y_forward, noFocusTexture=pic_y_forward, alignment=ALIGN_CENTER, font='font10')
	ret.append([btn_h, Data(CONTROL_TYPE_YEAR_NAVIGATION, CONTROL_VALUE_NAVIGATE_NEXT)])
	
	return ret

def buildNavigation(left_space, top_space, width, hight, selected_date):
	ret=[]
	row_space = 10
	row_hight = (hight-2*row_space)/3
	
	column_space = 10
	
	
	btn_a = createLabel(left_space, top_space, (width-column_space)/3, row_hight, "Today: ")
	ret.append([btn_a, Data("nothing","")])
	
	btn_b = createButton(left_space + column_space + (width-column_space)/3, top_space, (width-column_space)/3*2, row_hight, str(datetime.date.today()))
	ret.append([btn_b, Data(CONTROL_TYPE_TODAY_NAVIGATION, datetime.date.today())])

	# Add navigation controls
	secound_line_hight = top_space+row_space+row_hight
	ret.extend(buildSmallNavigation(left_space, secound_line_hight, width, row_hight,selected_date))
	
	thierd_line_hight = top_space+2*(row_space+row_hight)
	btn_i = createLabel(left_space, thierd_line_hight, (width-column_space)/3, row_hight, "Go To: ")
	ret.append([btn_i, Data("nothing", "")])

	btn_j = createButton(left_space + column_space + (width-column_space)/3, thierd_line_hight, (width-column_space)/3*2, row_hight, str(datetime.date.today()))
	ret.append([btn_j, Data(CONTROL_TYPE_GOTO, "")])
	
	return ret

def getControlsFromData(controlsDataList):
	tmp_ctrl = []
	for ctrl in controlsDataList:
		tmp_ctrl.append(ctrl[0])
	return tmp_ctrl
	
def removeAllControls(window, control_to_data):

	tmp_ctrl = []
	for k,v in control_to_data.items():
		tmp_ctrl.append([window.getControl(k), v])
	
	removeControls(window, tmp_ctrl, control_to_data)
		
	
def removeControls(window, controls, control_to_data):
	# Add all controls to screen 
	tmp_ctrl = []
	for ctrl in controls:
		if ctrl[1].batchAdd:
			tmp_ctrl.append(ctrl[0])
			
	# Get controls (for cleanup and events)
	for ctrl in controls:
		control_to_data.pop(ctrl[0].getId(), 0)

	# Remove all controls to screen 	
	window.removeControls(tmp_ctrl)
	

def addControls(window, controls, control_to_data):
	# Add all controls to screen 
	tmp_ctrl = []
	for ctrl in controls:
		if ctrl[1].batchAdd:
			tmp_ctrl.append(ctrl[0])
	
	window.addControls(tmp_ctrl)
	
	lastControl = None
	# Save controls (for cleanup and events)
	for ctrl in controls:
		control_to_data[ctrl[0].getId()] = ctrl[1] 
		#if lastControl != None:
#			ctrl[0].controlLeft(lastControl)
#			lastControl.controlRight(ctrl[0])
	
		lastControl = ctrl[0]
		
	
def formatDate(event, a):
	x = event[a].get('dateTime', event[a].get('date'))
	return date(int(dateutil.parser.parse(x).strftime('%Y')), int(dateutil.parser.parse(x).strftime('%m')), int(dateutil.parser.parse(x).strftime('%d') ))

def formatDateTime(event, a):
	x = event[a].get('dateTime', event[a].get('date'))
	return dateutil.parser.parse(x)	

def formatDateTime_get_hour(event, a):
	x = event[a].get('dateTime', event[a].get('date'))
	return dateutil.parser.parse(x).strftime('%H')

def formatDateTime_get_minute(event, a):
	x = event[a].get('dateTime', event[a].get('date'))
	return dateutil.parser.parse(x).strftime('%M')

def formatDateTime_get_iso(dt):
	if type(dt) is datetime.datetime:
		# Example: 2003-08-05T21:36:11.590000
		return datetime.datetime(dt.year, dt.month,  dt.day, dt.hour, dt.minute).isoformat() 
	if type(dt) is date:
		return datetime.datetime(dt.year, dt.month,  dt.day, 0, 0).isoformat()
		
def message(msg):
	dialog = xbmcgui.Dialog()
	dialog.ok("Event", msg)


	