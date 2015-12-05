# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter, methodcaller
import xbmcgui
import datetime
import utils
import task
import dayselection
import calendarutils
from dateutil import relativedelta

class Tasks(xbmcgui.WindowDialog):
	logo_size = 226
	stop = 1
	w=1280
	h=720
	shift_top = 10
	shift_left = 10
	calendar_width = 400
	calendar_hight = 222
	day_view_width = 630
	day_view_hight = 200

	def __init__(self):
		# Set background
		self.addControl(xbmcgui.ControlImage(0, 0, self.w, self.h, utils.background))
		self.addControl(xbmcgui.ControlImage(self.shift_left, self.shift_top, self.logo_size, self.logo_size, utils.logo))
		self.before = 3
		self.after = 3
		if utils.username == '':
			utils.message( "Setting a user name will assist you to defer between users. A user name is a free text that will help you to save your cradentials for next time")
		self.calCon = calendarutils.CalendarConnection()
	
		self.lastSelected = None
		self.view_controls = []
		self.control_to_data = {}
		self.date_center = datetime.date.today()
		self.view = utils.default_view
		print 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwww'+self.view
		
		self.load()
		
	def reload(self):
		utils.removeAllControls(self, self.control_to_data)
		self.load()
	
	def update(self):
		utils.removeControls(self, self.view_controls, self.control_to_data)
		ctrls = self.loadView()
		utils.addControls(self, ctrls, self.control_to_data)
	
	def focus_on_selected(self):
		selectedId = utils.getSelectedControl(self, self.date_center, self.control_to_data)
		self.lastSelected = self.getControl(selectedId)
		self.lastSelected.setLabel(textColor=utils.COLOR_LABEL_SELECTED)
		self.setFocus(self.lastSelected)
		
	def newDateSelected(self, new_date):
		unique_new = new_date.year*12 + new_date.month
		self.date_center = new_date
		if self.unique_month != unique_new and self.unique_month != unique_new+1 and self.unique_month != unique_new-1:
			self.reload()
		else:
			self.update()
		goto_id = utils.getTypeControl(self, self.control_to_data, utils.CONTROL_TYPE_GOTO)
		self.getControl(goto_id).setLabel(str(self.date_center))
		
		self.focus_on_selected()
		
	def loadView(self):
		
		if self.view == utils.VIEW_TYPE_MONTH:			
			self.view_controls = utils.buildMonth(self.shift_left + self.logo_size + self.calendar_width, self.shift_top, self.day_view_width, self.h-2*self.shift_top, self.date_center.year , self.date_center.month, self.date_center, self.calCon)

		elif self.view == utils.VIEW_TYPE_DAY:			
			self.view_controls = utils.buildDayView(self.shift_left + self.logo_size + self.calendar_width, self.shift_top, self.day_view_width, self.date_center, self.calCon)

		elif self.view == utils.VIEW_TYPE_WEEK:
			self.view_controls = utils.buildWeek(self.shift_left + self.logo_size + self.calendar_width, self.shift_top, self.day_view_width, self.h-2*self.shift_top, self.date_center.year , self.date_center.month, self.date_center, self.before, self.after, self.calCon)
		print 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwww11'+self.view+str(len(self.view_controls))
		return self.view_controls
		
	def load(self):
		try:
			tmp_controls = []
			progress = xbmcgui.DialogProgressBG()
			progress.create(utils.addonname, 'Loading ...')

			progress.update(20, 'Add Calendars controls')
			ctrls = utils.buildCalendarList(self.shift_left, self.h - 150 - self.shift_top, self.logo_size, 150, self.calCon, self)
			tmp_controls.extend(ctrls)

			progress.update(30, 'Add View Selection controls')
			ctrls = utils.buildViewSelection(self.shift_left, self.h - 350 - self.shift_top, self.logo_size, 60, self.calCon, self)
			tmp_controls.extend(ctrls)

			progress.update(40, 'Add Navigation controls')
			tmp_controls.extend(utils.buildNavigation(self.shift_left, self.shift_top+self.logo_size, self.logo_size, 73, self.date_center))

			progress.update(60, 'Add Calendar controls')
			year_ago = self.date_center + relativedelta.relativedelta(months=-1)
			next_year = self.date_center + relativedelta.relativedelta(months=1)
			tmp_controls.extend(utils.buildMonth(self.shift_left + self.logo_size, self.shift_top, self.calendar_width, self.calendar_hight, year_ago.year, year_ago.month, self.date_center, None))
			tmp_controls.extend(utils.buildMonth(self.shift_left + self.logo_size, self.shift_top+self.calendar_hight, self.calendar_width, self.calendar_hight, self.date_center.year, self.date_center.month, self.date_center, None))
			tmp_controls.extend(utils.buildMonth(self.shift_left + self.logo_size, self.shift_top+2*self.calendar_hight, self.calendar_width, self.calendar_hight, next_year.year, next_year.month, self.date_center, None))
			self.unique_month = self.date_center.year*12+self.date_center.month

			progress.update(60, 'Load View (Day/Month)')
			tmp_controls.extend(self.loadView())

			progress.update(80, 'Add all controls to window')
			utils.addControls(self, tmp_controls, self.control_to_data)

			self.focus_on_selected()

			progress.update(100, 'finish ....')
			progress.close()
			
			self.keyOrder()
		
		except:
			progress.close()
			print "Unexpected error:", sys.exc_info()[0]
			raise
		
	def onAction(self, action):
		if action == utils.ACTION_PREVIOUS_MENU:
			self.close()
 
	def change_selection(self, ctrl):
		if self.lastSelected != None:
			self.lastSelected.setLabel(textColor=utils.COLOR_LABEL_REGULAR)
		ctrl.setLabel(textColor=utils.COLOR_LABEL_SELECTED)
		self.lastSelected = ctrl

	def keyOrder(self):
		# TODO: Need to finish this for all controls and navigation keys....
		days = []
		slots = []
		for k, v in self.control_to_data.items():
			if v.type == utils.CONTROL_TYPE_DATE:
				days.append([v.value,self.getControl(k)])
			if v.type == utils.CONTROL_TYPE_TASK_SLOT:
				slots.append([v.value,self.getControl(k)])
				
		days = sorted(days, key=itemgetter(0))
		for i in range(0, len(days)):
			target = (i+7)%len(days)	
			next = (i+1)%len(days)	
			days[i][1].controlDown(days[target][1])
			days[target][1].controlUp(days[i][1])
			days[i][1].controlRight(days[next][1])
			days[next][1].controlLeft(days[i][1])
			
		slots = sorted(slots, key=itemgetter(0))
		for i in range(0, len(slots)):
			target = (i+1)%len(slots)	
			slots[i][1].controlDown(slots[target][1])
			slots[target][1].controlUp(slots[i][1])
			slots[i][1].controlLeft(days[0][1])
		
		if len(slots) > 1:
			days[len(days)-1][1].controlRight(slots[0][1])
			slots[0][1].controlLeft(days[len(days)-1][1])
				
	def onControl(self, control):
		# Change the selected control info
		self.change_selection(control)
		
		ctrl_data = self.control_to_data[control.getId()]
		
		if ctrl_data != None and type(ctrl_data) is utils.Data:
			# View Type selection
			if ctrl_data.type == utils.CONTROL_TYPE_VIEW:
				self.view = ctrl_data.value
				self.reload()
			
			
			# Enable/Disable calendar
			if ctrl_data.type == utils.CONTROL_TYPE_CALENDAR:
				cal_name=str(self.calCon.calendar_control_to_calendar_name[control.getId()].encode('utf-8'))
				utils.addon.setSetting(cal_name, str(control.isSelected()))
				self.reload()
				
			# Week View Before
			elif ctrl_data.type == utils.CONTROL_TYPE_BEFORE_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					if self.before > 1:
						self.before = self.before - 1
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.before = self.before + 1
				self.newDateSelected(self.date_center)
			
			# Week View After
			elif ctrl_data.type == utils.CONTROL_TYPE_AFTER_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					if self.after > 1:
						self.after = self.after - 1
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.after = self.after + 1
				self.newDateSelected(self.date_center)
				
			# Navigate Month
			elif ctrl_data.type == utils.CONTROL_TYPE_MONTH_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					self.newDateSelected(self.date_center + relativedelta.relativedelta(months=-1))
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.newDateSelected(self.date_center + relativedelta.relativedelta(months=1))				
			
			# Navigate Year
			elif ctrl_data.type == utils.CONTROL_TYPE_YEAR_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					self.newDateSelected(self.date_center + relativedelta.relativedelta(years=-1))
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.newDateSelected(self.date_center + relativedelta.relativedelta(years=1))
			
			# Navigate Today
			elif ctrl_data.type == utils.CONTROL_TYPE_TODAY_NAVIGATION:
				self.newDateSelected(ctrl_data.value)
				
			# Navigat GOTO
			elif ctrl_data.type == utils.CONTROL_TYPE_GOTO:
				dialog=dayselection.DaySelectionDialog(self.date_center)
				dialog.doModal()
				if dialog.selection_date != None:
					self.newDateSelected(dialog.selection_date)
				
				del dialog
				dialog = None
			
			# Edit existing event
			elif ctrl_data.type == utils.CONTROL_TYPE_EVENT:
				dialog=task.TaskDialog(ctrl_data.value, self.calCon, False)
				dialog.doModal()
				self.newDateSelected(utils.formatDateTime(dialog.event,'start').date())
				del dialog
				dialog = None
			
			# Add event to a given slot
			elif ctrl_data.type == utils.CONTROL_TYPE_TASK_SLOT:
				_s = str(ctrl_data.value.isoformat())
				_e = str((ctrl_data.value + relativedelta.relativedelta(hours=1)).isoformat())
				new_event = self.calCon.createNewEventBody(_s, _e)
				dialog=task.TaskDialog(new_event, self.calCon, True)
				dialog.doModal()
				self.newDateSelected(utils.formatDateTime(dialog.event,'start').date())
				del dialog
				dialog = None
			
			# Month selected - change view 
			elif ctrl_data.type == utils.CONTROL_TYPE_MONTH:
				self.view = utils.VIEW_TYPE_MONTH		
				self.newDateSelected(ctrl_data.value)
			
			# Day selected - change view 
			elif ctrl_data.type == utils.CONTROL_TYPE_DATE:
				self.view = utils.VIEW_TYPE_DAY
				self.newDateSelected(ctrl_data.value)

	
dialog=Tasks()
dialog .doModal()
del dialog
dialog = None

