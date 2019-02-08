#!/usr/bin/env python 
from __future__ import generators
from __future__ import print_function


import argparse
import copy
import json
import re

from collections import OrderedDict

kBaseType		= 'BaseType'
kClassType		= 'Class'

kRarity			= 'Rarity'
kQuality		= 'Quality'
kItemLevel		= 'ItemLevel'
kDropLevel		= 'DropLevel'

kSockets		= 'Sockets'
kLinkedSockets	= 'LinkedSockets'
kSocketGroup	= 'SocketGroup'

kHeight			= 'Height'
kWidth			= 'Width'

kExplicitMod	= 'HasExplicitMod'
kStackSize		= 'StackSize'

kGemLevel		= 'GemLevel'

kIdentified		= 'Identified'
kCorrupted		= 'Corrupted'
kElderItem		= 'ElderItem'
kShaperItem		= 'ShaperItem'
kShapedMap		= 'ShapedMap'

kMapTier		= 'MapTier'



kPropertyIgnore = [
#	kBaseType,	# Automatically Selected Based of there is only a single base type
#	kClassType,	# Automatically Selected Based of there is only a single class type
	kQuality, 
	kItemLevel, 
	kDropLevel, 
	kSockets, 
	kLinkedSockets, 
	kSocketGroup, 
	kHeight, 
	kWidth, 
	kExplicitMod,
	kStackSize,
	kGemLevel,
	kIdentified,
	kCorrupted,
	kElderItem,
	kShaperItem,
	kShapedMap,
	kMapTier,
	
	'action'
]



kActionBorderColour		= 'SetBorderColor'
kActionTextColour		= 'SetTextColor'
kActionBackgroundColour	= 'SetBackgroundColor'
kActionFontSize			= 'SetFontSize'
kActionAlertSound		= 'AertSound'
kActionMiniMapIcon		= 'MiniMapIcon'
kActionPlayEffect		= 'PlayEffect'

kPropertySize			= 'Size'
kPropertyShape			= 'Shape'
kPropertyColour			= 'Colour'
kPropertyTemporary		= 'Temp'


kRarityNormal	= 'Normal'
kRarityMagic	= 'Magic'
kRarityRare		= 'Rare'
kRarityUnique	= 'Unique'


kOPNone			= 0x00
kOPEqual		= 0x01
kOPGreater		= 0x02
kOPLesser		= 0x04
# None =, Equal = 1, Greater = 2, Lesser = 4, GreaterEqual = 2 + 1 = 3, LesserEqual = 4 + 1 = 5
kOPGreaterEqual	= kOPEqual | kOPGreater
kOPLesserEqual	= kOPEqual | kOPLesser
kOperators 		= [kOPNone, kOPEqual, kOPGreater, kOPGreaterEqual, kOPLesser, kOPLesserEqual]
kOperatorsStr	= ["", "=", ">", ">=", "<", "<="]

kSizeLarge		= 0
kSizeMedium		= 1
kSizeSmall		= 2

kShapeCircle 	= 'Circle'
kShapeDiamond 	= 'Diamond'
kShapeHexagon 	= 'Hexagon'
kShapeSquare 	= 'Square'
kShapeStar		= 'Star'
kShapeTriangle 	= 'Triangle'
kShapes = [kShapeCircle, kShapeDiamond, kShapeHexagon, kShapeSquare, kShapeStar, kShapeTriangle]

kColourRed		= 'Red'
kColourGreen	= 'Green'
kColourBlue		= 'Blue'
kColourBrown	= 'Brown'
kColourWhite	= 'White'
kColourYellow	= 'Yellow'
kColours = [kColourRed, kColourGreen, kColourBlue, kColourBrown, kColourWhite, kColourYellow]

# Globals
printer = None


# Output
class Printer(object):
	def __call__(self, s):
		raise NotImplementedError()
	
class PrinterNone(object):
	def __call__(self, s):
		pass
	
