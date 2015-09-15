from gazeTools import gazeSphere
from gazeTools import gazeVector

import viz
import vizact
import smi_beta
import vizconnect



# A demo of the gazeTools module
# Some tools for visualizing data from the SMI eye tracker integration into the oculus rift dk2

# Code by Kamran Binaee (with a bit of help from Gabriel Diaz) 
# PerForm Labs @ Rochester Institute of Technology
# Part of the multidisciplinary vision research laboratories (MVRL) 
# ...in the Chester F. Carlson Center for Imaging Science!

################## THE SETUP ########################

# This code uses vizconnect file: vizConnectSetupFile.py
#	This file is setup to configure both the oculus and a desktop mirror of what is inside the oculus
#	The desktop mirror is a second instance of vizard run using the clustering tools that come with vizard enterprise

# This configuratoin assumes that you have 2 monitors on the machine you're using, in addition to the Rift DK2
# My monitor numbers correspond to...
# 	1: oculus rift
# 	2: for the vizard IDE
# 	3: for a mirror of the in-helmet display
# Windows not on the right monitors? You can move vizard windows between displays inside the vizconnect file. Just run that file with the vizard ide.

# This configuatnoi also requires that you are using an enterprise version running the CLUSTER MASTER with 1 client running on the local machine
#	Click on "tools".  
#	In tools, click on "cluster master"
#	Check the box next to localhost, and make sure that the count is 1
#	You should probably uncheck "sync frames," if your desktop monitors can't run at 74 Hz, like your DK2 can




def onKeyDown(key):
	##########################################################
	##########################################################
	## Keys used in the default mode
	
	#  C brings up the SMI calibration screen
	
	
	global eyeTracker, calibrationDoneSMI, text_object
	if key == 'c' and eyeTracker:
		
		calibrationDoneSMI = 1.0
		print 'calibrationDoneSMI ==> ', calibrationDoneSMI
		eyeTracker.calibrate()

	if key == 'e':
		print 'My Calibration Method is Called'
		cyclopeanCalibObj.myCalibrationMethod()
		if ( cyclopeanCalibObj.calibrationInProgress == True ):
			text_object = viz.addText('')
			text_object.setParent(cyclopeanCalibObj.calibrationSphere)
			vizact.onupdate(viz.PRIORITY_INPUT+1,cyclopeanCalibObj.calculateAngularError, cyclopEyeSphere.node3D, 0.0, text_object)#self.currentTrial.ballObj.node3D

		else:
			text_object.remove()

	if key == 'q':

		cyclopeanCalibObj.updateCalibrationPoint()


# This specialized function allows you to update the mainview position using
# the position informatnoi from a mocap system
# and the orientation info from the oculus rift DK2
def updateOrientation():
	global headTracker
	riftOriTracker = vizconnect.getTracker('rift').getNode3d()			
	
	headTracker = vizconnect.getRawTracker('headtracker')
	
	ori_xyz = riftOriTracker.getEuler()
	headTracker.setEuler( ori_xyz  )
	
	# If you wanted to, you could now update the headTracker position using mocap data here
	# We hardcode it a a particular value
	headTracker.setPosition([0, 2, 0])


# Register keypresses
viz.callback(viz.KEYDOWN_EVENT, onKeyDown)

# Import vizconnect file
vizCon = vizconnect.go( 'vizConnect/' + 'vizConnectSetupFile.py' )

# Import SMI eyetracker module
simulateBool = True
if(simulateBool):
	print '***** SIMULATING GAZE DATA *******'
eyeTracker = smi_beta.iViewHMD(simulate=simulateBool)


# Import piazza environment
viz.add('piazza.osgb')

# Schedule call to update head position/orientation on each frame
vizact.onupdate(viz.PRIORITY_LAST_UPDATE,updateOrientation)

################################################################################################
################################################################################################
## Some examples of how to use the gazetools module

# Get access to the client window
dispDict = vizconnect.getRawDisplayDict()
desktopDisplay = dispDict['custom_window']

