import math, pygame
import numpy as np
from BackEndData import *

##################################################################################
######## BODY CREATER ########
##############################

class Body(object):
    # INITIALIZING BODY
    def __init__(self, name, parent, dia, mass, vel, rad, color, IS):
        print(name)
        self.Name = name
        self.Diameter = dia
        self.Mass = np.array([mass], dtype = np.float64)
        self.Color = color
        self.Parent = parent
        self.Children = []
        self.Is = IS

        # IF PARENT EXISTS, ASSUME POSITION AND VELOCITY ARE RELATIVE TO PARENT
        if parent!= None:
            self.Position = np.array([rad,0], dtype = np.float64) + self.Parent.Position

            # ADDING SPHERE OF INFLUENCE IF PARENT EXISTS
            dist = np.linalg.norm(self.Position - self.Parent.Position)
            SOI = dist*((self.Mass/self.Parent.Mass)**(2/5))
            self.SOI = SOI

            # IF NO VELOCITY GIVEN, ASSUME CIRCULAR ORBIT,
            # ELSE, ASSUME VELOCITY GIVEN IS RELATIVE TO PARENT
            if vel == None:
                dist = np.linalg.norm(self.Position - self.Parent.Position)
                vel = math.sqrt(G*(self.Parent.Mass[0]**2)/(dist*(self.Mass[0] + self.Parent.Mass[0])))
                self.Velocity = np.array([0,vel], dtype = np.float64) + self.Parent.Velocity
            else:
                self.Velocity = np.array([0,vel + self.Parent.Velocity[1]], dtype = np.float64)
        else:
            self.Position = np.array([rad,0], dtype = np.float64)
            self.Velocity = np.array([0,vel], dtype = np.float64)
            self.SOI = None


    # ADDERS
    def addChild(self, Child):
        self.Children.append(Child)


    # GETTERS
    def getChildren(self):
        return self.Children
    def getParent(self):
        return self.Parent


    # SYSTEM STUFF
    #def _str(self, depth):
    #   rslt = depth*3*" "+self.name
    #   for i in self.Children:
    #       rslt += "\n"+depth*3*" "+i_str(depth+1)
    #   return rslt
    #def show(self):
    #   returnself._str(0)
    #def __str__(self):
    #   return self.Name
    #def __repr__(self):
    #   return self.Name + str(list(self.Velocity))


    # DISPLAY
    def display(self, DISPLAYSURF, KM2PIX, Focus, SOI):
        MiddlePoint = KM2PIX*(self.Position - Focus)
        CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
        CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

        # ENABLING DISSAPPEARING PLANETS
        # pixelSize = KM2PIX*self.Diameter/2
        # if CheckXAxis and CheckYAxis and pixelSize > 0.5
        if CheckXAxis and CheckYAxis:
            pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*round(self.Diameter/2)), 0)
            
            if SOI and self.SOI != None and self.SOI*KM2PIX > 1:
                pygame.draw.circle(DISPLAYSURF, WHITE, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(self.SOI*KM2PIX), 1)
