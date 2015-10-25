import unittest
import Battle
import random


def startBattle(contestants):
	""" This is a typical workflow for the Battle class: 
	1. Generate a Battle using a list of contestants
	2. As long as the Current battle is not a Single contestant (a Leaf in the graph) :
	  a. check if there is any undecided battle between contestant before we can select a winner for the current battle
	  b. if there is one, fetch it and elect the winner for the battle using WinnerIsA() or WinnerIsB()
	  c. If the current battle is decided (ie a winner has been elected), fetch the winner and create a new graph battle without him.
	     This become the new current battle
	"""
	listOfResults = []

	battle = Battle.GenerateBattles(contestants)

	while not battle.IsLeaf():
		undec = battle.GetNextUndecided()
		if(undec != None):
			a = undec.a.getWinner()
			b = undec.b.getWinner()
			# decide which contestant is stronger depending on its number
			if int(a.id) < int(b.id):
				undec.WinnerIsA()
			else:
				undec.WinnerIsB()
		if battle.IsDecided():
			listOfResults.append(battle.getWinner())
			battle = battle.RemoveWinner()
		
	# append the last element, when b is leaf
	listOfResults.append(battle.getWinner())
	return listOfResults


class TestBattle(unittest.TestCase):

	def test_GenerateBattles(self):
		contestantList = []
		for i in range(5):
			contestantList.append( Battle.Contestant(str(i)) )

		mainBattle = Battle.GenerateBattles(contestantList)

		# Check Topology
		self.assertFalse(mainBattle.IsDecided())
		self.assertFalse(mainBattle.a.IsLeaf())
		self.assertFalse(mainBattle.a.a.IsLeaf())
		self.assertTrue(mainBattle.a.a.a.IsLeaf())
		self.assertTrue(mainBattle.b.IsLeaf())
		
	def test_IsLeaf(self):
		a = Battle.GenerateBattles( [Battle.Contestant("0")] )
		self.assertTrue(a.IsLeaf())

		b = Battle.GenerateBattles( [Battle.Contestant("1"), Battle.Contestant("2")])
		self.assertFalse(b.IsLeaf())


	def test_IsDecided(self):
		a = Battle.GenerateBattles( [Battle.Contestant("0")] )
		self.assertTrue(a.IsDecided())

		b = Battle.GenerateBattles( [Battle.Contestant("1"), Battle.Contestant("2")] )
		self.assertFalse(b.IsDecided())
		b.WinnerIsA()
		self.assertTrue(b.IsDecided())

	def test_GetNextUndecided(self):
		a = Battle.GenerateBattles( [Battle.Contestant("0")] )
		self.assertTrue(a.GetNextUndecided() is None)
		b = Battle.GenerateBattles( [Battle.Contestant("1"), Battle.Contestant("2")] )
		self.assertEqual(b.GetNextUndecided(), b)
		b.WinnerIsA()
		self.assertTrue(b.GetNextUndecided() is None)
		self.assertTrue(b.IsDecided())

	def test_GetWinner(self):
		c1 = Battle.Contestant("1")
		c2 = Battle.Contestant("2")
		c3 = Battle.Contestant("3")

		a = Battle.GenerateBattles( [c1, c2, c3] )

		c =	a.GetNextUndecided()
		c.WinnerIsA()
		self.assertEqual( c.getWinner(), c1 )

	def test_RemoveWinner(self):
		c1 = Battle.Contestant("1")
		c2 = Battle.Contestant("2")
		c3 = Battle.Contestant("3")

		main = Battle.GenerateBattles( [c1, c2, c3])

		# c1 vs. c2
		c = main.GetNextUndecided()
		# c1 winner
		c.WinnerIsA()

		# c1 vs. c3
		d = main.GetNextUndecided()
		# c1 winner
		d.WinnerIsA()
		
		self.assertTrue(main.IsDecided())
		self.assertEqual(main.getWinner(), c1)
		main = main.RemoveWinner()
		self.assertFalse(main.IsDecided())
		
		# winner is c3
		main.WinnerIsB()
		self.assertTrue(main.IsDecided())
		self.assertEqual(main.getWinner(), c2)

		self.assertTrue(main.IsDecided())
		main = main.RemoveWinner()

		self.assertTrue(main.IsDecided())
		self.assertEqual(main.getWinner(), c3)

	def test_Workflow_limit(self):
		"""Check the workflow, from Battle creation to the end, for limit case"""
		# Only one contestant
		listOfContestants1 = [ Battle.Contestant(str(i)) for i in range(1) ]
		listOfResults1 = startBattle(listOfContestants1)

		self.assertListEqual(listOfContestants1, listOfResults1)

		# Only two contestants
		listOfContestants2 = [ Battle.Contestant(str(i)) for i in range(2) ]
		listOfResults2 = startBattle(listOfContestants2)

		self.assertListEqual(listOfContestants2, listOfResults2)

		# lots of contestants
		listOfContestants200 = [ Battle.Contestant(str(i)) for i in range(200) ]
		listOfResults200 = startBattle(listOfContestants200)

		self.assertListEqual(listOfContestants200, listOfResults200)

	def test_Workflow_ordered(self):
		"""Check the workflow, from Battle creation to the end, for ordered data"""
		# The list is ordered, odd number
		listOfContestantsO = [ Battle.Contestant(str(i)) for i in range(13) ]
		listOfResultsO = startBattle(listOfContestantsO)

		self.assertListEqual(listOfContestantsO, listOfResultsO)

		# The list is ordered, even number
		listOfContestantsE = [ Battle.Contestant(str(i)) for i in range(12) ]
		listOfResultsE = startBattle(listOfContestantsE)

		self.assertListEqual(listOfContestantsE, listOfResultsE)

	def test_Workflow_unordered(self):
		"""Check the workflow, from Battle creation to the end, for unordered data"""
		# The list is ordered, odd number
		listOfContestantsO = [ Battle.Contestant(str(i)) for i in range(15) ]
		
		# copy the list and shuffle it
		shuffledlistOfContestantsO = listOfContestantsO[:]
		random.shuffle(shuffledlistOfContestantsO)

		listOfResultsO = startBattle(shuffledlistOfContestantsO)

		self.assertListEqual(listOfContestantsO, listOfResultsO)

		# The list is ordered, even number
		listOfContestantsE = [ Battle.Contestant(str(i)) for i in range(14) ]
		
		# copy the list and shuffle it
		shuffledlistOfContestantsE = listOfContestantsE[:]
		random.shuffle(shuffledlistOfContestantsE)

		listOfResultsE = startBattle(shuffledlistOfContestantsE)

		self.assertListEqual(listOfContestantsE, listOfResultsE)



if __name__ == '__main__':
	unittest.main()