class PrinterTerminal(Printer):
	def __call__(self, s):
		print(s)

class PrinterFile(Printer):
	# TODO: Implement arg for -o to output directly to file
	pass


# Utility Functions
def clamp(value, minValue, maxValue):
	return max(minValue, min(maxValue, value))

def rgba(r=0, g=0, b=0, a=255):
	# May not need this anymore
	r = clamp(red, 0, 255)
	g = clamp(green, 0, 255)
	b = clamp(blue, 0, 255)
	a = clamp(alpha, 0, 255)
	return "%s %s %s %s" % (r, g, b, a)

def toList(value):
	if not type(value) is list:
		return [value]
	return value
		
		


# Display
def DisplayNOOP(o):
	# Display as-is
	return o

def DisplayString(o):
	 # Force quotations around the output
	return '"%s"' % o


# Value
class Value(object):
	def __init__(self, value=None):
		self._value = value
	
	def setValue(self, value=None):
		self._value = value
	
	def getValue(self):
		return self._value
		
	def toString(self, displayCB=DisplayNOOP):
		return displayCB(self.getValue())


class ValueOperator(Value):
	def __init__(self, value=None, operator=kOPEqual):
		
		if type(operator) is str:
			operator = kOperatorsStr.index(operator)
		if operator not in kOperators:
			raise ValueError("Invalid Operator: %s" % operator)
		self._operator = operator
		super().__init__(value)
		
	def getOperator(self):
		return self._operator
		
	def getOperation(self):
		global kOperatorsStr
		return kOperatorsStr[self._operator]

	def toString(self, displayCB=DisplayNOOP):
		s = '%s %s' % (self.getOperation(), displayCB(self.getValue()))
		return s




# Validation
class Validate(object):

	def __call__(self, item):
		return True

class ValidateRange(Validate):
	def __init__(self, min=0, max=100):
		if max <= min:
			raise ValueError()
		self._min = min
		self._max = max
		
	def __call__(self, item):
		print(type(item))
		if not type(item) is int:
			raise ValueError()
		return item >= min and item <= max

class ValidateList(Validate):
	def __init__(self, options):
		self._options = options
		
	def __call__(self, item):
		return item in self._options
			
class ValidateBoolean(Validate):
	
	def __call__(self, item):
		return type(item) is bool


# Visual Style		
class Colour(object):

	def __init__(self, r=0, g=0, b=0, a=255):
		self._red = clamp(r, 0, 255)
		self._green = clamp(g, 0, 255)
		self._blue = clamp(b, 0, 255)
		self._alpha = clamp(a, 0, 255)
	
	def __str__(self):
		return "%s %s %s %s" % (self._red, self._green, self._blue, self._alpha)


	
class MiniMapIcon(object):
	def __init__(self, size=kSizeMedium, colour=kColourWhite, shape=kShapeCircle):
		self._size = size
		self._colour = colour
		self._shape = shape
		
	def getSize(self):
		return self._size
		
	def getColour(self):
		return self._colour
		
	def getShape(self):
		return self._shape
		
	def __str__(self):
		return "%s %s %s" % (self._size, self._colour, self._shape)


class PlayEffect(object):
	def __init__(self, colour=kColourWhite, temp=False):
		self._colour = colour
		self._temporary = temp
	
	def getColour(self):	
		return self._colour
	
	def isTemporary(self):
		return self._temporary
		
	def __str__(self):
		if self.isTemporary():
			return "%s %s" % (self._colour, "Temp")
		else:
			return "%s" % (self._colour)
		

class Sound(object):
	def __init__(self):
		# TODO:
		# ID:			Int			(PlayAlertSound, PlayAlertSoundPositional)
		# Volume:		Int			(PlayAlertSound, PlayAlertSoundPositional)
		# Positional: 	Boolean		(PlayAlertSoundPositional)
		# Disable:		Boolean		(DisableDropSound)
		# Filename: 	String		(CustomAlertSound)
		
		# Disabled is Set			: Use DisableDropSound
		# Filename is not None		: Use CustomAlertSound
		# Positional == True 		: Use PlayAlertSoundPositional Else Use PlayAlertSound
		pass
		
	def getAction(self):
		pass


