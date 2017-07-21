# SOLAR SYSTEM SIMULATOR

import pygame, math, sys, os
import numpy as np
from pygame.locals import *
from BackEndData import *


##################################################################################
############# MAIN PROGRAM ##############
#########################################

# ==================================================
# MAIN METHOD
# Handles:
#   - FPS
#   - Display Window Params
#   - Calling Initialiation Method
#   - Calling Pysics Engine
#   - Calling GUI
#   - Calling Renderer
#   - Refreshing Display Window
def main():
    global FPSCLOCK, DISPLAYSURF
    TIME_SCALAR = 1
    ACTUAL_SCALAR = 0
    GOD_LOOP = int(1)
    BASIC_LOOP = int(FPS+1)
    BASIC_LOOP_COUNTER = int(1)
    FPSCLOCK = pygame.time.Clock()
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((SURF_WIDTH, SURF_HEIGHT))
    pygame.display.set_caption('Solar System Simulator')

    initialize_bodies()
    
    FocusBody = SUN
    # MAP LISTS
    global MAP_LEVEL, MAP_PLANET_INDEX, MAP_SATELLITE_INDEX
    M_LIST0 = [SUN]
    M_LIST1 = [SUN] + PLANETS
    M_LIST2 = [[SUN], [MERCURY], [VENUS], [EARTH, MOON], [MARS, PHOBOS, DEIMOS], [CERES], [JUPITER, IO, EUROPA, GANYMEDE, CALLISTO], [SATURN, RHEA, TITAN], [URANUS, MIRANDA, ARIEL, UMBRIEL, TITANIA, OBERON], [NEPTUNE, TRITON], [PLUTO, CHARON]]
    MAP = [M_LIST0, M_LIST1, M_LIST2]
    MAP_LEVEL = int(0)
    MAP_PLANET_INDEX = int(0)
    MAP_SATELLITE_INDEX = int(0)

    SOI = False

    KM2PIX = np.array([1./1000], dtype = np.float64)
    
    # GAME LOOP
    while True:
        START_UPS_TIC = FPSCLOCK.get_time()
        
        # GAME EVENTS
        for event in pygame.event.get():
            # EXIT CONDITION
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            # KEY INPUT LOOP
            elif event.type == KEYDOWN:
                
               ## ZOOM INPUT ##
                if event.key == K_SLASH:
                    # ZOOM IN
                    if KM2PIX >= 1/10:
                        KM2PIX *= 2
                    else:
                        KM2PIX *= 10
                elif event.key == K_PERIOD:
                    # ZOOM OUT
                    if KM2PIX <= 1/10:
                        KM2PIX /= 10
                    else:
                        KM2PIX /= 2
                    
                ## TIME_SCALAR KEY INPUT ##
                elif event.key == K_RIGHTBRACKET:
                    if BASIC_LOOP > 1:
                        BASIC_LOOP -= 10
                    elif TIME_SCALAR < 10000:
                        TIME_SCALAR *= 10
                    else: 
                        GOD_LOOP *= 2
                elif event.key == K_LEFTBRACKET:
                    if GOD_LOOP > 1:
                        GOD_LOOP = int(GOD_LOOP/2)
                    elif TIME_SCALAR > 1:
                        TIME_SCALAR = int(TIME_SCALAR/10)
                    elif BASIC_LOOP < FPS:
                        BASIC_LOOP += 10


                ## MAP / FOCUS KEY INPUT ##
                # KEY UP            
                elif event.key == K_UP and MAP_LEVEL != 0:
                    MAP_LEVEL -= 1
                    # ZOOM OUT
                    if KM2PIX <= 1/10:
                        KM2PIX /= 10
                    else:
                        KM2PIX /= 2
                # KEY DOWN
                elif event.key == K_DOWN and MAP_LEVEL < 2:
                    MAP_LEVEL += 1
                    # ZOOM IN
                    if KM2PIX >= 1/10:
                        KM2PIX *= 2
                    else:
                        KM2PIX *= 10
                    # RESET SAT INDEX
                    if MAP_LEVEL == 2:
                        MAP_SATELLITE_INDEX = 0
                # KEY RIGHT
                elif event.key == K_RIGHT:
                    if MAP_LEVEL == 1:
                        MAP_PLANET_INDEX += 1
                    elif MAP_LEVEL == 2:
                        MAP_SATELLITE_INDEX += 1
                # KEY LEFT
                elif event.key == K_LEFT:
                    if MAP_LEVEL == 1:
                        MAP_PLANET_INDEX -= 1
                    elif MAP_LEVEL == 2:
                        MAP_SATELLITE_INDEX -= 1
                
                # ENSURING POSITIVE INDICES
                if MAP_PLANET_INDEX < 0:
                    MAP_PLANET_INDEX = len(M_LIST1) + MAP_PLANET_INDEX
                if MAP_SATELLITE_INDEX < 0:
                    MAP_SATELLITE_INDEX = len(MAP[MAP_LEVEL][MAP_PLANET_INDEX]) + MAP_SATELLITE_INDEX
                        
                # SETTING FOCUS BODY
                if MAP_LEVEL == 0:
                    FocusBody = MAP[MAP_LEVEL][0]
                elif MAP_LEVEL == 1:
                    try:
                        FocusBody = MAP[MAP_LEVEL][MAP_PLANET_INDEX]
                    except:
                        MAP_PLANET_INDEX = 0
                        FocusBody = MAP[MAP_LEVEL][MAP_PLANET_INDEX]
                else:
                    try:
                        FocusBody = MAP[MAP_LEVEL][MAP_PLANET_INDEX][MAP_SATELLITE_INDEX]
                    except:
                        MAP_SATELLITE_INDEX = 0
                        FocusBody = MAP[MAP_LEVEL][MAP_PLANET_INDEX][MAP_SATELLITE_INDEX]

                    


        ### RUNNING PHYSICS ENGINE ###
        # LINEAR SCALE
        if ACTUAL_SCALAR != TIME_SCALAR:
            if ACTUAL_SCALAR == 0 and TIME_SCALAR == 1:
                PhysicsEngine(TIME_SCALAR)
            elif ACTUAL_SCALAR > TIME_SCALAR:
                ACTUAL_SCALAR -= 5
            else:
                ACTUAL_SCALAR += 5
            PhysicsEngine(ACTUAL_SCALAR)
            
        # BASIC LOOP, FOR WHEN SIM IS BETWEEN 1SEC AND 60SEC
        elif BASIC_LOOP > 1 and BASIC_LOOP_COUNTER >= 1 and GOD_LOOP == 1:
            if BASIC_LOOP_COUNTER == BASIC_LOOP:
                PhysicsEngine(TIME_SCALAR)
            elif BASIC_LOOP_COUNTER == 60:
                BASIC_LOOP_COUNTER = 1
            else:
                BASIC_LOOP_COUNTER += 1

        # GOD MODE
        elif GOD_LOOP > 1:
            for x in range(0, GOD_LOOP):
                PhysicsEngine(TIME_SCALAR)
        
        else:
            PhysicsEngine(TIME_SCALAR)
        
        
        # FOCUS ON...
        Focus = FocusBody.Position

        # RENDERING OBJECTS
        DISPLAYSURF.fill(BGCOLOR)
        Renderer(KM2PIX[0], Focus, SOI)
        Sim_Speed = TIME_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP) if ACTUAL_SCALAR == 0 else ACTUAL_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP)
        GUI(Sim_Speed, FocusBody, KM2PIX[0], FPSCLOCK, START_UPS_TIC)
        pygame.display.update()
        
        # IF NOT GOING THROUGH THE LINEAR SCALE, STICK TO 60 FPS LIMIT
        if ACTUAL_SCALAR == TIME_SCALAR or ACTUAL_SCALAR == 0:
            FPSCLOCK.tick(FPS)



