import glob
import sys
from PIL import Image
from PIL import ImageShow
import os
import os.path
import itertools
import random
import math

import os
import wx

PREVIEW_SIZE = wx.Point(640, 640)
PEEK_SIZE = wx.Size(256, 256)
		
import Battle

def getPeekImage(im, pos):
	"""Get the small part from im around position cursorPosition of size PEEK_SIZE"""
	image = Image.new("RGB", (PEEK_SIZE.width, PEEK_SIZE.height), "black")
	imSize = wx.Point(im.size[0], im.size[1])

	# Check if the cursor is inside the image
	if(	pos.x > 0 and 
		pos.y > 0 and 
		imSize.x - pos.x > 0 and 
		imSize.y - pos.y > 0):				
			# element that will be taken from the original image
			cropElement = [ pos.x - (PEEK_SIZE.width/2), pos.y - (PEEK_SIZE.height/2), pos.x + (PEEK_SIZE.width/2),  pos.y + (PEEK_SIZE.height/2) ]

			# Remove invalid positions (out of the image)
			if cropElement[0] < 0:  cropElement[0] = 0
			if cropElement[0] >= imSize.x:  cropElement[0] = imSize.x - 1 
			if cropElement[1] < 0:  cropElement[1] = 0
			if cropElement[1] >= imSize.y:  cropElement[1] = imSize.y + 1

			smallPart = im.crop( cropElement );

			# add the PEEK image at the right position, taking care of the mouse cursor position if it was too close
			# to a border (then PEEK_SIZE.width > smallPart.size[0])
			image.paste(smallPart, (PEEK_SIZE.width - smallPart.size[0], PEEK_SIZE.height - smallPart.size[1]))
	return image










