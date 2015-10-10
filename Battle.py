def GenerateBattles(listOfContestants):
	battleList = []
	for c in listOfContestants:
		battleList.append(Battle(c))
	return generateBattlesImpl(battleList)

def generateBattlesImpl(listOfContestants):
	"""Recursive function : will generate pair of the elements given
	in parameters, creating a pyramid. Return the top element at the end"""
	
	if len(listOfContestants) == 1:
		return Battle(listOfContestants[0], None)
	elif len(listOfContestants) == 2:
		return Battle(listOfContestants[0], listOfContestants[1])
	else:
		battleList = []
		max_battle = len(listOfContestants) / 2
	
		for i in range(max_battle):
			battleList.append(Battle(listOfContestants[i], listOfContestants[i + 1]))

		# Last element will be a leaf
		if len(listOfContestants) % 2 == 1:
			battleList.append(listOfContestants[-1])
	
		return generateBattlesImpl(battleList)
		

class Contestant:
	"""All data about an Image. TODO: Get out of Battle"""

	def __init__(self, myId, image=None, fullImage=None):
		self.im = image
		self.id = myId
		self.fullImage = fullImage

class Battle:
		"""A battle or a leaf"""
		
		def __init__(self, a, b=None):
			"""A Battle between 2 contestants"""
			self.a = a
			self.b = b

			self.winner = None

			# If you are a leaf, you are automatically the winner
			if b == None:
				self.winner = self.a
			
		def IsDecided(self):
			return self.winner != None

		def IsLeaf(self):
			return self.b == None

		def __str__(self):
			return "%s - Decided: %s, Leaf %s" % (self.id, str(self.IsLeaf()), set(self.IsDecided()))
		
		
		def GetNextUndecided(self):
			if self.IsDecided():
				return None

			if not self.a.IsDecided():
				return self.a.GetNextUndecided()

			if not self.b.IsDecided():
				return self.b.GetNextUndecided()

			return self
		
		def WinnerIsA(self):
			self.winner = self.a

		def getContestant(self):
			assert(self.b == None)
			return self.a

		def WinnerIsB(self):
			self.winner = self.b
		

		def getWinner(self):
			"""Get the winner (Contestant) of the current battle.  On a Leaf, the current
			element is the winner"""
			assert(self.winner != None)
			if(self.IsLeaf()):
				return self.getContestant()
			return self.winner.getWinner()

		def getLoosingBattle(self):
			"""Get the looser (Battle) of the current battle."""
			assert(self.winner != None)
			assert(not self.IsLeaf())
			if self.winner == self.a:
				return self.b
			else:
				return self.a
		
		def RemoveWinner(self):
			"""Return a new graph where the winner have been removed"""
			if self.IsLeaf():
				return None
			elif self.winner.IsLeaf() :
				return self.getLoosingBattle()
			else:
				return Battle(self.getLoosingBattle(), self.winner.RemoveWinner())