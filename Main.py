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

    SOI = True

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

    for body in ALL_BODIES:
        body.display(KM2PIX, Focus, SOI)


# ==================================================
# PHYSICS ENGINE
# Handles:
#   - Updating Velocity and Position of All Stars, Planets, Moons
def PhysicsEngine(TIME_SCALAR):

    for bodyA in ALL_BODIES:

        # ONLY CALCULATE IF :
        #   - IT ORBITS PARENT
        #   - bodyB IS A STAR
        #   GOT RID OF -> IS ON SAME LEVEL AS OTHER CHILDREN <- REQUIREMENT, IS USELESS AND SOI PROVES IT
        for bodyB in ALL_BODIES:
            if bodyB != bodyA and (bodyB.Is == 'Star' or bodyB == bodyA.Parent):
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


    for body in ALL_BODIES:
        body.Position = body.Position + TIME_SCALAR*body.Velocity


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
    


    # DISPLAY
    def display(self, KM2PIX, Focus, SOI):
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

            

 
# ==================================================
# INTIALIZATION METHOD
# Handles:
#   - Creating and Defining Stars, Planets, Moons
#   - Creating Callable lists of Stars, Planets, Moons
def initialize_bodies():
    print()
    print("List of Bodies Created...")

    
    ### CREATING STARS ###
    # BODY REQUIREMENTS: name, parent, dia, mass, vel, pos, color, is
    
    # SUN
    global SUN
    SUN = Body('Sun', None, SUN_DIA, SUN_MASS, 0, 0, YELLOW, 'Star')
    
    #STARS = [SUN]


    ### CREATING PLANETS ###
    # BODY REQUIREMENTS: name, parent, dia, mass, vel, pos, color, is
    global PLANETS
    
    # EARTH
    global EARTH
    EARTH = Body('Earth', SUN, EARTH_DIA, EARTH_MASS, None, EARTH_INITIAL_RAD, BLUE, 'Planet')

    # MARS
    global MARS
    MARS = Body('Mars', SUN, MARS_DIA, MARS_MASS, None, MARS_INITIAL_RAD, RED, 'Planet')

    # MERCURY
    global MERCURY
    MERCURY = Body('Mercury', SUN, MERCURY_DIA, MERCURY_MASS, None, MERCURY_INITIAL_RAD, WHITE, 'Planet')

    # VENUS
    global VENUS
    VENUS = Body('Venus', SUN, VENUS_DIA, VENUS_MASS, None, VENUS_INITIAL_RAD, YELLOW, 'Planet')

    # JUPITER
    global JUPITER
    JUPITER = Body('Jupiter', SUN, JUPITER_DIA, JUPITER_MASS, None, JUPITER_INITIAL_RAD, ORANGE, 'Planet')

    # SATURN
    global SATURN
    SATURN = Body('Saturn', SUN, SATURN_DIA, SATURN_MASS, None, SATURN_INITIAL_RAD, SATURNCLR, 'Planet')
    
    # URANUS
    global URANUS
    URANUS = Body('Uranus', SUN, URANUS_DIA, URANUS_MASS, None, URANUS_INITIAL_RAD, URANUSCLR, 'Planet')
    
    # CERES
    global CERES
    CERES = Body('Ceres', SUN, CERES_DIA, CERES_MASS, None, CERES_INITIAL_RAD, CERESCLR, 'Planet')

    # PLUTO
    global PLUTO
    PluVel = math.sqrt(G*(SUN_MASS**2)/(PLUTO_INITIAL_RAD*(3/2)*(PLUTO_MASS + SUN_MASS)))
    PLUTO = Body('Pluto', SUN, PLUTO_DIA, PLUTO_MASS, PluVel, PLUTO_INITIAL_RAD, PLUTOCLR, 'Planet')

    # NEPTUNE
    global NEPTUNE
    NEPTUNE = Body('Neptune', SUN, NEPTUNE_DIA, NEPTUNE_MASS, None, NEPTUNE_INITIAL_RAD, NEPTUNECLR, 'Planet')

    PLANETS = [MERCURY, VENUS, EARTH, MARS, CERES, JUPITER, SATURN, URANUS, NEPTUNE, PLUTO]


    ### CREATING SATELLITES ###
    # BODY REQUIREMENTS: name, parent, dia, mass, vel, pos, color, is
    global SATELLITES
    
    # MOON
    global MOON
    MOON = Body('Moon', EARTH, MOON_DIA, MOON_MASS, None, MOON_INITIAL_RAD, WHITE, 'Satellite')
    EARTH.addChild(MOON)

    # PHOBOS
    global PHOBOS
    PHOBOS = Body('Phobos', MARS, PHOBOS_DIA, PHOBOS_MASS, None, PHOBOS_INITIAL_RAD, PHOBOSCLR, 'Satellite')
    MARS.addChild(PHOBOS)

    # DEIMOS
    global DEIMOS
    DEIMOS = Body('Deimos', MARS, DEIMOS_DIA, DEIMOS_MASS, None, DEIMOS_INITIAL_RAD, DEIMOSCLR, 'Satellite')
    MARS.addChild(DEIMOS)

    # IO
    global IO
    IO = Body('Io', JUPITER, IO_DIA, IO_MASS, None, IO_INITIAL_RAD, DEIMOSCLR, 'Satellite')
    JUPITER.addChild(IO)

    # EUROPA
    global EUROPA
    EUROPA = Body('Europa', JUPITER, EUROPA_DIA, EUROPA_MASS, None, EUROPA_INITIAL_RAD, EUROPACLR, 'Satellite')
    JUPITER.addChild(EUROPA)

    # GANYMEDE
    global GANYMEDE
    GANYMEDE = Body('Ganymede', JUPITER, GANYMEDE_DIA, GANYMEDE_MASS, None, GANYMEDE_INITIAL_RAD, GANYMEDECLR, 'Satellite')
    JUPITER.addChild(GANYMEDE)
    
    # CALLISTO
    global CALLISTO
    CALLISTO = Body('Callisto', JUPITER, CALLISTO_DIA, CALLISTO_MASS, None, CALLISTO_INITIAL_RAD, CALLISTOCLR, 'Satellite')
    JUPITER.addChild(CALLISTO)

    # TITAN
    global TITAN
    TITAN = Body('Titan', SATURN, TITAN_DIA, TITAN_MASS, None, TITAN_INITIAL_RAD, TITANCLR, 'Satellite')
    SATURN.addChild(TITAN)

    # RHEA
    global RHEA
    RHEA = Body('Rhea', SATURN, RHEA_DIA, RHEA_MASS, None, RHEA_INITIAL_RAD, RHEACLR, 'Satellite')
    SATURN.addChild(RHEA)
    
    # MIRANDA
    global MIRANDA
    MIRANDA = Body('Miranda', URANUS, MIRANDA_DIA, MIRANDA_MASS, None, MIRANDA_INITIAL_RAD, MIRANDACLR, 'Satellite')
    URANUS.addChild(MIRANDA)

    # ARIEL
    global ARIEL
    ARIEL = Body('Ariel', URANUS, ARIEL_DIA, ARIEL_MASS, None, ARIEL_INITIAL_RAD, ARIELCLR, 'Satellite')
    URANUS.addChild(ARIEL)

    # UMBRIEL
    global UMBRIEL
    UMBRIEL = Body('Umbriel', URANUS, UMBRIEL_DIA, UMBRIEL_MASS, None, UMBRIEL_INITIAL_RAD, UMBRIELCLR, 'Satellite')
    URANUS.addChild(UMBRIEL)

    # TITANIA
    global TITANIA
    TITANIA = Body('Titania', URANUS, TITANIA_DIA, TITANIA_MASS, None, TITANIA_INITIAL_RAD, TITANIACLR, 'Satellite')
    URANUS.addChild(TITANIA)

    # OBERON
    global OBERON
    OBERON = Body('Oberon', URANUS, OBERON_DIA, OBERON_MASS, None, OBERON_INITIAL_RAD, OBERONCLR, 'Satellite')
    URANUS.addChild(OBERON)

    # TRITON
    global TRITON
    TRITON = Body('Triton', NEPTUNE, TRITON_DIA, TRITON_MASS, None, TRITON_INITIAL_RAD, TRITONCLR, 'Satellite')
    NEPTUNE.addChild(TRITON)

    # CHARON
    global CHARON
    CHARON = Body('Charon', PLUTO, CHARON_DIA, CHARON_MASS, None, CHARON_INITIAL_RAD, CHARONCLR, 'Satellite')
    PLUTO.addChild(CHARON)
    
    SATELLITES = [MOON, PHOBOS, DEIMOS, IO, EUROPA, GANYMEDE, CALLISTO, TITAN, RHEA, TRITON, MIRANDA, ARIEL, UMBRIEL, TITANIA, OBERON, CHARON]


    global ALL_BODIES
    ALL_BODIES = (SUN, MERCURY, VENUS, EARTH, MOON, MARS, PHOBOS, DEIMOS, CERES, JUPITER, IO, EUROPA, GANYMEDE, CALLISTO, SATURN, TITAN, RHEA, NEPTUNE, TRITON, URANUS, MIRANDA, ARIEL, UMBRIEL, TITANIA, OBERON, PLUTO, CHARON)



# CALLING THE PROGRAM
main()
