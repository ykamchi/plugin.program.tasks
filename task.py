# -*- coding: utf-8 -*-

import xbmcgui
import utils
import timezoneselection
import pytz
import datetime
import dateutil.parser
import dayselection
from datetime import date
import datetime

			
class TaskDialog(xbmcgui.WindowDialog):
	logo_size = 110
	w=1280/2
	h=720/2
	t=h/2
	l=w/2
	space=10
	
	def onAction(self, action):
		if action == utils.ACTION_PREVIOUS_MENU:
			self.close()
			
	def __init__(self, task, connection, isNew):
		# Dialog return value
		self.event = task
		self.is_new = isNew
		
		self.calCon = connection
		self.control_to_data = {}
		self.lastSelected = None
		
		# Set background
		self.addControl(xbmcgui.ControlImage(self.l, self.t, self.w, self.h, utils.background))
		self.addControl(xbmcgui.ControlImage(self.l + self.space, self.t + self.space ,self.logo_size,self.logo_size, utils.logo))
		
		# Load UI
		self.load()
		
	def load(self):
		tmp_controls = []
		
		# Build the task controls
		tmp_controls.extend(utils.buildTaskView(self.l + self.logo_size + self.space*2, self.t + self.space, self.w - self.logo_size - self.space*2, self.h - 2*self.space, self.event))
		
		# Build Ok/Cancel controls
		tmp_controls.extend(utils.buildOkCancelButtons(self.l+(self.w-300)/2, self.t + self.h - self.space - 30, 300, 30))

		# Build Delete controls
		tmp_controls.extend(utils.buildDeleteButton(self.l+self.w-30 , self.t + self.h - self.space - 30, 30, 30))

		# Add all controls to screen 		
		utils.addControls(self, tmp_controls, self.control_to_data)
	
	def change_selection(self, ctrl): #TODO: move to parent calss
		if self.lastSelected != None:
			self.lastSelected.setLabel(textColor=utils.COLOR_LABEL_REGULAR)
		ctrl.setLabel(textColor=utils.COLOR_LABEL_SELECTED)
		self.lastSelected = ctrl
	

	def onControl(self, control):
		# Change the selected control info
		self.change_selection(control)
		
		value = self.control_to_data[control.getId()]
		
		ctrl_data = self.control_to_data[control.getId()]
		if ctrl_data != None and type(ctrl_data) is utils.Data:
			if ctrl_data.type == utils.CONTROL_TYPE_EVENT_SUMMARY:
				self.event['summary'] = utils.getKeyboardResults(control.getLabel(), 'Task Summary')
				control.setLabel(self.event['summary'])
				
			if ctrl_data.type == utils.CONTROL_TYPE_EVENT_DESCRIPTION:
				self.event['description'] = utils.getKeyboardResults(control.getLabel(), 'Task Description')
				control.setLabel(self.event['description'])
				
			if ctrl_data.type == utils.CONTROL_TYPE_TIMEZONE:
				dialog = timezoneselection.TimezoneDialog(utils.addon.getSetting('timezone'))
				dialog.doModal()
				if dialog.selected != None:
					self.event['start']['timeZone'] = dialog.selected
					self.event['end']['timeZone'] = dialog.selected
					control.setLabel(dialog.selected)
				
			if  ctrl_data.type == utils.CONTROL_TYPE_EVENT_LOCATION:
				self.event['location'] = utils.getKeyboardResults(control.getLabel(), 'Task Location')
				control.setLabel(self.event['location'])
				
			if value.type =='start_day':
				dialog = dayselection.DaySelectionDialog(utils.formatDateTime(self.event, 'start'))
				dialog.doModal()
		
				control.setLabel(str(dialog.selection_date))
				self.event['start']['dateTime']= utils.formatDateTime_get_iso(dialog.selection_date)
				
			if value.type =='end_day':
				dialog = dayselection.DaySelectionDialog(utils.formatDateTime(self.event, 'end'))
				dialog.doModal()
				
				control.setLabel(str(dialog.selection_date))
				self.event['end']['dateTime']= utils.formatDateTime_get_iso(dialog.selection_date)
			
			if ctrl_data.type == utils.CONTROL_TYPE_ACTION:
				if ctrl_data.value == utils.CONTROL_VALUE_ACTION_DELETE:
					self.calCon.deleteEvent(self.event)
					self.close()
					
				if ctrl_data.value == utils.CONTROL_VALUE_ACTION_OK:
					print str(self.event)
					if 'timeZone' in self.event['start'] and self.event['start']['timeZone'] in pytz.all_timezones and self.event['end']['timeZone'] in pytz.all_timezones:
						if self.is_new:
							self.calCon.createEvent(self.event)
						else:
							self.calCon.updateEvent(self.event)
						
						self.close()
					
					else:
						utils.message("You must select time zone from the list of timezones")
					
				if ctrl_data.value == utils.CONTROL_VALUE_ACTION_CANCEL:
					self.close()
					
			if value.type == "action" and value.value == "cancel":
				self.close()
