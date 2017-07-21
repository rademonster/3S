#!/usr/bin/env python
import json, os, math
import numpy as np
from BackEndData import NAMESPACE, G

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
	reservedWords = requiredWords + ["color", "avg_dia", "vel"]
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
				if "color" in tree[key]:
					color = self._evalExpr(tree[key]["color"])
				else:
					color = self._evalExpr("WHITE")
				if "vel" in tree[key]:
					vel = self._evalExpr(tree[key]["vel"])
				elif parent:
					vel = math.sqrt(G*(parent.mass**2)/(rad*(mass + parent.mass)))
				else:
					vel = [0,0]
				b = Body(key, dia, mass, rad, vel, parent)
				self._index[key] = b
				if not parent:
					self._roots.append(b)
				walk(tree[key], b)
		walk(raw, None)

	def getRoots(self):
		return self._roots

	def _evalExpr(self, exp):
		if isinstance(exp, unicode) or isinstance(exp, str):
			ns = NAMESPACE.copy()
			exec "val="+exp in ns
			return ns["val"]
		return exp

	def _formatNumber(self, number):
		return np.array([self._evalExpr(number)], dtype = np.float64)

	def _checkSpec(self, name, tree):
		for req in System.requiredWords:
			if req not in tree:
				#raise NameError("Body "+name+" has no "+req+" field.")
				print("Error: Body "+name+" has no "+req+" field. This body will not be added to the system.")
				return False
		return True

	def __iter__(self):
		return _sysiter(self._index.iteritems())

class _sysiter():
	def __init__(self, it):
		self.it = it
	def __iter__(self):
		return self
	def next(self):
		return self.it.next()[1]
	def __next__(self):
		return self.next()



if __name__ == "__main__":
	print("Running system tests")
	sys = System(os.path.abspath('resources/systems/solar.json'))
	sun = sys._index["Earth"]
	print "Printing parents"
	for b in sys:
		i = b.name
		print i+"'s parent is "+ (b.parent.name if b.parent else "None")
		print i+"'s children are "+str(b.children)
		print i+"'s velocity is "+str(b.velocity)
	print sys.getRoots()[0]

