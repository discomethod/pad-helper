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
	# holds the orb paint selection buttons
	orbSelectors = {}
	
	###---HELPER FUNCTIONS---###
	def linearIndex(self,row, column):
		return row*constants.gridColumns+column;

	def goLeft(self,index):
		result = index-1
		# try going left from this index
		if index%constants.gridColumns==0:
			# index is in the left-most column
			return -1
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
	
	def paintOrbGrid(self,row,column):
		# load in the default png file
		pngFile = Image.open(constants.orbImageURL[self.selectedOrb])
		# convert to a TK PhotoImage
		img = ImageTk.PhotoImage(pngFile)
		# paints the orb grid element at row, column
		self.orbGrid[self.linearIndex(row,column)].config(image=img)
		# remember the orb value of this orb
		self.orbGrid[self.linearIndex(row,column)].orb = self.selectedOrb
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
			if constants.DEBUG: print "checking for a horizontal group starting at index " + str(index)
			currentColor = boardstate[index].orb
			currentStreak = 1
			nextIndex = index
			while self.goRight(nextIndex)!=-1:
				# there is an orb to the right of this element
				nextIndex = self.goRight(nextIndex)
				if constants.DEBUG: print "checking streak at index " + str(nextIndex)
				if currentColor != boardstate[nextIndex].orb:
					# next orb is a different color, break
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
		# traverse the orb grid searching for vertical combos
		currentGroup = 0 # reset currentGroup
		for index in range(0,constants.gridRows*constants.gridColumns):
			if verticalGroup[index]!=-1:
				# this element has already been checked, don't process
				continue
			if constants.DEBUG: print "checking for a vertical group starting at index " + str(index)
			currentColor = boardstate[index].orb
			currentStreak = 1
			nextIndex = index
			while self.goDown(nextIndex)!=-1:
				# there is an orb below this element
				nextIndex = self.goDown(nextIndex)
				if constants.DEBUG: print "checking streak at index " + str(nextIndex)
				if currentColor != boardstate[nextIndex].orb:
					# next orb is a different color, break
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
				if constants.DEBUG: print "orb " + str(index) + " has already been processed"
				continue;
			if horizontalGroup[index]==-1 and verticalGroup[index]==-1:
				# this orb is not in any group
				if constants.DEBUG: print "orb " + str(index) + " is not in a horizontal or vertical group"
				continue;
			# this orb is the start of an overall group
			if constants.DEBUG: print "queue initialized with element " + str(index)
			# record this group's color
			overallGroupColor.append(boardstate[index].orb)
			# initialize the count at 0
			overallGroupCount.append(0)
			# put first element into queue
			overallGroupQueue.append(index)
			while(len(overallGroupQueue)>0):
				# pop the element
				currentIndex = overallGroupQueue.popleft()
				if constants.DEBUG: print "popped from the queue element " + str(currentIndex) + ", and there are " + str(len(overallGroupQueue)) + " elements remaining"
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
				nextIndex = self.goLeft(currentIndex)
				if nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup] and (horizontalGroup[nextIndex]!=-1 or verticalGroup[nextIndex]!=-1):
					overallGroupQueue.append(nextIndex)
				nextIndex = self.goUp(currentIndex)
				if nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup] and (horizontalGroup[nextIndex]!=-1 or verticalGroup[nextIndex]!=-1):
					overallGroupQueue.append(nextIndex)
				nextIndex = self.goRight(currentIndex)
				if nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup] and (horizontalGroup[nextIndex]!=-1 or verticalGroup[nextIndex]!=-1):
					overallGroupQueue.append(nextIndex)
				nextIndex = self.goDown(currentIndex)
				if nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup] and (horizontalGroup[nextIndex]!=-1 or verticalGroup[nextIndex]!=-1):
					overallGroupQueue.append(nextIndex)
				# check if it's in a horizontal group
				if horizontalGroup[index]!=-1:
					# orb is in horizontal group, so search both to the left and right
					# search to the right
					nextIndex = self.goRight(currentIndex)
					while(nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup]):
						overallGroupQueue.append(nextIndex)
						nextIndex=self.goRight(nextIndex)
					# search to the left
					nextIndex = self.goLeft(currentIndex)
					while(nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup]):
						overallGroupQueue.append(nextIndex)
						nextIndex=self.goLeft(nextIndex)
				# check if it's in a vertical group
				if verticalGroup[index]!=-1:
					# orb is in vertical group, so search both to the top and bottom
					# search to the top
					nextIndex = self.goUp(currentIndex)
					while(nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup]):
						overallGroupQueue.append(nextIndex)
						nextIndex=self.goUp(nextIndex)
					# search to the bottom
					nextIndex = self.goDown(currentIndex)
					while(nextIndex!=-1 and overallGroup[nextIndex]==-1 and overallGroupQueue.count(nextIndex)==0 and boardstate[nextIndex].orb==overallGroupColor[currentGroup]):
						overallGroupQueue.append(nextIndex)
						nextIndex=self.goDown(nextIndex)
			currentGroup += 1
		totalOverallGroups = currentGroup
		print "there are " + str(totalOverallGroups) + " overall groups"
		
		
	def createWidgets(self):
		# create the orb grid
		for row in range(0,constants.gridRows):
			for column in range(0,constants.gridColumns):
				# load in the default png file
				pngFile = Image.open(constants.orbImageURL[constants.orbDefault])
				# convert to a TK PhotoImage
				img = ImageTk.PhotoImage(pngFile)
				# create a button with that image
				self.orbGrid.append(tk.Button(self,image=img,relief=constants.tkButtonInactive,command = lambda row=row,column=column: self.paintOrbGrid(row,column)))
				# remember the orb value of this orb
				self.orbGrid[self.linearIndex(row,column)].orb = constants.orbDefault
				# store a reference to the image
				self.orbGrid[self.linearIndex(row,column)].img = img
				# send the button to be displayed in the grid
				self.orbGrid[self.linearIndex(row,column)].grid(column=column,row=row)
		
		# create a row of orb image choosers
		# preface with an instructory line
		self.orbSelectorLabel = tk.Label(self,text="Choose an orb to paint:")
		self.orbSelectorLabel.grid(columnspan=constants.gridColumns)
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
			self.orbSelectors[orb].grid(row=(constants.gridRows+2),column=index)
			# advance the index
			index += 1
		# make the default orb color selected
		self.orbSelectors[self.selectedOrb].config(relief=constants.tkButtonActive)
		# create calculate combos button
		self.calculateCombosbutton = tk.Button(self, text="Calculate Combos", command=self.calculateCombos)
		# place quit button
		self.calculateCombosbutton.grid(columnspan=constants.gridColumns,sticky=tk.E+tk.W)
		# create quit button
		self.quitButton = tk.Button(self, text="Close", command=self.quit)
		# place quit button
		self.quitButton.grid(columnspan=constants.gridColumns,sticky=tk.E+tk.W)
		
	
app = Application()
app.master.title("Puzzle and Dragons Helper")
app.mainloop()