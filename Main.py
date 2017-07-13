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

    SOI = False

    KM2PIX = 1 #actually Megameters to Pixels
    
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
                
                # ZOOM INPUT
                if event.key == K_SLASH:
                    if KM2PIX >= 1:
                        KM2PIX *= 2
                    else:
                        KM2PIX *= 10
                elif event.key == K_PERIOD:
                    if KM2PIX <= 1:
                        KM2PIX /= 10
                    else:
                        KM2PIX /= 2
                    
                # TIME_SCALAR KEY INPUT
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

                # MAP / FOCUS KEY INPUT
                
                    


        ### RUNNING PHYSICS ENGINE ###
        
        # BASIC LOOP, FOR WHEN SIM IS BETWEEN 1SEC AND 60SEC
        if BASIC_LOOP > 1 and BASIC_LOOP_COUNTER >= 1 and GOD_LOOP == 1:
            if BASIC_LOOP_COUNTER == BASIC_LOOP:
                PhysicsEngine(TIME_SCALAR)
            elif BASIC_LOOP_COUNTER == 60:
                BASIC_LOOP_COUNTER = 1
            else:
                BASIC_LOOP_COUNTER += 1

        # GOD MODE
        elif GOD_LOOP > 1:
            print('GOD MODE ENGAGED')
            for x in range(0, GOD_LOOP):
                PhysicsEngine(TIME_SCALAR)

        # LINEAR SCALE
        elif ACTUAL_SCALAR != TIME_SCALAR:
            if ACTUAL_SCALAR == 0 and TIME_SCALAR == 1:
                PhysicsEngine(TIME_SCALAR)
            elif ACTUAL_SCALAR > TIME_SCALAR:
                ACTUAL_SCALAR -= 10
            else:
                ACTUAL_SCALAR += 10
            PhysicsEngine(ACTUAL_SCALAR)
        
        else:
            #print('IS THIS REALLY RUNNING?')
            PhysicsEngine(TIME_SCALAR)
        
        
        # FOCUS ON...
        FocusBody = MARS
        Focus = FocusBody.Position

        # RENDERING OBJECTS
        DISPLAYSURF.fill(BGCOLOR)
        Renderer(KM2PIX, Focus, SOI)
        Sim_Speed = TIME_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP) if ACTUAL_SCALAR == 0 else ACTUAL_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP)
        GUI(Sim_Speed, FocusBody, KM2PIX, FPSCLOCK)
        pygame.display.update()
        
        # IF NOT GOING THROUGH THE LINEAR SCALE, STICK TO 60 FPS LIMIT
        if ACTUAL_SCALAR != TIME_SCALAR or ACTUAL_SCALAR == 0:
            FPSCLOCK.tick(FPS)