class Action(object):
	def __init__(self):
		self._textColor = None
		self._backgroundColor = None
		self._borderColor = None
		
		self._fontSize = None
		
		self._miniMapIcon = None
		self._playEffect = None
		
		self._alertSound = None
		
	def setBorderColour(self, colour=None):
		if colour and not isinstance(colour, Colour):
			return False
		self._borderColor = copy.deepcopy(colour)
		return True
	
	def setBackgroundColour(self, colour=None):
		if colour and not isinstance(colour, Colour):
			return False
		self._backgroundColor = copy.deepcopy(colour)
		return True
		
	def setTextColour(self, colour=None):
		if colour and not isinstance(colour, Colour):
			return False
		self._textColor = copy.deepcopy(colour)	
		return True
	
	def setFontSize(self, fontSize=32):
		self._fontSize = fontSize
		return True
	
	def setMiniMapIcon(self, size=kSizeMedium, colour=kColourWhite, shape=kShapeCircle, icon=None):
		# TODO: Investigate MultipleDispatch
		if icon:
			if isinstance(icon, MiniMapIcon):
				self._miniMapIcon = MiniMapIcon(icon.getSize(), icon.getColour(), icon.getShape())
			else:
				return False
		else:
			self._miniMapIcon = MiniMapIcon(size, colour, shape)
		return True
		
	def setPlayEffect(self, colour=kColourWhite, temp=False, effect=None):
		# TODO: Investigate MultipleDispatch
		if effect:
			if isinstance(effect, PlayEffect):
				self._playEffect = PlayEffect(colour=effect.getColour(), temp=effect.isTemporary())
			else:
				return False
		else:
			self._playEffect = PlayEffect(colour=colour, temp=temp)
		return True
		
	def setAlertSound(self, id, volume=None, positional=False):
		# TODO: Use above sound class
		s = OrderedDict({'id': id})
		if volume:
			s['volume'] = volume
		s['positional'] = positional
		
		self._alertSound = s
		return True
	
	def setCustomAlertSound(self, filename):
		# TODO: Use above sound class
		self._alertSound = OrderedDict({'filename': filename})
		return True
	
	def getBorderColour(self):
		return self._borderColor
		
	def getBackgroundColour(self):
		return self._backgroundColor
		
	def getTextColour(self):
		return self._textColor
		
	def getFontSize(self):
		return self._fontSize
		
	def getMiniMapIcon(self):
		return self._miniMapIcon
		
	def getPlayEffect(self):
		return self._playEffect
		
	def getAlertSound(self):
		return self._alertSound
	




# FilterCondition Base
class Condition(object):

	def __init__(self, condition, validationCB=None, displayCB=DisplayNOOP):
		if not condition:
			raise ValueError()	
	
		self._condition = condition
		self._validationCB = validationCB
		self._displayCB = displayCB
	
	def __call__(self, printer):
		raise NotImplementedError()

	def _validate(self, item):
		if not self._validationCB:
			return True
		return self._validationCB(item)


# Condition contains multiple options
class ConditionArray(Condition):

	def __init__(self, condition, validationCB=None, displayCB=DisplayNOOP):
		self._items = None
		super().__init__(condition, validationCB, displayCB)
	
	def addItem(self, item):
		if not item and this._validate(item):
			return False
		if self._items is None:
			self._items = []
		self._items.append(item)
		return True
		
	def getLength(self):
		return 0 if self._items is None else len(self._items)
	
	def getItems(self):
		if not self._items:
			return
		for i in self._items:
			yield i
			