class PhotoCtrl(wx.App):
	currentBest = None
	currentBattle = None
	# List of elements ordered from the best to the worst
	winners = []

	# Rectangle describing where the image 1 is located in the panel. Is a rectangle (x, y, width, height)
	posIm1 = wx.Rect(0,0, 1, 1)

	# Rectangle describing where the image 2 is located in the panel. Is a rectangle (x, y, width, height)
	posIm2 = wx.Rect(0,0, 1, 1)

	def __init__(self, redirect=False, filename=None):
		wx.App.__init__(self, redirect, filename)
		self.frame = wx.Frame(None, title='Photo Control')
		self.framePeek = wx.Frame(None, title='Peek', size=PEEK_SIZE)
		self.frameResult = wx.Frame(None, title='Result')

		self.panel = wx.Panel(self.frame)
		self.panelPeek = wx.Panel(self.framePeek)
		self.panelResult = wx.Panel(self.frameResult)

		self.createWidgetsMainFrame()
		self.createWidgetsPeekFrame()
		self.createWidgetsResultFrame()
		self.frame.Show()

	def createWidgetsResultFrame(self):
		self.text = wx.TextCtrl(self.panelResult, value="hello\nworld", size=(800,600), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL|wx.TE_RICH)
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.text)
		self.sizer.Fit(self.frameResult)

	def createWidgetsPeekFrame(self):
		self.imgPeek = wx.EmptyImage(PEEK_SIZE.width, PEEK_SIZE.height)
		self.imagePeekCtrl = wx.StaticBitmap(self.panelPeek, wx.ID_ANY, 
			wx.BitmapFromImage(self.imgPeek))
		
		self.panelPeek.Layout()

	def createWidgetsMainFrame(self):
		self.img = wx.EmptyImage(PREVIEW_SIZE[0] * 2,PREVIEW_SIZE[1])
		self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
										 wx.BitmapFromImage(self.img))
		self.imageCtrl.Bind(wx.EVT_MOUSE_EVENTS, self.onHoover)
		dirBtn = wx.Button(self.panel, label='Choose Directory')
		self.leftBtn = wx.Button(self.panel, label='Left')
		self.rightBtn = wx.Button(self.panel, label='Right')
		
		self.label = wx.StaticText(self.panel, label='Select image directory', style=wx.ALIGN_CENTER_VERTICAL)

		self.leftBtn.Disable()
		self.rightBtn.Disable()
		
		dirBtn.Bind(wx.EVT_BUTTON, self.onBrowse)
		self.leftBtn.Bind(wx.EVT_BUTTON, self.onSelect)
		self.rightBtn.Bind(wx.EVT_BUTTON, self.onSelect)

		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
						   0, wx.ALL | wx.EXPAND, 5)
		self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
		self.sizer.Add(dirBtn, 0, wx.ALL, 5)         
		self.sizer.Add(self.leftBtn, 0, wx.ALL, 5)         
		self.sizer.Add(self.rightBtn, 0, wx.ALL, 5)          
		self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)          
		self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)

		self.panel.SetSizer(self.mainSizer)
		self.mainSizer.Fit(self.frame)

		self.panel.Layout()

	def setLabel(self, str):
		self.label.SetLabelText(str)

	def onBrowse(self, event):
		""" Show the browsing dialog to the user and load data from the directory"""
		dialog = wx.DirDialog(None, "Choose a directory",
							   style=wx.DD_DIR_MUST_EXIST)
		if dialog.ShowModal() == wx.ID_OK:
			self.generateBattle(dialog.GetPath())
			self.leftBtn.Enable()
			self.rightBtn.Enable()

		dialog.Destroy() 
		self.onView()


	def onHoover(self, event):
		""" Called when the cursor is going over the images """
		if(self.currentBattle == None):
			return

		if event.X < PREVIEW_SIZE[0]:
			posIm = self.posIm1
			im = self.currentBattle.a.getWinner().fullImage
		else:
			posIm = self.posIm2
			im = self.currentBattle.b.getWinner().fullImage

		pos = wx.Point(event.X - posIm.x, event.Y - posIm.y)
		posRelative = wx.Point2D(float(pos.x)/posIm.width,float(pos.y)/posIm.height)
		
		imSize = wx.Point(im.size[0], im.size[1])
		pos = wx.Point(int(posRelative.x * imSize.x), int(posRelative.y * imSize.y ))

		# create the PEEK images
		imWx = wx.EmptyImage(PEEK_SIZE.width, PEEK_SIZE.height)

		imWx.SetData(getPeekImage(im, pos).tostring())
		self.imagePeekCtrl.SetBitmap(wx.BitmapFromImage(imWx))


	def generateBattle(self, path):
		""" Generate the main battle structure with the different Contestants and the associated images """
		contestants = []
		for file_name in glob.glob(os.path.join(path, "*.jpg")):
			im = Image.open(file_name)
			fullIm = im.copy()
			im.thumbnail(PREVIEW_SIZE, Image.ANTIALIAS)
			contestants.append(Battle.Contestant(file_name, im, fullIm))
		self.setLabel("Number of images loaded: %d"%( len(contestants), ))
		self.currentBest = Battle.GenerateBattles(contestants)
		self.currentBattle = self.currentBest.GetNextUndecided()


	def onSelect(self, event):
		"""The user selected an image"""
		if event.GetEventObject() == self.leftBtn:
			self.currentBattle.WinnerIsA()
			print "Left button pressed"
		else:
			self.currentBattle.WinnerIsB()
			print "Right button pressed"
				
		self.currentBattle = self.currentBest.GetNextUndecided()
			
		if self.currentBattle == None:
			while(self.currentBest != None and self.currentBest.IsDecided()):
				self.winners.append(self.currentBest.getWinner().id)
				self.currentBest = self.currentBest.RemoveWinner()
			
			if self.currentBest == None:
				self.leftBtn.Disable()
				self.rightBtn.Disable()
				self.currentBattle = None
				self.text.SetLabelText("\n".join(self.winners))
				self.frameResult.Show()

			else:
				self.currentBattle = self.currentBest.GetNextUndecided()
	
		self.onView()
			
	def onView(self):
		"""Redraw the images using new data for the current Battle"""
		if self.currentBattle != None:
			assert(not self.currentBattle.IsDecided())
			c0 = self.currentBattle.a.getWinner()
			c1 = self.currentBattle.b.getWinner()

			imPIL = Image.new('RGBA', (PREVIEW_SIZE[0] * 2, PREVIEW_SIZE[1]))
			
			height0 = (PREVIEW_SIZE[1] - c0.im.size[1]) / 2
			imPIL.paste(c0.im, (0,height0))
			self.posIm1 = wx.Rect(0,height0, c0.im.size[0], c0.im.size[1])

			height1 = (PREVIEW_SIZE[1] - c1.im.size[1]) / 2
			imPIL.paste(c1.im, (PREVIEW_SIZE[0],height1))
			self.posIm2 = wx.Rect(PREVIEW_SIZE[0],height1, c1.im.size[0], c1.im.size[1])

			imWx = wx.EmptyImage(imPIL.size[0],imPIL.size[1])
			imWx.SetData(imPIL.convert("RGB").tostring())

			self.imageCtrl.SetBitmap(wx.BitmapFromImage(imWx))
			self.panel.Refresh()
			
			# Show the zoom frame
			self.framePeek.Show()

if __name__ == '__main__':
	app = PhotoCtrl()
	app.MainLoop()