# ==================================================
# GUI
# Handles:
#   - Displaying list of bodies in system
#   - Displaying current focus point
#   - Displaying TIME_SCALAR
def GUI(Sim_Speed, FocusBody, KM2PIX, FPSCLOCK, START_UPS_TIC):
    # SETTING UP FONT
    path = os.path.abspath('resources/fonts/Cubellan.ttf')
    BasicFont = pygame.font.Font(path, 12)

    ### INFORMATION GUI TOP LEFT ###
    # BACKGROUND
    BGCOLOR = DARKGRAY
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (10, 10, 120, 54), 0)
    pygame.draw.rect(DISPLAYSURF, WHITE, (7, 7, 126, 60), 1)
    pygame.draw.rect(DISPLAYSURF, WHITE, (4, 4, 132, 66), 1)

    # FOCUSED ON... TEXT
    temp = 'Focus - %s' %FocusBody.Name
    FocusText = BasicFont.render(temp, True, WHITE)
    DISPLAYSURF.blit(FocusText, (12,12))

    # SIM SPEED TEXT
    temp = 'SimSpeed %s' %Sim_Speed
    SimSpeedText = BasicFont.render(temp, True, WHITE)
    DISPLAYSURF.blit(SimSpeedText, (12, 24))

    # KM2PIX TEXT
    temp = 'Scale: %s' %KM2PIX
    ScaleText = BasicFont.render(temp, True, WHITE)
    DISPLAYSURF.blit(ScaleText, (12, 36))

    # UPS/FPS DISPLAY TEXT
    if FPSCLOCK.get_time() > 0:
        UPS = int(1000/FPSCLOCK.get_time())
        temp = 'UPS: %s' %UPS
        #FPS = int(FPSCLOCK.get_fps())
        #temp = 'FPS: %s' %FPS
        Text = BasicFont.render(temp, True, WHITE)
        DISPLAYSURF.blit(Text, (12, 48))
    else:
        UPSText = BasicFont.render('TOO FAST', True, WHITE)
        DISPLAYSURF.blit(UPSText, (12, 48))


    # RETICLE
    radius = int(round(FocusBody.Diameter*KM2PIX/2) + 5)
    pygame.draw.circle(DISPLAYSURF, WHITE, (int(round(SURF_WIDTH/2)), int(round(SURF_HEIGHT/2))), radius, 1)
    pygame.draw.polygon(DISPLAYSURF, WHITE, ((round(SURF_WIDTH/2) - 3, round(SURF_HEIGHT/2) - radius), (round(SURF_WIDTH/2), round(SURF_HEIGHT/2) - radius - 5), (round(SURF_WIDTH/2) + 3, round(SURF_HEIGHT/2) - radius)), 1)
    temp = FocusBody.Name
    text = BasicFont.render(temp, True, WHITE)
    textrect = text.get_rect()
    textrect.centerx = round(SURF_WIDTH/2)
    textrect.centery = round(SURF_HEIGHT/2) - radius - 12
    DISPLAYSURF.blit(text, textrect)

    # MAP & CHANGE FOCUS
    