# Condition is listed multiple times in the filter [AND conditions]
class ConditionList(ConditionArray):
	def __init__(self, condition, validationCB=None, displayCB=DisplayNOOP):
		super().__init__(condition, validationCB, displayCB)	
	
	def __call__(self, printer):
		if not self._items:
			return
		for item in self._items:
	 		printer('\t%s %s' % (self._condition, item.toString(self._displayCB)))
			
	

# Condition is combined into a single item in the Filter [OR conditions]
class ConditionSelect(ConditionArray):
	def __init__(self, condition, validationCB=None, displayCB=DisplayNOOP):
		super().__init__(condition, validationCB, displayCB)
			
	def __call__(self, printer):
		
		if self._items:
			s = "\t%s" % self._condition			
			for item in self._items:
				s = '%s %s' % (s, self._displayCB(item))
			printer(s)



# Condition contains only a single value
class ConditionValue(Condition, Value):
	def __init__(self, condition, validationCB=None, displayCB=DisplayNOOP):
		Condition.__init__(self, condition, validationCB, displayCB)
		Value.__init__(self)

	def setValue(self, value=None):
		if not self._validate(value):
			return False
		Value.setValue(self, value)
		return True
		
	def __call__(self, printer):
		if not self.getValue():
			return
		s = '\t%s %s' % (self._condition, self._displayCB(self.getValue()))
		printer(s)


# FilterAction
class FilterAction(Action):

	def __init__(self):
		Action.__init__(self)
		
	def _applyAction(self, actionID, actionDB):
		
		# Actions are applied in order of first to last. Property is set in a first-come first served basis
		action = actionDB.getAction(actionID)
		if not action:
			#print('Unable to apply action: %s' % actionID)
			return False
		
		
		self.setBorderColour(action.getBorderColour())
		self.setTextColour(action.getTextColour())
		self.setBackgroundColour(action.getBackgroundColour())
		
		if action.getMiniMapIcon():
			self.setMiniMapIcon(icon=action.getMiniMapIcon())
			
		if action.getPlayEffect():
			self.setPlayEffect(effect=action.getPlayEffect())
	
	def setBorderColour(self, colour=None):
		if self.getBorderColour():
			return False
		return Action.setBorderColour(self, colour)
	
	def setBackgroundColour(self, colour=None):
		if self.getBackgroundColour():
			return False
		return Action.setBackgroundColour(self, colour)
		
	def setTextColour(self, colour=None):
		if self.getTextColour():
			return False
		return Action.setTextColour(self, colour)
	
	def setFontSize(self, fontSize=32):
		pass
	
	def setMiniMapIcon(self, size=kSizeMedium, colour=kColourWhite, shape=kShapeCircle, icon=None):
		if self.getMiniMapIcon():
			return False
		return Action.setMiniMapIcon(self, size=size, colour=colour, shape=shape, icon=icon)
				
	def setPlayEffect(self, colour=None, temp=False, effect=None):
		if self.getPlayEffect():
			return False
		return Action.setPlayEffect(self, colour=colour, temp=temp, effect=effect)
		
	def setAlertSound(self, id, volume=None, positional=False):
		pass
	
	def setCustomAlertSound(self, filename):
		pass
	
	def __call__(self, printer):
		if self.getBorderColour():
			printer('\t%s %s' % (kActionBorderColour, self.getBorderColour()))
		if self.getTextColour():
			printer('\t%s %s' % (kActionTextColour, self.getTextColour()))
		if self.getBackgroundColour():
			printer('\t%s %s' % (kActionBackgroundColour, self.getBackgroundColour()))
		if self.getFontSize():
			printer('\t%s %s' % (kActionFontSize, self.getFontSize()))
		if self.getMiniMapIcon():
			printer('\t%s %s' % (kActionMiniMapIcon, self.getMiniMapIcon()))
		if self.getPlayEffect():
			printer('\t%s %s' % (kActionPlayEffect, self.getPlayEffect()))
		if self.getAlertSound():
			printer('\t%s %s' % (self._alertSound.getAction(), self.getAlertSound()))
		
	
		
		
