#!/usr/bin/env python
import json, os
import numpy as np
from BackEndData import AU

class Body():
	def __init__(self, name, diameter, mass, radius, parent = None):
		self.name = name
		self.dia = diameter
		self.mass = mass
		self.radius = radius
		self.parent = parent
		self.children = []
		if self.parent:
			self.parent.children.append(self)

	def _str(self, depth):
		rslt = depth*3*" "+self.name
		for i in self.children:
			rslt += "\n"+depth*3*" "+i._str(depth+1)
		return rslt
	def __str__(self):
		return self._str(0)
	def __repr__(self):
		return self.name



class System():
	requiredWords = ["dia", "mass", "rad"]
	reservedWords = requiredWords + ["avg_dia"]
	def __init__(self, path):
		self._index = {}
		self._roots = []
		raw = json.loads(open(path, "r").read())
		def walk(tree, parent):
			# print ""
			# print tree
			for key in tree:
				if key in System.reservedWords:
					continue
				#print parent, key
				if not self._checkSpec(key, tree[key]):
					continue
				dia = self._formatNumber(tree[key]["dia"])
				mass = self._formatNumber(tree[key]["mass"])
				rad = self._formatNumber(tree[key]["rad"])
				b = Body(key, dia, mass, rad, parent)
				self._index[key] = b
				if not parent:
					self._roots.append(b)
				walk(tree[key], b)
		walk(raw, None)

	def getRoots(self):
		return self._roots


	def _formatNumber(self, number):
		if isinstance(number, unicode) or isinstance(number, str):
			ns = {"AU":AU}
			exec "val="+number in ns
			number = ns["val"]
		return np.array([number], dtype = np.float64)

	def _checkSpec(self, name, tree):
		for req in System.requiredWords:
			if req not in tree:
				#raise NameError("Body "+name+" has no "+req+" field.")
				print("Error: Body "+name+" has no "+req+" field. This body will not be added to the system.")
				return False
		return True





if __name__ == "__main__":
	print("Running system tests")
	sys = System(os.path.abspath('resources/systems/solar.json'))
	sun = sys._index["Sun"]
	print "Printing parents"
	for i in sys._index:
		b = sys._index[i]
		print i+"'s parent is "+ (b.parent.name if b.parent else "None")
		print i+"'s children are "+str(b.children)
	print sys.getRoots()[0]