# ==================================================
# RENDERER
# Handles:
#   - Iterating through all Stars, Planets, Moons and Calling Display Function
#   - Zoom
#   - Conversion of km to pixels
def Renderer(KM2PIX, Focus, SOI):
    
    #for Star in STARS:
    #    Star.display(KM2Pix, Focus)
    SUN.display(KM2PIX, Focus)

    for Planet in PLANETS:
        Planet.display(KM2PIX, Focus, SOI)

    for Sat in SATELLITES:
        Sat.display(KM2PIX, Focus)


# ==================================================
# PHYSICS ENGINE
# Handles:
#   - Updating Velocity and Position of All Stars, Planets, Moons
def PhysicsEngine(TIME_SCALAR):

    for bodyA in ALL_BODIES:

        # DOING SATELLITE CALCS BASED ON PLANET IT ORBITS
        if bodyA.Is == 'Satellite':
            for bodyB in ALL_BODIES:
                # IF bodyB IS NOT bodyA AND (bodyB ORBITS SAME PLANET AS bodyA OR bodyA ORBITS bodyB OR bodyB IS A STAR)
                if bodyA != bodyB and (bodyB.Orbits == bodyA.Orbits or bodyB == bodyA.Orbits or bodyB.Is == 'Star'):
                    DistanceArray = bodyB.Position - bodyA.Position
                    Distance = np.linalg.norm(bodyB.Position - bodyA.Position)
                    angle = math.atan(DistanceArray[1]/DistanceArray[0])
                    GForce = TIME_SCALAR*G*bodyB.Mass[0]/(Distance*Distance)
                    if bodyA.Position[0] > bodyB.Position[0]:
                        ForceX = -math.cos(angle)*GForce[0]
                        ForceY = -math.sin(angle)*GForce[0]
                    else:
                        ForceX = math.cos(angle)*GForce[0]
                        ForceY = math.sin(angle)*GForce[0]

                    bodyA.Velocity = bodyA.Velocity + np.array([ForceX,ForceY])


        # DOING PLANETS AND STAR
        else:
            for bodyB in ALL_BODIES:
                # IF bodyB IS A SAT AND DOES NOT ORBIT bodyA, IGNORE!
                # IF bodyB IS A SAT AND bodyA IS SUN, IGNORE!
                # BUT, bodyA AND bodyB ARE PLANETS, CALCULATE
                if bodyA != bodyB and (bodyB.Orbits != bodyA or bodyB.Is == 'Planet'):
                    DistanceArray = bodyB.Position - bodyA.Position
                    Distance = np.linalg.norm(bodyB.Position - bodyA.Position)
                    angle = math.atan(DistanceArray[1]/DistanceArray[0])
                    GForce = np.array([TIME_SCALAR*G*bodyB.Mass[0]/(Distance*Distance)], dtype = np.float64)
                    GForce = GForce[0]
                    if bodyA.Position[0] > bodyB.Position[0]:
                        Force = np.array([-math.cos(angle)*GForce[0], -math.sin(angle)*GForce[0]], dtype = np.float64)
                    else:
                        Force = np.array([math.cos(angle)*GForce[0],math.sin(angle)*GForce[0]], dtype = np.float64)

                    bodyA.Velocity = bodyA.Velocity + Force
                        
                    if bodyA.Is == 'Planet':
                        bodyA.theta = angle

    for body in ALL_BODIES:
        body.Position = body.Position + TIME_SCALAR*body.Velocity