# Filter Conditions
class FilterConditions(object):
	
	def __init__(self):
		self._classType = ConditionSelect(kClassType, displayCB=DisplayString)
		self._baseType = ConditionSelect(kBaseType, displayCB=DisplayString)

		self._itemLevel = ConditionList(kItemLevel, validationCB=ValidateRange(1, 100))
		self._dropLevel = ConditionList(kDropLevel, validationCB=ValidateRange(1, 100))
		self._quality = ConditionList(kQuality, validationCB=ValidateRange(0, 20))
		self._rarity = ConditionList(kRarity, validationCB=ValidateList(kRarity), displayCB=DisplayString)
	
		self._sockets = ConditionList(kSockets, validationCB=ValidateRange(0, 6))
		self._linkedSockets = ConditionList(kLinkedSockets, validationCB=ValidateRange(0, 6))
		self._socketGroup = ConditionValue(kSocketGroup, validationCB=ValidateList("RGBW"), displayCB=DisplayString)
		
		self._height = ConditionList(kHeight, validationCB=ValidateRange(1, 4))
		self._width = ConditionList(kWidth, validationCB=ValidateRange(1, 2))
		
		self._explicitMod = ConditionSelect(kExplicitMod, displayCB=DisplayString)
		
		self._stackSize = ConditionList(kStackSize, validationCB=ValidateRange(1, 0xFFFF))
		self._gemLevel = ConditionList(kGemLevel, validationCB=ValidateRange(1, 21))
		self._mapTier = ConditionList(kMapTier, validationCB=ValidateRange(1, 17))
		
		self._identified = ConditionValue(kIdentified, validationCB=ValidateBoolean())
		self._corrupted = ConditionValue(kCorrupted, validationCB=ValidateBoolean())
		self._elderItem = ConditionValue(kElderItem, validationCB=ValidateBoolean())
		self._shaperItem = ConditionValue(kShaperItem, validationCB=ValidateBoolean())
		self._shapedMap = ConditionValue(kShapedMap, validationCB=ValidateBoolean())
		
	def addBaseType(self, baseType=None):
		return self._baseType.addItem(baseType)
	
	def addClassType(self, classType=None):
		return self._classType.addItem(classType)
	
	
	def addItemLevel(self, itemLevel, operator=kOPEqual):
		return self._itemLevel.addItem(ValueOperator(itemLevel, operator))
	
	def addDropLevel(self, dropLevel, operator=kOPEqual):
		return self._dropLevel.addItem(ValueOperator(dropLevel, operator))
		
	def addQuality(self, quality, operator=kOPEqual):
		return self._quality.addItem(ValueOperator(quality, operator))
		
	def addRarity(self, rarity, operator=kOPEqual):
		return self._rarity.addItem(ValueOperator(rarity, operator))
		

	def addSockets(self, sockets, operator=kOPEqual):
		return self._sockets.addItem(ValueOperator(sockets, operator))
	def addLinkedSockets(self, sockets, operator=kOPEqual):
		return self._linkedSockets.addItem(ValueOperator(sockets, operator))
	def setSocketGroup(self, socketGroup):
		return self._socketGroup.setValue(socketGroup)
		
	def addStackSize(self, stackSize, operator=kOPEqual):
		return self._stackSize.addItem(ValueOperator(stackSize, operator))
	def addGemLevel(self, gemLevel, operator=kOPEqual):
		return self._gemLevel.addItem(ValueOperator(gemLevel, operator))

	def addMapTier(self, mapTier, operator=kOPEqual):
		return self._mapTier.addItem(ValueOperator(mapTier, operator))
				
	def setSizeDimensions(self, width=0, height=0):
		# There may neeed to be more options for dealing with this
		if width:
			self._width.addItem(ValueOperator(width))
		if height:
			self._height.addItem(ValueOperator(height))
		
	def setIdentified(self, value):
		return self._identified.setValue(value)
	
	def setCorrupted(self, value):
		return self._corrupted.setValue(value)
		
	def setElderItem(self, value):
		return self._elderItem.setValue(value)
	
	def setShaperItem(self, value):
		return self._shaperItem.setValue(value)

	def setShapedMap(self, value):
		return self._shapedMap.setValue(value)		
		
		
		
	def visibility(self):
		return self._show
	
	def isIdentified(self):
		return None
	
	def isCorrupted(self):
		return None
		
	def isElderItem(self):
		return None

	def isShaperItem(self):
		return None	
	
	def isShapedMap(self):
		return None
		
	def __call__(self, printer):
		self._classType(printer)
		self._baseType(printer)
		
		self._itemLevel(printer)
		self._dropLevel(printer)
		self._quality(printer)
		self._rarity(printer)
	
		self._sockets(printer)
		self._linkedSockets(printer)
		self._socketGroup(printer)
		
		self._width(printer)
		self._height(printer)
		
		self._explicitMod(printer)
		
		self._stackSize(printer)
		self._gemLevel(printer)
		self._mapTier(printer)
		
		self._identified(printer)
		self._corrupted(printer)
		self._elderItem(printer)
		self._shaperItem(printer)
		self._shapedMap(printer)

