import xbmcgui
import utils
from datetime import date
import datetime
from dateutil import relativedelta
		
class DaySelectionDialog(xbmcgui.WindowDialog):
	# Dialog Location and Size
	w=1280/2
	h=720/2
	t=h/2
	l=w/2
	
	# Controls Location and Size
	logo_size = 170
	space=10
	left = l + logo_size + space*2 #for controls section
	top = t + space #for controls section
	width = w - logo_size - space*2
	hight = 230
			
	def __init__(self, selected):
		# Dialog return value
		self.selection_date = selected

		self.control_to_data = {}
		self.month_view_controls = []
		self.lastSelected = None
		
		# Set background
		self.addControl(xbmcgui.ControlImage(self.l, self.t, self.w, self.h, utils.background))
		self.addControl(xbmcgui.ControlImage(self.l + self.space, self.t + self.space ,self.logo_size,self.logo_size, utils.logo))
		
		# Load UI
		self.load()
	def getSelectedDate(self):
		x =self.selection_date
		if type(x) is datetime.datetime:
			x = x.date()
		return x
			
		
	def focus_on_selected(self):
		selectedId = utils.getSelectedControl(self, self.getSelectedDate(), self.control_to_data)
		self.change_selection( self.getControl(selectedId))
	
	def change_selection(self, ctrl):
		if self.lastSelected != None:
			self.lastSelected.setLabel(textColor=utils.COLOR_LABEL_REGULAR)
		ctrl.setLabel(textColor=utils.COLOR_LABEL_SELECTED)
		self.lastSelected = ctrl
	
	def update(self):
		# Clean UI controls to be replaced
		utils.removeControls(self, self.month_view_controls, self.control_to_data)
		
		# Build the month view controls and save it for removal/update
		self.month_view_controls = utils.buildMonth(self.left, self.top, self.width, self.hight, self.selection_date.year, self.selection_date.month, self.getSelectedDate(), None)

		# Build the time selection controls
		if type(self.selection_date) is date:
			_h = 0
			_m = 0
		else:
			_h = self.selection_date.hour
			_m = self.selection_date.minute
		
			self.month_view_controls.extend(utils.buildTime(self.left + self.width - self.width/2 - self.space, self.top + self.hight + self.space, self.width/2, 30, _h, _m))

			
		
	
		# Add all controls to screen
		utils.addControls(self, self.month_view_controls, self.control_to_data)
		
		# Set the focus on the selected control
		self.focus_on_selected()
		
	def load(self):
		tmp_controls = []
					
		# Build the navigation controls
		tmp_controls.extend(utils.buildNavigation(self.l + self.space, self.t + self.logo_size + self.space, self.logo_size, 60, self.selection_date))
		
		# Build Ok/Cancel controls
		tmp_controls.extend(utils.buildOkCancelButtons(self.l+(self.w-300)/2, self.t + self.h - self.space - 30, 300, 30))
		
		# Add all controls to screen 		
		utils.addControls(self, tmp_controls, self.control_to_data)
			
		# Build the controls that refreshed by update
		self.update()
	
	def onAction(self, action):
		if action == utils.ACTION_PREVIOUS_MENU:
			self.selection_date = None
			self.close()
			
	def onControl(self, control):
		# Change the selected control info
		self.change_selection(control)
		
		ctrl_data = self.control_to_data[control.getId()]
		if ctrl_data != None and type(ctrl_data) is utils.Data:
			if ctrl_data.type == utils.CONTROL_TYPE_DATE:
				print 'x. ....'+str(self.selection_date)
				if type(self.selection_date) is datetime.datetime:
					print '0. ....'+str(self.selection_date)
					self.selection_date=self.selection_date.replace(year=ctrl_data.value.year , month=ctrl_data.value.month, day=ctrl_data.value.day,hour=self.selection_date.hour,minute=self.selection_date.minute,tzinfo=self.selection_date.tzinfo)
					print '1. ....'+str(self.selection_date)
					self.update()
				
				elif type(self.selection_date) is datetime.date:
					print '2. ....'+str(self.selection_date)
					self.selection_date = ctrl_data.value
					print '3. ....'+str(self.selection_date)
					
				else:
				
					print 'y. ....'+str(type(self.selection_date))
			
			elif ctrl_data.type == utils.CONTROL_TYPE_HOUR_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.selection_date = self.selection_date + relativedelta.relativedelta(hours=1)		
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					self.selection_date = self.selection_date + relativedelta.relativedelta(hours=-1)
				
				self.update()	
				
			elif ctrl_data.type == utils.CONTROL_TYPE_MINUTE_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.selection_date = self.selection_date + relativedelta.relativedelta(minutes=1)
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					self.selection_date = self.selection_date + relativedelta.relativedelta(minutes=-1)				

				self.update()	
				
			elif ctrl_data.type == utils.CONTROL_TYPE_MONTH_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.selection_date = self.selection_date + relativedelta.relativedelta(months=1)
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					self.selection_date = self.selection_date + relativedelta.relativedelta(months=-1)
				
				self.update()

			elif ctrl_data.type == utils.CONTROL_TYPE_YEAR_NAVIGATION:
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_NEXT:
					self.selection_date = self.selection_date + relativedelta.relativedelta(years=1)
				if ctrl_data.value == utils.CONTROL_VALUE_NAVIGATE_PREVIOS:
					self.selection_date = self.selection_date + relativedelta.relativedelta(years=-1)
				
				self.update()
								
			if ctrl_data.type == utils.CONTROL_TYPE_ACTION:
				if ctrl_data.value == utils.CONTROL_VALUE_ACTION_OK:
					print '3. selected: '+str(self.selection_date)
					self.close()
					
				elif ctrl_data.value == utils.CONTROL_VALUE_ACTION_CANCEL:
					self.selection_date = None
					self.close()
		