##################################################################################
#### STAR, PLANET, SATELLITE CREATER ####
#########################################

# --------------------------------------------------
# STAR OBJECT
# Handles:
#   - Creating Stars and Defining Them
#   - Display Function that decides if it is appropriate to "render" object
class Star(object):
    def __init__(self):
        a = 1+1

    def define(self, name, dia, mass, vel, pos):
        print(name)
        self.Name = name
        self.Diameter = dia
        self.Mass = mass
        self.Velocity = vel
        self.Position = pos
        self.Color = YELLOW
        self.Is = 'Star'
        self.Orbits = 0

    def display(self, KM2PIX, Focus):
        MiddlePoint = KM2PIX*(self.Position - Focus)
        CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
        CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

        if CheckXAxis and CheckYAxis:
            pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*round(self.Diameter/2)), 0)


# --------------------------------------------------
# PLANET OBJECT
# Handles:
#   - Creating Planets and Defining Them
#   - Display Function that decides if it is appropriate to "render" object
class Planet(object):
    def __init__(self):
        a = 1+1

    def define(self, name, orbits, dia, mass, theta, vel, pos, color):
        print(name)
        self.Name = name
        self.Orbits = orbits
        self.Diameter = dia
        self.Mass = mass
        self.Theta = theta
        self.Velocity = vel
        self.Position = pos
        self.PrevPosition = pos
        self.Color = color
        self.Is = 'Planet'
        
        # SPHERE OF INFLUENCE
        # NOTE: THIS COULD BE PUT IN THE PHYSICS ENGINE, BUT TO AVOID
        # REDUNDANT RECALCULATIONS, IT IS PUT IN THE DEFINITION
        ### WARNING ###
        # SOI IS CURRENTLY AN UN-USED VARIABLE, IMPLEMENTATION WILL
        # COME WITH PLAYER IMPLEMENTATION
        Star = self.Orbits
        DistanceArray = Star.Position - self.Position
        Distance = math.sqrt((DistanceArray[0]**2) + (DistanceArray[1]**2))
        SOI = Distance*((self.Mass/Star.Mass)**(2/5))
        self.SOI = SOI
        
    def display(self, KM2PIX, Focus, SOI):
        MiddlePoint = KM2PIX*(self.Position - Focus)
        CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
        CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

        if CheckXAxis and CheckYAxis:
            pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*round(self.Diameter/2)), 0)
            
            if SOI and self.SOI*KM2PIX > 1:
                pygame.draw.circle(DISPLAYSURF, WHITE, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(self.SOI*KM2PIX), 1)


# --------------------------------------------------
# SATELLITE OBJECT
# Handles:
#   - Creating Moons and Defining Them
# TO COME...- Display Function that decides if it is appropriate to "render" object
class Satellite(object):
    def __init__(self):
        a = 1+1

    def define(self, name, orbits, dia, mass, theta, vel, pos, color):
        print(name)
        self.Name = name
        self.Orbits = orbits
        self.Diameter = dia
        self.Mass = mass
        self.Theta = theta
        self.Velocity = vel
        self.Position = pos
        self.Color = color
        self.Is = 'Satellite'

    def display(self, KM2PIX, Focus):
        MiddlePoint = KM2PIX*(self.Position - Focus)
        CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
        CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

        if CheckXAxis and CheckYAxis:
            pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*round(self.Diameter/2)), 0)