# Filter to output
class FilterListing(FilterConditions, FilterAction):
	
	def __init__(self, data=None, actionDB=None):

		FilterConditions.__init__(self)
		FilterAction.__init__(self)
		
		self._show = True
		self._comment = None	# Dumps a comment after the Show/Hide line
		
		self._actions = ConditionSelect("actions")
		self._properties = {}
	
		if data:
			# TODO: Could be cleaner :)
			if 'Hide' in data:
				self.hide()
			if 'Show' in data:
				self.show()
				
			# Extract data from JSON object to build the filter conditions
			self._addItem(kClassType, self._classType, data)
			self._addItem(kBaseType, self._baseType, data)
			
			self._addValueItem(kItemLevel, self._itemLevel, data)
			self._addValueItem(kDropLevel, self._dropLevel, data)
			self._addValueItem(kRarity, self._rarity, data)
			self._addValueItem(kQuality, self._quality, data)
			
			self._addValueItem(kSockets, self._sockets, data)
			self._addValueItem(kLinkedSockets, self._linkedSockets, data)
			self._setValue(kSocketGroup, self._socketGroup, data)
			
			self._addValueItem(kHeight, self._height, data)
			self._addValueItem(kWidth, self._width, data)
			
			self._addItem(kExplicitMod, self._explicitMod, data)
			
			self._addValueItem(kStackSize, self._stackSize, data)
			self._addValueItem(kGemLevel, self._gemLevel, data)
			self._addValueItem(kMapTier, self._mapTier, data)
			
			self._setValue(kIdentified, self._identified, data)
			self._setValue(kCorrupted, self._corrupted, data)
			self._setValue(kElderItem, self._elderItem, data)
			self._setValue(kShaperItem, self._shaperItem, data)
			self._setValue(kShapedMap, self._shapedMap, data)
	
			self._addItem("action", self._actions, data)
			
			# BETA: Build Property Listing
			# IMPROVE: This is really bad way of implementing this ... It shouldn't include the majority of the conditions
			for n in data:
				
				if n not in kPropertyIgnore:
					# IMPROVE: This looks horrible :)
					p = toList(data[n])
					if len(p) == 1:
						if isinstance(p, list):
							self._properties[n] = str(p[0])
						else:
							self._properties[n] = str(p)
			
			print("Properties: %s " % self._properties)
			
		for action in self._actions.getItems():
			self._applyAction(action, actionDB)
			
	
	def _addItem(self, filter, condition, data):
		if filter in data:
			f = toList(data[filter])
			for item in f:
				condition.addItem(item)
		
		
	def _addValueItem(self, filter, condition, data):
		if filter in data:				
			f = toList(data[filter])
			
			pattern = '^(?P<OPERATOR>(%s)?)( ?)(?P<VALUE>[0-9a-zA-Z]+)' % (')|('.join(kOperatorsStr))
			p = re.compile(pattern)

			for item in f:
				result = p.search(str(item))
				if not result:
					print('Error evaluating operation %s ' % str(item))
					continue
				operator = kOPEqual if not result.group('OPERATOR') else result.group('OPERATOR')
				result = condition.addItem(ValueOperator(value=result.group('VALUE'), operator=operator))
				if not result:
					print('Error adding condition: %s' % condition)
						
	def _setValue(self, filter, condition, data):			
		if filter in data:
			condition.setValue(data[filter])
		

	def _applyAction(self, actionName, actionDB):
		
		# The Action MAY have dynamic information
		actionID = actionName
		
		pattern = re.compile('\{(?P<PROPERTY>[\w\-]+)\}')
		
		while True:
			result = pattern.search(actionID)
			if not result:
				break
			property = result.group('PROPERTY')
			actionID = actionID.replace('{%s}' % property, self._getProperty(property))
				
		FilterAction._applyAction(self, actionID, actionDB)
		
	def _getProperty(self, property):
		
		if property not in self._properties:
			return ""
					
		return self._properties[property]
		

	def show(self):
		self._show = True
		
	def hide(self):
		self._show = False

	# TODO: Action Overridables		
		
	def __call__(self, printer):
		s = 'Show' if self._show else 'Hide'
		if self._comment:
			s = '%s # %s' % (s, self._comment)
		
		printer(s)
		FilterConditions.__call__(self, printer)
		FilterAction.__call__(self, printer)
		printer("")
		
		