# Get acces to the head tracker, which is used to update the mainview
headTracker = vizconnect.getRawTracker('headtracker')

# Create a cyclopean gaze vector.  Rendered only to desktopDisplay
# In other words, this is not visible inside the helmet
# The "gaze sphere" is placed along the subject's gaze vector
# The viz.BOTH_EYE argument makes this a cyclopean eye vecotr
# For left eye, use viz.LEFT_EYE, and for right, viz.RIGHT_EYE
cyclopEyeSphere = gazeSphere(eyeTracker,viz.BOTH_EYE,headTracker,[desktopDisplay],viz.GREEN)
# Note that the sphere and vector are indepent
cyclopEyeSphere.toggleUpdate()

##################################################################################
##################################################################################
### Here, we create a calibration volume for the CYCLOPEAN eye
# The volume position is defined relative to head psition (in a head-centered frame of reference)
# Note that This just sets things up.  
# Calibration points will not be visible until a calibration point is turned on (below)

import vizshape

# For convenience, place a node at the locatoin of the cyclopean eye
cyclopEyeNode = vizshape.addSphere(radius=0.015, color = viz.GREEN)
cyclopEyeNode.setParent(headTracker)
cyclopEyeNode.visible(viz.OFF) # Make it invisible

# Create a calibration toolset for the cyclopean eye
from gazeTools import calibrationTools
cyclopeanCalibObj = calibrationTools(cyclopEyeNode)

# Now, setup the range/size of the calib volume
xMinMax = [-0.5, 0.5];  # in meters
yMinMax = [-0.2, 0.2];  # in meters
zMinMax = [1.0,5.0]; 
resolution = 3; # The volume is sampled linearly within the range
# So, a resolution of 3 creates 27 points (3 samples along X * 3 along Y * 3 along Z)
# These points are linearly distributed
cyclopeanCalibObj.setVolume(xMinMax, yMinMax, zMinMax, resolution)

################################################
################################################

# Get the helmet's IPD.  This is set using the 
# oculus config application
IOD = vizconnect.getRawTracker('rift').getIPD()

# For convenience, create a node3D leftEyeNode at the locatoin of the left eye
leftEyeNode = vizshape.addSphere(radius = 0.005, color = viz.BLUE)
#leftEyeNode.visible(viz.OFF)
leftEyeNode.setParent(headTracker)
# shift it to the left by half the IOD. This shift is in head-centered coordinates
leftEyeNode.setPosition(-IOD/2, 0, 0.0,viz.ABS_PARENT) 

# Create a gaze sphere at a location along the gaze vector
left_sphere = gazeSphere(eyeTracker,viz.LEFT_EYE,leftEyeNode,[desktopDisplay],sphereColor=viz.YELLOW)
# Create a gaze VECTOR, extending from the eye to the gaze sphere
leftGazeVector = gazeVector(eyeTracker,viz.LEFT_EYE,leftEyeNode,[desktopDisplay],gazeVectorColor=viz.YELLOW)
left_sphere.toggleUpdate() 
leftGazeVector.toggleUpdate()
# Note:  A small issue.  The way things are set up, if you make the eye node invisible with #leftEyeNode.visible(viz.OFF)
# you will also hide the leftGazeVector, which is a child of the leftEyeNode.  

# create a node3D rightEyeNode
rightEyeNode = vizshape.addSphere(radius = 0.005, color = viz.RED)
#rightEyeNode.visible(viz.OFF) 
rightEyeNode.setParent(headTracker)
rightEyeNode.setPosition(IOD/2, 0, 0.0,viz.ABS_PARENT)
right_sphere = gazeSphere(eyeTracker,viz.RIGHT_EYE,rightEyeNode,[desktopDisplay],sphereColor=viz.ORANGE)
rightGazeVector = gazeVector(eyeTracker,viz.RIGHT_EYE,rightEyeNode,[desktopDisplay],gazeVectorColor=viz.ORANGE)
right_sphere.toggleUpdate()
rightGazeVector.toggleUpdate()
