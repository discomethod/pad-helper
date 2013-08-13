DEBUG = 0

# cardinal diretions
directions = ("left","up","right","down")

# logic
maxExamined = 75000 # maximum number of tries when solving
maxMoves = 19 # maximum number of moves
cullFrequency = 75000 # number of tries per cull update
cullCutoff = 1.2 # fraction of average to cull

# grid size
gridRows = 5
gridColumns = 6

# text strings
textCalculateCurrentCombos = "Calculate Damage"
textClose = "Close"
textDamageDisplayAmount = "Total: "
textChoosePaint = "Choose a color to paint:"
textSolve = "Solve"
textTitle = "Puzzle and Dragons Helper"

# orbs
orbDefault = "light"
orbDefaultConfig = ("heal","light","wood","wood","fire","light","dark","heal","wood","water","heal","dark","fire","light","light","fire","fire","wood","heal","wood","dark","wood","water","light","light","dark","heal","heal","fire","dark")
orbDefaultStrength = 100
orbList = ("heal","fire","water","wood","light","dark")
# orb image URLs
orbImageURL = dict(light="img/light.png",
					dark="img/dark.png",
					fire="img/fire.png",
					water="img/water.png",
					wood="img/wood.png",
					heal="img/heal.png",
					bg="img/bgOrb.png"
					);

# TKinter styles
tkButtonInactive = "flat"
tkButtonActive = "groove"
tkButtonBorder = 3
tkOrbStrengthEntryWidth = 7