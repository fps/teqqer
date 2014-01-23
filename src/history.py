 
class history:
	def __init__(self):
		# A list of tuples of lambdas where the first
		# entry in each tuple is the action and the second
		# is the action with the inverse effect.
		self.reset()
		
	def add(self, action, inverse_action):		
		if self.last > -1:
			self.actions = self.actions[0:self.last+1]
		
		self.actions.append((action, inverse_action))
		self.last += 1
		
		action()
		
	def undo(self):
		if self.last > -1:
			self.actions[self.last][1]()
			self.last -= 1
	
	def redo(self):
		if self.last + 1 < len(self.actions):
			self.actions[self.last + 1][0]()
			self.last += 1
			
	def reset(self):
		self.actions = []
		self.last = -1

