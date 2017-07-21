import numpy as np

class Body():
	def __init__(self, name, diameter, mass, radius, velocity, parent = None):
		self.name = name
		self.dia = diameter
		self.mass = mass
		self.radius = radius
		self.parent = parent
		self.velocity = np.array(velocity, dtype = np.float64)
		self.children = []
		if self.parent:
			self.parent.children.append(self)


	def getParent(self):
		return self.parent
	def getSatelites(self):
		return iter(self.children)

	def _str(self, depth):
		rslt = depth*3*" "+self.name
		for i in self.children:
			rslt += "\n"+depth*3*" "+i._str(depth+1)
		return rslt
	def show(self):
		return self._str(0)
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.name+str(list(self.velocity))
