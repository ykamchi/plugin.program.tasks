# -*- coding: utf-8 -*-

import xbmcgui
import utils
import pytz
			
class TimezoneDialog(xbmcgui.WindowDialog):
	logo_size = 110
	w=1280/2
	h=720/2
	t=h/2
	l=w/2
	space=10
	
	def onAction(self, action):
		if action == utils.ACTION_PREVIOUS_MENU:
			self.close()
			
	def __init__(self, selected):
		# Dialog return value
		self.selected = selected
		self.last_selected = None
		self.control_to_data = {}
		
		# Set background
		self.addControl(xbmcgui.ControlImage(self.l, self.t, self.w, self.h, utils.background))
		self.addControl(xbmcgui.ControlImage(self.l + self.space, self.t + self.space ,self.logo_size,self.logo_size, utils.logo))
		
		# Load UI
		self.load()
		
	def load(self):
		tmp_controls = []
		
	
		# Build the timezone list control
		tmp_controls.extend(utils.builTimezoneView(self.l + self.logo_size + self.space*2, self.t + self.space, self.w - self.logo_size - self.space*2, self.h - 30 - 2*self.space,''))
		
		# Build Ok/Cancel controls
		tmp_controls.extend(utils.buildOkCancelButtons(self.l+(self.w-300)/2, self.t + self.h - self.space - 30, 300, 30))

		# Add all controls to screen 		
		utils.addControls(self, tmp_controls, self.control_to_data)
		
		ctrl = self.getControl(utils.getTypeControl(self, self.control_to_data, utils.CONTROL_TYPE_TIMEZONE_LIST))
		items = []
		for tz in pytz.all_timezones:
			itm = xbmcgui.ListItem(label=tz)
			items.append(itm)

		ctrl.addItems(items)

	def onControl(self, control):
		ctrl_data = self.control_to_data[control.getId()]
		if ctrl_data != None and type(ctrl_data) is utils.Data:
			if ctrl_data.type == utils.CONTROL_TYPE_TIMEZONE_LIST:
				if self.last_selected != None:
					self.last_selected.select(False)
				control.getSelectedItem().select(True)
				self.last_selected = control.getSelectedItem()
				print self.last_selected
				
			if ctrl_data.type == utils.CONTROL_TYPE_ACTION:
				if ctrl_data.value == utils.CONTROL_VALUE_ACTION_OK:
					ctrl = self.getControl(utils.getTypeControl(self, self.control_to_data, utils.CONTROL_TYPE_TIMEZONE_LIST))
					if self.last_selected != None:
						self.selected = self.last_selected.getLabel()
						utils.addon.setSetting('timezone', self.selected)
					else:
						self.selected = None
						
					self.close()
					
				if ctrl_data.value == utils.CONTROL_VALUE_ACTION_CANCEL:
					self.selected = None
					self.close()
