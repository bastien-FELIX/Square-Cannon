import os
from ion import *
from math import pi, cos, sin
from time import sleep
from random import randint

try:
  import os
  if hasattr(os, "environ"):
    os.environ['KANDINSKY_ZOOM_RATIO'] = "4"
    os.environ['KANDINSKY_OS_MODE'] = "0"
except: pass
from kandinsky import *

# created on 25/03/2024 by overbleed
# credits to the people who ported ion and kandinsky to pc

SKY_COLOR = (110, 210, 250)
ROCK_COLOR = (140, 140, 140)

TURRET_CENTER_1 = [30, 135]
TURRET_CENTER_2 = [290, 135]
MAX_SCORE = 3
DEFAULT_CANNON_VELOCITY = 50
MAX_WIND_FORCE = 7

score1, score2 = 0, 0
cannonVelocity = DEFAULT_CANNON_VELOCITY
cannonAngle = pi/5
windForce = 7
turretChosen = []
for i in range (2):
    turretChosen.append(TURRET_CENTER_1[i])

class Square:
    def __init__(self, x, y, teta, l):
        self.x0 = x
        self.y0 = y
        self.teta0 = teta
        self.length = l

    def show(self, color=(0,0,0), inside=False, insideColor=(255,255,255)):
        drawLine(self.x0, self.y0, self.teta0, self.length)
        x1 = round(cos(self.teta0)*self.length) + self.x0
        y1 = -round(sin(self.teta0)*self.length) + self.y0
        teta1 = self.teta0 - pi/2

        for i in range(3):
            drawLine(x1, y1, teta1, self.length, color)
            x1 = round(cos(teta1)*self.length) + x1
            y1 = -round(sin(teta1)*self.length) + y1
            teta1 -= pi/2
        
        if inside:
            fill_rect(self.x0+1, self.y0+1, self.length-1, self.length-1, insideColor)
    
    def center(self):
        x = self.x0 + self.length/2
        y = self.y0 + self.length/2
        return(x, y)

def drawLine(x, y, angle, length, color="black"):
    length -= 1

    while length >= 0:
        a = round(cos(angle)*length) + x
        b = -round(sin(angle)*length) + y

        set_pixel(a, b, color)

        length -= 1

def drawArrow(x0, y0, teta, length):
    drawLine(x0, y0, teta, length)
    x1 = round(cos(teta)*length) + x0
    y1= -round(sin(teta)*length) + y0
    drawLine(x1, y1, teta+3*pi/4, length/10)
    drawLine(x1, y1, teta-3*pi/4, length/10)

def drawScreen():
    fill_rect(0, 0, 320, 140, SKY_COLOR)
    fill_rect(60, 140, 200, 100, SKY_COLOR)

    for i in range (2):
        fill_rect(0 + 260*i, 140, 60, 100, ROCK_COLOR)
        drawLine(0 + 260*i, 140, 0, 60)
        drawLine(59 + 201*i, 140, -pi/2, 100)
    
    turret1.show((0,0,0), True)
    turret2.show((0,0,0), True)

    draw_string(str(score1), 0, 0, "black", SKY_COLOR)
    draw_string(str(score2), 310, 0, "black", SKY_COLOR)
    showWindDirection()

def parabolicMovement(x0, y0, v0, angle0, show=False, length=300, color=(0,0,0), gravity=9.81):
    for i in range (length):
        x = (v0 * cos(angle0)) * (i*0.1) + x0
        y = 1/2 * gravity * (i*0.1)**2 + (v0 * -sin(angle0))*(i*0.1) + y0

        if show: set_pixel(round(x), round(y), color)
    return(round(x), round(y))

def windEffect(force, l):
    for i in range (l):
        x = 0.5*force*(i*0.1)**2
    return(round(x))

def showWindDirection():
    if windForce > 0: drawArrow(135, 20, 0, 50)
    elif windForce < 0: drawArrow(185, 20, pi, 50)
    else: pass

def aiming():
    global cannonVelocity, cannonAngle
    global turretChosen
    
    if keydown(KEY_PLUS) and cannonVelocity < 75:
        cannonVelocity += 1
        drawScreen()
    if keydown(KEY_MINUS) and cannonVelocity > 0:
        cannonVelocity -= 1
        drawScreen()
    if keydown(KEY_RIGHT):
        cannonAngle -= pi/120
        drawScreen()
    if keydown(KEY_LEFT):
        cannonAngle += pi/120
        drawScreen()
        
    drawArrow(turretChosen[0], turretChosen[1], cannonAngle, cannonVelocity*0.75)

    if keydown(KEY_OK):
        firing()

def firing():
    global cannonAngle, cannonVelocity

    for i in range(1, 250):
        cannonBall.x0 = parabolicMovement(turretChosen[0], turretChosen[1], cannonVelocity, cannonAngle, False, i)[0] + windEffect(windForce, i)
        cannonBall.y0 = parabolicMovement(turretChosen[0], turretChosen[1], cannonVelocity, cannonAngle, False, i)[1]
        # drawScreen()
        cannonBall.show((0,0,0), True, (0, 0, 0))
        sleep(0.01)
        if checkCollisions():
            drawScreen()
            break

    if turretChosen == TURRET_CENTER_1:
        turretChosen[0] = TURRET_CENTER_2[0]
        turretChosen[1] = TURRET_CENTER_2[1]
        cannonAngle = 4*pi/5
    elif turretChosen == TURRET_CENTER_2: 
        turretChosen[0] = TURRET_CENTER_1[0]
        turretChosen[1] = TURRET_CENTER_1[1]
        cannonAngle = pi/5
    
    cannonVelocity = DEFAULT_CANNON_VELOCITY

def checkCollisions():
    global score1, score2, windForce
    if turretChosen == TURRET_CENTER_1: #when first turret is selected (won't kill yourself)
        if cannonBall.center()[0] < (turret2.x0 + turret2.length) and cannonBall.center()[0] > turret2.x0:
            if cannonBall.center()[1] < (turret2.y0 + turret2.length) and cannonBall.center()[1] > turret2.y0:
                score1 += 1
                windForce = randint(-MAX_WIND_FORCE, MAX_WIND_FORCE)
                return (True)
    else:
        if cannonBall.center()[0] < (turret1.x0 + turret1.length) and cannonBall.center()[0] > turret1.x0:
            if cannonBall.center()[1] < (turret1.y0 + turret1.length) and cannonBall.center()[1] > turret1.y0:
                score2 += 1
                windForce = randint(-MAX_WIND_FORCE, MAX_WIND_FORCE)
                return (True)
            
    #with screen
    if cannonBall.center()[0] > 325 or cannonBall.center()[0] < 0 or cannonBall.center()[1] > 220: return (True)
    
    #with rocks
    if cannonBall.center()[1] > 140:
        if cannonBall.center()[0] < 63: return(True)
        if cannonBall.center()[0] > 257: return(True)

turret1 = Square(25, 130, 0, 10)
turret2 = Square(285, 130, 0, 10)
cannonBall = Square(0, 0, 0, 3)

drawScreen()

while 1:
    aiming()
    if score1 == MAX_SCORE or score2 == MAX_SCORE:
        break

if score1 == MAX_SCORE:
    draw_string("P1 WINS", 125, 20, "black", SKY_COLOR)
else: draw_string("P2 WINS", 125, 20, "black", SKY_COLOR)