#############################
# Database loaded from file #
#############################

def LoadJSON(filename):
	data = None
	
	try:
		with open(filename, "r") as f:
			data = json.load(f, object_pairs_hook=OrderedDict)
			
	except IOError as e:
		print("%s" % e)
	
	except Exception as e:
		print("%s" % e)
	
	return data


			
		

class ActionDB(object):
	
	def __init__(self, colourData, actionData):
		
		self._actions = {}
		self._colours = {}
		
		# Load the Colour Constants
		for colourName in colourData:
			colour = colourData[colourName]
						
			c = self._buildColour(colour)
			if c:
				self._colours[colourName] = c
		
		# Load Actions
		for actionName in actionData:
			action = actionData[actionName]

			a = Action()

			a.setBorderColour(self._loadColour(kActionBorderColour, action))
			a.setTextColour(self._loadColour(kActionTextColour, action))
			a.setBackgroundColour(self._loadColour(kActionBackgroundColour, action))

			icon = self._loadMiniMapIcon(kActionMiniMapIcon, action)
			if icon:
				a.setMiniMapIcon(icon=icon)
			effect = self._loadPlayEffect(kActionPlayEffect, action)
			if effect:
				a.setPlayEffect(effect=effect)
 
 
			self._actions[actionName] = a
			

	def _loadColour(self, property, data):
		
		if not property in data:
			 return False
		
		p = data[property]
		
		if isinstance(p, str):
			# Special Case: Load from ColourDB
			
			result = re.search('^\{(?P<COLOURID>[\w\-]+)\}$', p)
			if result:
				colourId = result.group('COLOURID')		
				return self._getColour(colourId)

		return self._buildColour(data)
		
	
	def _loadMiniMapIcon(self, property, data):
		if not property in data:
			return None
		p = data[property]
		if isinstance(p, dict):
			size = kSizeMedium if kPropertySize not in p else p[kPropertySize]
			colour = kColourWhite if kPropertyColour not in p else p[kPropertyColour]
			shape = kShapeCircle if kPropertyShape not in p else p[kPropertyShape]
			return MiniMapIcon(size=size, colour=colour, shape=shape)
		
		return None
		
	def _loadPlayEffect(self, property, data):
		if not property in data:
			return None
		p  = data[property]
		if isinstance(p, dict):
			colour = kColourWhite if kPropertyColour not in p else p[kPropertyColour]
			temp = False if kPropertyTemporary not in p else bool(p[kPropertyColour])
			return PlayEffect(colour=colour, temp=temp)
		elif isinstance(p, str):
			colour = p
			return PlayEffect(colour=colour)
			
		return None
		
	def _buildColour(self, colourData):
		if isinstance(colourData, dict):
			r = 0 if 'r' not in colourData else colourData['r']
			g = 0 if 'g' not in colourData else colourData['g']
			b = 0 if 'b' not in colourData else colourData['b']
			a = 255 if 'a' not in colourData else colourData['a']
			c = Colour(r, g, b, a)
			return c
		elif type(colourData) is str:
			# TODO: Support for String formats. IE #RRGGBBAA or #AARRGGBB
			# Awkward cos it's usually represented by ARGB, but may need to be RGBA for consistency with POE Filters
			return None

		return None



	def _getColour(self, colourName):
		if colourName not in self._colours:
			return None
		return self._colours[colourName]	
		

	def getAction(self, action):
		if action not in self._actions:
			return None
		
		return self._actions[action]