# --------------------------------------------------
# BODY OBJECT
class Body(object):
    # INITIALIZING BODY
    def __init__(self, name, parent, dia, mass, vel, rad, color, IS):
        print(name)
        self.Name = name
        self.Diameter = dia
        self.Mass = np.array([mass], dtype = np.float64)
        self.Color = color
        self.Orbits = parent
        self.Children = []
        self.Is = IS

        # IF PARENT EXISTS, ASSUME POSITION AND VELOCITY ARE RELATIVE TO PARENT
        if parent!= None:
            self.Position = np.array([rad,0], dtype = np.float64) + self.Orbits.Position

            # ADDING SPHERE OF INFLUENCE IF PARENT EXISTS
            dist = np.linalg.norm(self.Position - self.Orbits.Position)
            SOI = dist*((self.Mass/self.Orbits.Mass)**(2/5))
            self.SOI = SOI

            # IF NO VELOCITY GIVEN, ASSUME CIRCULAR ORBIT,
            # ELSE, ASSUME VELOCITY GIVEN IS RELATIVE TO PARENT
            if vel == None:
                dist = np.linalg.norm(self.Position - self.Orbits.Position)
                vel = math.sqrt(G*(self.Orbits.Mass[0]**2)/(dist*(self.Mass[0] + self.Orbits.Mass[0])))
                self.Velocity = np.array([0,vel], dtype = np.float64) + self.Orbits.Velocity
            else:
                self.Velocity = np.array([0,vel + self.Orbits.Velocity[1]], dtype = np.float64)
        else:
            self.Position = np.array([pos], dtype = np.float64)
            self.Velocity = np.array([vel], dtype = np.float64)

        


    # ADDERS
    def addChild(Child):
        self.Children.append[Child]


    # GETTERS
    def getChildren():
        return self.Children
    def getParent():
        return self.Parent


    # SYSTEM STUFF
    


    # DISPLAY
    def display(self, KM2PIX, Focus):#, SOI):
        MiddlePoint = KM2PIX*(self.Position - Focus)
        CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
        CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

        # ENABLING DISSAPPEARING PLANETS
        # pixelSize = KM2PIX*self.Diameter/2
        # if CheckXAxis and CheckYAxis and pixelSize > 0.5
        if CheckXAxis and CheckYAxis:
            pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*round(self.Diameter/2)), 0)
            
            #if SOI and self.SOI*KM2PIX > 1:
            #    pygame.draw.circle(DISPLAYSURF, WHITE, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(self.SOI*KM2PIX), 1)

            

 
