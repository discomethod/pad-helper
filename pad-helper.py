##! D:/Coding/GitHub/pad-helper python

# import Tkinter
import Tkinter as tk
# import PIL to handle PNGs, etc.
from PIL import Image, ImageTk
# import constants
import constants
# import queues
from collections import deque

class Application(tk.Frame):
	
	# keep track of which orb is currently being painted
	selectedOrb = constants.orbDefault
	# holds the orb grid buttons
	orbGrid = []
	# holds the orb grid solution
	orbGridSolutionFields = []
	# holds the orb grid solution
	orbGridSolution = {}
	# holds the orb paint selection buttons
	orbSelectors = {}
	# holds the ATK value input fields of each element
	orbStrengthFields = {}
	# holds the ATK value of each element
	orbStrength = {}
	# holds the calculated damage fields
	orbDamageFields = {}
	# holds the calculated damage value of each element
	orbDamage = {}
	
	###---HELPER FUNCTIONS---###
	def linearIndex(self,row, column):
		return row*constants.gridColumns+column;

	def goLeft(self,index):
		# try going left from this index
		if index%constants.gridColumns==0:
			# index is in the left-most column
			return -1
		result = index-1
		return result

	def goUp(self,index):
		result = index-constants.gridColumns
		# try going up from this index
		if result<0:
			# index is in the top-most row
			return -1
		return result

	def goRight(self,index):
		result = index+1
		# try going right from this index
		if result%constants.gridColumns==0:
			#index is in the right-most column
			return -1
		return result

	def goDown(self,index):
		# try going down from this index
		result = index+constants.gridColumns
		if result>=(constants.gridRows * constants.gridColumns):
			# index is in the bottom-most row
			return -1
		return result

	def goDispatcher(self,direction,index):
		# trying going in a direction
		if direction==0:
			return self.goLeft(index)
		if direction==1:
			return self.goUp(index)
		if direction==2:
			return self.goRight(index)
		return self.goDown(index)
	###---HELPER FUNCTIONS---###

	def __init__(self, master=None):
		tk.Frame.__init__(self,master)
		self.grid()
		self.createWidgets()

	def setSelectedOrb(self,color):
		# remove the effect from the current selectedOrb
		self.orbSelectors[self.selectedOrb].config(relief=constants.tkButtonInactive)
		# change the selectedOrb to color
		self.selectedOrb = color
		# add effect to the new selectedOrb
		self.orbSelectors[self.selectedOrb].config(relief=constants.tkButtonActive)

	def paintOrbGrid(self,row,column,color=""):
		if len(color)==0:
			color = self.selectedOrb
		# load in the default png file
		pngFile = Image.open(constants.orbImageURL[color])
		# convert to a TK PhotoImage
		img = ImageTk.PhotoImage(pngFile)
		# paints the orb grid element at row, column
		self.orbGrid[self.linearIndex(row,column)].config(image=img)
		# remember the orb value of this orb
		self.orbGrid[self.linearIndex(row,column)].orb = color
		# store a reference to the image
		self.orbGrid[self.linearIndex(row,column)].img = img

	def calculateCombos(self,boardstate=""):
		# calculates combos present based on the provided boardstate
		# will use current boardstate if applicable
		if len(boardstate)==0:
			boardstate = self.orbGrid
		# initialize the arrays
		horizontalGroup = []
		verticalGroup = []
		overallGroup = []
		for index in range(0,constants.gridRows*constants.gridColumns):
			horizontalGroup.append(-1)
			verticalGroup.append(-1)
			overallGroup.append(-1)
		# traverse the orb grid searching for horizontal combos
		currentGroup = 0 # reset currentGroup
		for index in range(0,constants.gridRows*constants.gridColumns):
			if horizontalGroup[index]!=-1:
				# this element has already been checked, don't process
				continue
			if constants.DEBUG>10: print "checking for a horizontal group starting at index " + str(index)
			currentColor = boardstate[index].orb
			currentStreak = 1
			nextIndex = index
			while self.goRight(nextIndex)!=-1:
				# there is an orb to the right of this element
				nextIndex = self.goRight(nextIndex)
				if constants.DEBUG>10: print "checking streak at index " + str(nextIndex)
				if currentColor != boardstate[nextIndex].orb:
					# last valid orb was the previous orb
					nextIndex = self.goLeft(nextIndex)
					# next orb is a different color, break
					if constants.DEBUG>10: print "streak ends at index " + str(nextIndex)
					break
				# next orb is the same color
				# increment counter and continue
				currentStreak += 1
			if currentStreak>=3:
				# was a combo
				# set all visited orb to be in this group
				for ii in range(0,currentStreak):
					horizontalGroup[nextIndex] = currentGroup
					nextIndex = self.goLeft(nextIndex)
				currentGroup += 1
		totalHorizontalGroups = currentGroup
		if constants.DEBUG: print "there are " + str(totalHorizontalGroups) + " horizontal groups"
		if constants.DEBUG>10:
			for row in range(0,constants.gridRows):
				for column in range(0,constants.gridColumns):
					print str(horizontalGroup[self.linearIndex(row,column)]),
				print "\n"
				
		# traverse the orb grid searching for vertical combos
		currentGroup = 0 # reset currentGroup
		for index in range(0,constants.gridRows*constants.gridColumns):
			if verticalGroup[index]!=-1:
				# this element has already been checked, don't process
				continue
			if constants.DEBUG>10: print "checking for a vertical group starting at index " + str(index)
			currentColor = boardstate[index].orb
			currentStreak = 1
			nextIndex = index
			while self.goDown(nextIndex)!=-1:
				# there is an orb below this element
				nextIndex = self.goDown(nextIndex)
				if constants.DEBUG>10: print "checking streak at index " + str(nextIndex)
				if currentColor != boardstate[nextIndex].orb:
					# last valid orb was the previous orb
					nextIndex = self.goUp(nextIndex)
					# next orb is a different color, break
					if constants.DEBUG>10: print "streak ends at index " + str(nextIndex)
					break
				# next orb is the same color
				# increment counter and continue
				currentStreak += 1
			if currentStreak>=3:
				# was a combo
				# set all visited orb to be in this group
				for ii in range(0,currentStreak):
					verticalGroup[nextIndex] = currentGroup
					nextIndex = self.goUp(nextIndex)
				currentGroup += 1
		totalVerticalGroups = currentGroup
		if constants.DEBUG: print "there are " + str(totalVerticalGroups) + " vertical groups"
		# combine overall combos
		currentGroup = 0 # reset currentGroup
		overallGroupQueue = deque() # initialize queue
		overallGroupColor = [] # overallGroupColor[groupNumber] = color of this combo
		overallGroupCount = [] # overallGroupCount[groupNumber] = number of orbs in this combo
		for index in range(0,constants.gridRows * constants.gridColumns):
			if overallGroup[index]!=-1:
				# this orb has already been processed
				if constants.DEBUG>10: print "orb " + str(index) + " has already been processed"
				continue;
			if horizontalGroup[index]==-1 and verticalGroup[index]==-1:
				# this orb is not in any group
				if constants.DEBUG>10: print "orb " + str(index) + " is not in a horizontal or vertical group"
				continue;
			# this orb is the start of an overall group
			if constants.DEBUG>20: print "queue initialized with element " + str(index)
			# record this group's color
			overallGroupColor.append(boardstate[index].orb)
			# initialize the count at 0
			overallGroupCount.append(0)
			# put first element into queue
			overallGroupQueue.append(index)
			while(len(overallGroupQueue)>0):
				# pop the element
				currentIndex = overallGroupQueue.popleft()
				if constants.DEBUG>20: print "popped from the queue element " + str(currentIndex) + ", and there are " + str(len(overallGroupQueue)) + " elements remaining"
				# mark it as in the current overall group
				overallGroup[currentIndex] = currentGroup
				# increment the group count
				overallGroupCount[currentGroup] += 1
				"""
				check the four directions around this orb
					nextIndex !=1 														check that the nextIndex is a valid location in the grid
					overallGroup[nextIndex]==-1 										don't queue the element if it's already in a group
					overallGroupQueue.count(nextIndex)==0 								don't queue the element if it's already in the queue
					boardstate[nextIndex].orb==overallGroupColor[currentGroup] 			only queue if the nextIndex is the right color
					(horizontalGroup[nextIndex]!=-1 or verticalGroup[nextIndex]!=-1) 	the next element must be in a horizontal or vertical group
				"""
				for direction in range(0,4):
					nextIndex=self.goDispatcher(direction,currentIndex)
					if nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup] and (horizontalGroup[nextIndex]!=-1 or verticalGroup[nextIndex]!=-1):
						overallGroupQueue.append(nextIndex)
			currentGroup += 1
		totalOverallGroups = currentGroup
		if constants.DEBUG>2:
			print "there are " + str(totalOverallGroups) + " overall groups"
			for row in range(0,constants.gridRows):
				for column in range(0,constants.gridColumns):
					print str(overallGroup[self.linearIndex(row,column)]),
				print ""
		# combos are found, calculate total throughput
		damage = {}
		totalDamage=0
		# initialize damage dictionary
		for orb in constants.orbList:
			damage[orb] = 0
		# go through the combos
		for index in range(0,totalOverallGroups):
			if constants.DEBUG: print "there is a " + overallGroupColor[index] + " group with " + str(overallGroupCount[index]) + " orbs in it"
			# calculate damage for this combo
			thisDamage = int(self.orbStrength[overallGroupColor[index]].get()) * (0.25 + overallGroupCount[index] * 0.25) * (1 + (totalOverallGroups - 1) * 0.25 )
			# add thisDamage to color damage
			damage[overallGroupColor[index]] += thisDamage
			# add thisDamage to total damage
			totalDamage += thisDamage
		if constants.DEBUG>10: 
			for orb in constants.orbList:
				print "total " + str(damage[orb]) + " " + orb + " damage"
			print "total " + str(totalDamage) + " damage"
		damage["total"] = totalDamage
		return damage

	def calculateCurrentCombos(self):
		# helper function to call calculateCombos() based on the current boardstate
		damage = self.calculateCombos()
		# extract damage totals from the returned data
		totalDamage = damage["total"]
		# update displays
		self.damageDisplayAmount.set(constants.textDamageDisplayAmount + str(totalDamage))
		for orb in constants.orbList:
			if damage[orb]==0.0:
				self.orbDamage[orb].set("0.0")
			else:
				self.orbDamage[orb].set(str(damage[orb]))

	def solve(self):
		# solve the current boardstate
		# initialize queue
		solveQueue = deque()
		examined = 0
		bestDamage = 0
		bestHistory = ()
		bestState = list(self.orbGrid)
		bestStartedFrom = 0
		cullTotal = 0
		cullCount = 0
		cullAmount = 0
		for index in range(0,constants.gridRows * constants.gridColumns):
			# start from this position
			solveQueue.append(dict(startedFrom=index,toMove=index,lastMove=-1,state=list(self.orbGrid),history=()))
		while(len(solveQueue)>0 and examined<constants.maxExamined):
			thisQueueElement = solveQueue.popleft()
			if constants.DEBUG: print "popped queue element with toMove: " + str(thisQueueElement['toMove']) + ", lastMove: " + str(thisQueueElement['lastMove'])
			if constants.DEBUG:
				print "history: "
				for index in range(0,len(thisQueueElement['history'])):
					print thisQueueElement['history'][index],
			if constants.DEBUG:
				print "state: "
				for row in range(0,constants.gridRows):
					for column in range(0,constants.gridColumns):
						print str(thisQueueElement['state'][self.linearIndex(row,column)].orb),
					print ""
			for direction in range(0,4):
				if constants.DEBUG>2: print "attempting to move " + str(thisQueueElement['toMove']) + " in the " + constants.directions[direction] + " direction"
				"""
				0	left
				1	up
				2	right
				3	down
				"""
				if (direction+2)%4==thisQueueElement['lastMove'] and thisQueueElement['lastMove']!=-1:
					if constants.DEBUG>2: print "cannot undo the previous move"
					continue;
				if self.goDispatcher(direction,thisQueueElement['toMove']) == -1:
					if constants.DEBUG>2: print "cannot move in that direction"
					continue;
				# the orb to move can move in this direction
				# copy the history
				newHistory = list(thisQueueElement['history'])
				# add this move
				newHistory.append(direction)
				# copy the state
				newState = list(thisQueueElement['state'])
				# find new index
				newIndex = self.goDispatcher(direction,thisQueueElement['toMove'])
				# swap old and new index
				newState[newIndex] = thisQueueElement['state'][thisQueueElement['toMove']]
				newState[thisQueueElement['toMove']] = thisQueueElement['state'][newIndex]
				# calculate damage of this configuration
				newDamage = self.calculateCombos(newState)
				# see if this is better than the previous record
				if newDamage["total"] > bestDamage:
					# record this
					if constants.DEBUG: print "found a new best damage!"
					bestDamage = newDamage["total"]
					bestHistory = list(newHistory)
					bestState = list(newState)
					bestStartedFrom = thisQueueElement['startedFrom']
				# manage culling
				cullTotal += newDamage["total"]
				cullCount += 1
				if cullCount > constants.cullFrequency:
					# update cull
					cullTemp = (cullTotal / cullCount) * constants.cullCutoff
					if cullTemp > cullAmount:
						cullAmount = cullTemp
					cullCount = 0
					cullTotal = 0
				# increment examined
				examined += 1
				# insert new queue element only if above culling thresh and below move thresh
				if newDamage["total"] >= cullAmount and len(newHistory)<constants.maxMoves:
					solveQueue.append(dict(startedFrom=thisQueueElement['startedFrom'],toMove=newIndex,lastMove=direction,state=newState,history=newHistory))
		if constants.DEBUG:
			print "best damage is " + str(bestDamage)
			print "best history is ",
			for index in range(0,len(bestHistory)):
				print constants.directions[bestHistory[index]],
			print " starting from " + str(bestStartedFrom)
			for row in range(0,constants.gridRows):
				for column in range(0,constants.gridColumns):
					try:
						print bestState[self.linearIndex(row,column)].orb,
					except IndexError:
						print "no best state found"
						break;
				print ""
		# print out the solutions in the secondary grid
		# clear out previous records
		for index in range(0,constants.gridRows * constants.gridColumns):
			self.orbGridSolution[index].set("")
		# start printing out solution
		toModify = bestStartedFrom
		self.orbGridSolution[toModify].set("1")
		for index in range(0,len(bestHistory)):
			toModify = self.goDispatcher(bestHistory[index],toModify)
			currentFieldValue = self.orbGridSolution[toModify].get()
			if(len(currentFieldValue)>0):
				currentFieldValue += ", "
			currentFieldValue += str(index+2)
			self.orbGridSolution[toModify].set(currentFieldValue)

	def createWidgets(self):
		# keep track of the next row
		nextRow = 0
		# create the orb grid
		for row in range(0,constants.gridRows):
			for column in range(0,constants.gridColumns):
				index = self.linearIndex(row,column)
				# load in the default png file
				pngFile = Image.open(constants.orbImageURL[constants.orbDefault])
				# convert to a TK PhotoImage
				img = ImageTk.PhotoImage(pngFile)
				# create a button with that image
				self.orbGrid.append(tk.Button(self,image=img,relief=constants.tkButtonInactive,command = lambda row=row,column=column: self.paintOrbGrid(row,column)))
				# remember the orb value of this orb
				self.orbGrid[index].orb = constants.orbDefault
				# store a reference to the image
				self.orbGrid[index].img = img
				# send the button to be displayed in the grid
				self.orbGrid[index].grid(column=column,row=nextRow)
				# load default config
				self.paintOrbGrid(row,column,constants.orbDefaultConfig[index])
			# increment the row
			nextRow += 1
		# create a row of orb image choosers
		# preface with an instructory line
		self.orbSelectorLabel = tk.Label(self,text=constants.textChoosePaint)
		self.orbSelectorLabel.grid(row=nextRow, columnspan=constants.gridColumns)
		# increment the row
		nextRow += 1
		# create the orb selectors
		index = 0
		for orb in constants.orbList:
			# load in the appropriate png file
			pngFile = Image.open(constants.orbImageURL[orb])
			# convert to a TK PhotoImage
			img = ImageTk.PhotoImage(pngFile)
			# create a button with that image
			self.orbSelectors[orb] = tk.Button(self,image=img,relief=constants.tkButtonInactive,bd=constants.tkButtonBorder,command = lambda color=orb: self.setSelectedOrb(color))
			# store a reference to the image
			self.orbSelectors[orb].img = img
			# send the button to be displayed in the grid
			self.orbSelectors[orb].grid(row=nextRow,column=index)
			# advance the index
			index += 1
		# increment the row
		nextRow += 1
		# make the default orb color selected
		self.orbSelectors[self.selectedOrb].config(relief=constants.tkButtonActive)
		# create atk inputs
		index = 0
		for orb in constants.orbList:
			# generate the data variable
			self.orbStrength[orb] = tk.StringVar()
			# initialize the data variable with default values
			self.orbStrength[orb].set(constants.orbDefaultStrength)
			# generate the text field
			self.orbStrengthFields[orb] = tk.Entry(self,textvariable=self.orbStrength[orb],bd=constants.tkButtonBorder,width=constants.tkOrbStrengthEntryWidth)
			# send the button to be displayed in the grid
			self.orbStrengthFields[orb].grid(row=nextRow,column=index)
			# advance the index
			index += 1
		# increment the row
		nextRow += 1
		# create damage displays
		index = 0
		for orb in constants.orbList:
			# generate the data variable
			self.orbDamage[orb] = tk.StringVar()
			# initialize the data variable with default values
			self.orbDamage[orb].set("0.0")
			# generate the text field
			self.orbDamageFields[orb] = tk.Label(self,textvariable=self.orbDamage[orb],bd=constants.tkButtonBorder,relief=constants.tkButtonInactive)
			# send the damage to be displayed in the grid
			self.orbDamageFields[orb].grid(row=nextRow,column=index)
			# advance the index
			index += 1
		# increment the row
		nextRow += 1
		# holds the damage to display
		self.damageDisplayAmount = tk.StringVar()
		self.damageDisplayAmount.set(constants.textDamageDisplayAmount + str(0.0))
		# create damage tracker
		self.damageDisplay = tk.Label(self,textvariable=self.damageDisplayAmount,relief=constants.tkButtonInactive)
		# place damage tracker
		self.damageDisplay.grid(row=nextRow,column=0,columnspan=int(constants.gridColumns/2))
		# create calculate combos button
		self.calculateCombosbutton = tk.Button(self, text=constants.textCalculateCurrentCombos, command=self.calculateCurrentCombos)
		# place combos button
		self.calculateCombosbutton.grid(row=nextRow,column=int(constants.gridColumns/2),columnspan=int(constants.gridColumns/2),sticky=tk.E+tk.W)
		# increment the row
		nextRow += 1
		# create solve button
		self.solveButton = tk.Button(self, text=constants.textSolve, command=self.solve)
		# place solve button
		self.solveButton.grid(row=nextRow,columnspan=constants.gridColumns,sticky=tk.E+tk.W)
		# increment the row
		nextRow += 1
		# create the secondary orb grid
		for row in range(0,constants.gridRows):
			for column in range(0,constants.gridColumns):
				# load in the default png file
				pngFile = Image.open(constants.orbImageURL["bg"])
				# convert to a TK PhotoImage
				img = ImageTk.PhotoImage(pngFile)
				# generate the data variable
				self.orbGridSolution[self.linearIndex(row,column)] = tk.StringVar()
				# create a label with that image and data
				self.orbGridSolutionFields.append(tk.Label(self,image=img,relief=constants.tkButtonInactive,textvariable=self.orbGridSolution[self.linearIndex(row,column)],compound=tk.CENTER,fg="#f00"))
				# store a reference to the image
				self.orbGridSolutionFields[self.linearIndex(row,column)].img = img
				# send the button to be displayed in the grid
				self.orbGridSolutionFields[self.linearIndex(row,column)].grid(column=column,row=nextRow)
			# increment the row
			nextRow += 1
		# create quit button
		self.quitButton = tk.Button(self, text=constants.textClose, command=self.quit)
		# place quit button
		self.quitButton.grid(row=nextRow,columnspan=constants.gridColumns,sticky=tk.E+tk.W)
		# increment the row
		nextRow += 1

# create instance of application
app = Application()
# set application title
app.master.title(constants.textTitle)
# calculate initial combo
app.calculateCurrentCombos()
# idle
app.mainloop()