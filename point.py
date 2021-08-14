class Point:

	def __init__(self, x, y):
		self.x = x
		self.y = y

	#CHECKS TO SEE IF SELF DOMINATES A GIVEN POINT
	def dominates(self, point: 'Point'):
		if self.x < point.x and self.y < point.y:
			return True
		else:
			return False