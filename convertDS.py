import re


fob = open("tempdata.txt", "r")

lines = fob.readlines()

obs = []


name = re.compile("^# (\w*)\s*")
diam = re.compile(".*_DIA = ([^\s]*)\s*#")
mass = re.compile(".*_MASS = ([^\s]*)\s*#")
rad = re.compile(".*_INITIAL_RAD = ([^\s]*)\s*#")
color = re.compile("\w*CLR\s*=\s*(\w*)")



c = []
for l in lines:
	g = name.search(l)
	if g:
		c.append(g.groups()[0].capitalize())
	g = diam.search(l)
	if g:
		c.append(g.groups()[0])
	g = mass.search(l)
	if g:
		c.append(g.groups()[0])
	g = rad.search(l)
	if g:
		c.append(g.groups()[0])
	g = color.search(l)
	if g:
		c.append(g.groups()[0])
	if l == "\n":
		print c
		obs.append(c)
		c = []


template1 = """
"%s":{
	"dia":"%s",
	"mass":"%s",
	"rad":"%s"
}
"""
template2 = """
"%s":{
	"dia":"%s",
	"mass":"%s",
	"rad":"%s",
	"color":"%s"
}
"""


for i in obs:
	if len(i)==4:
		print template1 % tuple(i)
	else:
		print template2 % tuple(i)