def FilterBuilder(filterData):
	
	if not data:
		return None
		
	filters = None


	for nodeName in filterData:
		node = toList(filterData[nodeName])
	
		# TODO: There may be additional copy.deepcopy(...) that isn't needed anymore
		if filters:
			# Reconstruct the Array with extras on the end
			filterLen = len(filters)
			cpy = copy.deepcopy(filters)
			filters = copy.deepcopy(cpy * len(node))
		else:
			filterLen = 1
			filters = []
			for i in node:
				filters.append(OrderedDict())
				
		idx = 0
		for item in node:
			for i in range(filterLen):
				f = copy.deepcopy(filters[idx])
				
				# HACK: Only one expansion group available for now
				# TODO: Look at what is present in the child node ... if it's a dict, it's likely to be all thats needed to determine whether
				# to copy the whole thing or construct a new property
				if isinstance(item, dict):
				#if nodeName == 'subdata':
					f.update(copy.deepcopy(item))
				else:
					f.update({nodeName: copy.deepcopy(item)})				
					
				filters[idx] = copy.deepcopy(f)
				idx = idx + 1
	
	
	return filters
			
	
	
	
	
def  Parse(data):
	global printer
	global args
	
	colourData = None if not 'colour' in data else data['colour']
	actionData = None if not 'action' in data else data['action']
	
	actionDB = ActionDB(colourData, actionData)
	
	filterList = []

	if 'filter' in data:
		filterDict = data['filter']
		
		# Load Each Filter
		for f in filterDict:
			print('Filter: %s' % f)
			
			filters = FilterBuilder(filterDict[f])
			
			for f in filters:
			
				filter = FilterListing(f, actionDB);

				filter(printer)

				if args.debugOutput:
					print('%s' % json.dumps(f, indent=4))

	
	
# Application
def addArgs(argParser=None):
	if not argParser:
		argParser = argparse.ArgumentParser();
		
	argParser.add_argument('-o', dest='disableOutput', action='store_true', help='Disables the Output')
	argParser.add_argument('-d', dest='debugOutput', action='store_true', help='Enables Debug Output')
		
	argParser.add_argument("filter")
	
	return argParser
	
	
if __name__ == "__main__":
	

	argParser = addArgs()
	args = argParser.parse_args()
	
	
	# Create Output Object
	if args.disableOutput:
		printer = PrinterNone()
	else:
		printer = PrinterTerminal()

	# Load Filter Builder File
	data = LoadJSON(args.filter)
	if not data:
		raise ValueError("Unable to load file")

	Parse(data)
	
	
	
	
	