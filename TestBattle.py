import unittest
import Battle

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


if __name__ == '__main__':
	unittest.main()