# ==================================================
# GUI
# Handles:
#   - Displaying list of bodies in system
#   - Displaying current focus point
#   - Displaying TIME_SCALAR
def GUI(Sim_Speed, FocusBody, KM2PIX, FPSCLOCK):
    # SETTING UP FONT
    path = os.path.abspath('C:/Users/Suleyman/Documents/3S/Cubellan_v_0_7/Cubellan.ttf')
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
    scale = 10**3/KM2PIX
    temp = 'Scale: 1/%i' %scale
    ScaleText = BasicFont.render(temp, True, WHITE)
    DISPLAYSURF.blit(ScaleText, (12, 36))

    # UPS/FPS DISPLAY TEXT
    if FPSCLOCK.get_time() > 0:
        #UPS = int(1000/FPSCLOCK.get_time())
        #temp = 'UPS: %s' %UPS
        FPS = int(FPSCLOCK.get_fps())
        temp = 'FPS: %s' %FPS
        UPSText = BasicFont.render(temp, True, WHITE)
        DISPLAYSURF.blit(UPSText, (12, 48))
    else:
        UPSText = BasicFont.render('TOO FAST', True, WHITE)
        DISPLAYSURF.blit(UPSText, (12, 48))


    # RETICLE
    radius = int(round(FocusBody.Diameter*KM2PIX/2) + 5)
    pygame.draw.circle(DISPLAYSURF, WHITE, (round(SURF_WIDTH/2), round(SURF_HEIGHT/2)), radius, 1)
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
            pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(MiddlePoint[1] + SURF_HEIGHT/2)), int(KM2PIX*round(self.Diameter/2)), 0)


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
    
    #STARS = (SUN)


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
    
    PLANETS = (EARTH, MARS, MERCURY, VENUS, JUPITER, SATURN)


    ### CREATING SATELLITES ###
    #(name, orbits, dia, mass, theta, vel, pos, color)
    global SATELLITES
    
    # MOON
    global MOON
    MoonVel = math.sqrt(G*(EARTH_MASS**2)/(MOON_INITIAL_RAD*(MOON_MASS + EARTH_MASS)))
    MOON = Satellite()
    MOON.define('Moon', EARTH, MOON_DIA, np.array([MOON_MASS], dtype = np.float64), 0, np.array([0,MoonVel], dtype = np.float64) + EARTH.Velocity, np.array([MOON_INITIAL_RAD,0], dtype = np.float64) + EARTH.Position, WHITE)

    # PHOBOS
    global PHOBOS
    PhobVel = math.sqrt(G*(MARS_MASS**2)/(PHOBOS_INITIAL_RAD*(PHOBOS_MASS + MARS_MASS)))
    PHOBOS = Satellite()
    PHOBOS.define('Phobos', MARS, PHOBOS_DIA, np.array([PHOBOS_MASS], dtype = np.float64), 0, np.array([0,PhobVel], dtype = np.float64) + MARS.Velocity, np.array([PHOBOS_INITIAL_RAD,0], dtype = np.float64) + MARS.Position, PHOBOSCLR)

    # DEIMOS
    global DEIMOS
    DeimVel = math.sqrt(G*(MARS_MASS**2)/(DEIMOS_INITIAL_RAD*(DEIMOS_MASS + MARS_MASS)))
    DEIMOS = Satellite()
    DEIMOS.define('Deimos', MARS, DEIMOS_DIA, np.array([DEIMOS_MASS], dtype = np.float64), 0, np.array([0,DeimVel], dtype = np.float64) + MARS.Velocity, np.array([DEIMOS_INITIAL_RAD,0], dtype = np.float64) + MARS.Position, DEIMOSCLR)

    # IO
    global IO
    IoVel = math.sqrt(G*(JUPITER_MASS**2)/(IO_INITIAL_RAD*(IO_MASS + JUPITER_MASS)))
    IO = Satellite()
    IO.define('Io', JUPITER, IO_DIA, np.array([IO_MASS], dtype = np.float64), 0, np.array([0,IoVel], dtype = np.float64) + JUPITER.Velocity, np.array([IO_INITIAL_RAD,0], dtype = np.float64) + JUPITER.Position, DEIMOSCLR)

    # EUROPA
    global EUROPA
    EuroVel = math.sqrt(G*(JUPITER_MASS**2)/(EUROPA_INITIAL_RAD*(EUROPA_MASS + JUPITER_MASS)))
    EUROPA = Satellite()
    EUROPA.define('Europa', JUPITER, EUROPA_DIA, np.array([EUROPA_MASS], dtype = np.float64), 0, np.array([0,EuroVel], dtype = np.float64) + JUPITER.Velocity, np.array([EUROPA_INITIAL_RAD,0], dtype = np.float64) + JUPITER.Position, EUROPACLR)

    # GANYMEDE
    global GANYMEDE
    GanyVel = math.sqrt(G*(JUPITER_MASS**2)/(GANYMEDE_INITIAL_RAD*(GANYMEDE_MASS + JUPITER_MASS)))
    GANYMEDE = Satellite()
    GANYMEDE.define('Ganymede', JUPITER, GANYMEDE_DIA, np.array([GANYMEDE_MASS], dtype = np.float64), 0, np.array([0,GanyVel], dtype = np.float64) + JUPITER.Velocity, np.array([GANYMEDE_INITIAL_RAD,0], dtype = np.float64) + JUPITER.Position, GANYMEDECLR)
    
    # CALLISTO
    global CALLISTO
    CalVel = math.sqrt(G*(JUPITER_MASS**2)/(CALLISTO_INITIAL_RAD*(CALLISTO_MASS + JUPITER_MASS)))
    CALLISTO = Satellite()
    CALLISTO.define('Callisto', JUPITER, CALLISTO_DIA, np.array([CALLISTO_MASS], dtype = np.float64), 0, np.array([0,CalVel], dtype = np.float64) + JUPITER.Velocity, np.array([CALLISTO_INITIAL_RAD,0], dtype = np.float64) + JUPITER.Position, CALLISTOCLR)

    # TITAN
    global TITAN
    TitVel = math.sqrt(G*(SATURN_MASS**2)/(TITAN_INITIAL_RAD*(TITAN_MASS + SATURN_MASS)))
    TITAN = Satellite()
    TITAN.define('Titan', SATURN, TITAN_DIA, np.array([TITAN_MASS], dtype = np.float64), 0, np.array([0,TitVel], dtype = np.float64) + SATURN.Velocity, np.array([TITAN_INITIAL_RAD,0], dtype = np.float64) + SATURN.Position, TITANCLR)

    # RHEA
    global RHEA
    ReVel = math.sqrt(G*(SATURN_MASS**2)/(RHEA_INITIAL_RAD*(RHEA_MASS + SATURN_MASS)))
    RHEA = Satellite()
    RHEA.define('Rhea', SATURN, RHEA_DIA, np.array([RHEA_MASS], dtype = np.float64), 0, np.array([0,ReVel], dtype = np.float64) + SATURN.Velocity, np.array([RHEA_INITIAL_RAD,0], dtype = np.float64) + SATURN.Position, RHEACLR)
    
    SATELLITES = (MOON, PHOBOS, DEIMOS, IO, EUROPA, GANYMEDE, CALLISTO, TITAN, RHEA)


    global ALL_BODIES
    ALL_BODIES = (SUN, MERCURY, VENUS, EARTH, MOON, MARS, PHOBOS, DEIMOS, JUPITER, IO, EUROPA, GANYMEDE, CALLISTO, SATURN, TITAN, RHEA)


# CALLING THE PROGRAM
main()