# ==================================================
# INTIALIZATION METHOD
# Handles:
#   - Creating and Defining Stars, Planets, Moons
#   - Creating Callable lists of Stars, Planets, Moons
def initialize_bodies():
    print()
    print("List of Bodies Created...")

    
    ### CREATING STARS ###
    #(name, dia, mass, theta, vel, pos, color)
    
    # SUN
    global SUN
    SUN = Star()
    SUN.define('Sun', SUN_DIA, np.array([SUN_MASS], dtype = np.float64), np.array([0,0], dtype = np.float64), np.array([0,0], dtype = np.float64))
    
    #STARS = [SUN]


    ### CREATING PLANETS ###
    #(name, orbits, dia, mass, theta, vel, pos, color)
    global PLANETS
    
    # EARTH
    global EARTH
    EarthVel = math.sqrt(G*(SUN_MASS**2)/(EARTH_INITIAL_RAD*(EARTH_MASS + SUN_MASS)))
    EARTH = Planet()
    EARTH.define('Earth', SUN, EARTH_DIA, np.array([EARTH_MASS], dtype = np.float64), 0, np.array([0,EarthVel], dtype = np.float64), np.array([EARTH_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, BLUE)

    # MARS
    global MARS
    MarsVel = math.sqrt(G*(SUN_MASS**2)/(MARS_INITIAL_RAD*(MARS_MASS + SUN_MASS)))
    MARS = Planet()
    MARS.define('Mars', SUN, MARS_DIA, np.array([MARS_MASS], dtype = np.float64), 0, np.array([0,MarsVel], dtype = np.float64), np.array([MARS_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, RED)

    # MERCURY
    global MERCURY
    MercVel = math.sqrt(G*(SUN_MASS**2)/(MERCURY_INITIAL_RAD*(MERCURY_MASS + SUN_MASS)))
    MERCURY = Planet()
    MERCURY.define('Mercury', SUN, MERCURY_DIA, np.array([MERCURY_MASS], dtype = np.float64), 0, np.array([0,MercVel], dtype = np.float64), np.array([MERCURY_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, WHITE)

    # VENUS
    global VENUS
    VenVel = math.sqrt(G*(SUN_MASS**2)/(VENUS_INITIAL_RAD*(VENUS_MASS + SUN_MASS)))
    VENUS = Planet()
    VENUS.define('Venus', SUN, VENUS_DIA, np.array([VENUS_MASS], dtype = np.float64), 0, np.array([0,VenVel], dtype = np.float64), np.array([VENUS_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, YELLOW)

    # JUPITER
    global JUPITER
    JupVel = math.sqrt(G*(SUN_MASS**2)/(JUPITER_INITIAL_RAD*(JUPITER_MASS + SUN_MASS)))
    JUPITER = Planet()
    JUPITER.define('Jupiter', SUN, JUPITER_DIA, np.array([JUPITER_MASS], dtype = np.float64), 0, np.array([0,JupVel], dtype = np.float64), np.array([JUPITER_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, ORANGE)

    # SATURN
    global SATURN
    SatVel = math.sqrt(G*(SUN_MASS**2)/(SATURN_INITIAL_RAD*(SATURN_MASS + SUN_MASS)))
    SATURN = Planet()
    SATURN.define('Saturn', SUN, SATURN_DIA, np.array([SATURN_MASS], dtype = np.float64), 0, np.array([0,SatVel], dtype = np.float64), np.array([SATURN_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, SATURNCLR)
    
    # URANUS
    global URANUS
    UraVel = math.sqrt(G*(SUN_MASS**2)/(URANUS_INITIAL_RAD*(URANUS_MASS + SUN_MASS)))
    URANUS = Planet()
    URANUS.define('Uranus', SUN, URANUS_DIA, np.array([URANUS_MASS], dtype = np.float64), 0, np.array([0,UraVel], dtype = np.float64), np.array([URANUS_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, URANUSCLR)
    
    # CERES
    global CERES
    CerVel = math.sqrt(G*(SUN_MASS**2)/(CERES_INITIAL_RAD*(CERES_MASS + SUN_MASS)))
    CERES = Planet()
    CERES.define('Ceres', SUN, CERES_DIA, np.array([CERES_MASS], dtype = np.float64), 0, np.array([0,CerVel], dtype = np.float64), np.array([CERES_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, CERESCLR)

    # PLUTO
    global PLUTO
    PluVel = math.sqrt(G*(SUN_MASS**2)/(PLUTO_AVERAGE_RAD*(PLUTO_MASS + SUN_MASS)))
    PLUTO = Planet()
    PLUTO.define('Pluto', SUN, PLUTO_DIA, np.array([PLUTO_MASS], dtype = np.float64), 0, np.array([0,PluVel], dtype = np.float64), np.array([PLUTO_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, PLUTOCLR)

    # NEPTUNE
    global NEPTUNE
    NepVel = math.sqrt(G*(SUN_MASS**2)/(NEPTUNE_INITIAL_RAD*(NEPTUNE_MASS + SUN_MASS)))
    NEPTUNE = Planet()
    NEPTUNE.define('Neptune', SUN, NEPTUNE_DIA, np.array([NEPTUNE_MASS], dtype = np.float64), 0, np.array([0,NepVel], dtype = np.float64), np.array([NEPTUNE_INITIAL_RAD,0], dtype = np.float64) + SUN.Position, NEPTUNECLR)

    PLANETS = [MERCURY, VENUS, EARTH, MARS, CERES, JUPITER, SATURN, URANUS, NEPTUNE, PLUTO]


    ### CREATING SATELLITES ###
    # BODY REQUIREMENTS: name, parent, dia, mass, vel, pos, color
    # SATERLLITE REQUIREMENTS name, orbits, dia, mass, theta, vel, pos, color
    global SATELLITES
    
    # MOON
    global MOON
    MOON = Body('Moon', EARTH, MOON_DIA, MOON_MASS, None, MOON_INITIAL_RAD, WHITE, 'Satellite')

    # PHOBOS
    global PHOBOS
    PHOBOS = Body('Phobos', MARS, PHOBOS_DIA, PHOBOS_MASS, None, PHOBOS_INITIAL_RAD, PHOBOSCLR, 'Satellite')

    # DEIMOS
    global DEIMOS
    DEIMOS = Body('Deimos', MARS, DEIMOS_DIA, DEIMOS_MASS, None, DEIMOS_INITIAL_RAD, DEIMOSCLR, 'Satellite')

    # IO
    global IO
    IO = Body('Io', JUPITER, IO_DIA, IO_MASS, None, IO_INITIAL_RAD, DEIMOSCLR, 'Satellite')

    # EUROPA
    global EUROPA
    EUROPA = Body('Europa', JUPITER, EUROPA_DIA, EUROPA_MASS, None, EUROPA_INITIAL_RAD, EUROPACLR, 'Satellite')

    # GANYMEDE
    global GANYMEDE
    GANYMEDE = Body('Ganymede', JUPITER, GANYMEDE_DIA, GANYMEDE_MASS, None, GANYMEDE_INITIAL_RAD, GANYMEDECLR, 'Satellite')
    
    # CALLISTO
    global CALLISTO
    CALLISTO = Body('Callisto', JUPITER, CALLISTO_DIA, CALLISTO_MASS, None, CALLISTO_INITIAL_RAD, CALLISTOCLR, 'Satellite')

    # TITAN
    global TITAN
    TITAN = Body('Titan', SATURN, TITAN_DIA, TITAN_MASS, None, TITAN_INITIAL_RAD, TITANCLR, 'Satellite')

    # RHEA
    global RHEA
    RHEA = Body('Rhea', SATURN, RHEA_DIA, RHEA_MASS, None, RHEA_INITIAL_RAD, RHEACLR, 'Satellite')
    
    # MIRANDA
    global MIRANDA
    MIRANDA = Body('Miranda', URANUS, MIRANDA_DIA, MIRANDA_MASS, None, MIRANDA_INITIAL_RAD, MIRANDACLR, 'Satellite')

    # ARIEL
    global ARIEL
    ARIEL = Body('Ariel', URANUS, ARIEL_DIA, ARIEL_MASS, None, ARIEL_INITIAL_RAD, ARIELCLR, 'Satellite')

    # UMBRIEL
    global UMBRIEL
    UMBRIEL = Body('Umbriel', URANUS, UMBRIEL_DIA, UMBRIEL_MASS, None, UMBRIEL_INITIAL_RAD, UMBRIELCLR, 'Satellite')

    # TITANIA
    global TITANIA
    TITANIA = Body('Titania', URANUS, TITANIA_DIA, TITANIA_MASS, None, TITANIA_INITIAL_RAD, TITANIACLR, 'Satellite')

    # OBERON
    global OBERON
    OBERON = Body('Oberon', URANUS, OBERON_DIA, OBERON_MASS, None, OBERON_INITIAL_RAD, OBERONCLR, 'Satellite')

    # TRITON
    global TRITON
    TRITON = Body('Triton', NEPTUNE, TRITON_DIA, TRITON_MASS, None, TRITON_INITIAL_RAD, TRITONCLR, 'Satellite')

    # CHARON
    global CHARON
    CHARON = Body('Charon', PLUTO, CHARON_DIA, CHARON_MASS, None, CHARON_INITIAL_RAD, CHARONCLR, 'Satellite')
    
    SATELLITES = [MOON, PHOBOS, DEIMOS, IO, EUROPA, GANYMEDE, CALLISTO, TITAN, RHEA, TRITON, MIRANDA, ARIEL, UMBRIEL, TITANIA, OBERON, CHARON]


    global ALL_BODIES
    ALL_BODIES = (SUN, MERCURY, VENUS, EARTH, MOON, MARS, PHOBOS, DEIMOS, CERES, JUPITER, IO, EUROPA, GANYMEDE, CALLISTO, SATURN, TITAN, RHEA, NEPTUNE, TRITON, URANUS, MIRANDA, ARIEL, UMBRIEL, TITANIA, OBERON, PLUTO, CHARON)



# CALLING THE PROGRAM
main()
