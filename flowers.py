import platform
import pygame
import time
import random
import math

class Game:
    def __init__(self, game_width=None, game_height=None, hideBorder=True):
        borderConfig = 0
        if hideBorder:
            borderConfig = pygame.NOFRAME
        if game_width is None:
            infoObject = pygame.display.Info()
            self.game_width = infoObject.current_w
            self.game_height = infoObject.current_h
        else:
            self.game_width = game_width
            self.game_height = game_height
        
        if platform.system().startswith("Win"):
            import win32api
            import win32con
            import win32gui
            
            self.background = (255, 0, 128)
            # Create layered window
            self.gameDisplay = pygame.display.set_mode((self.game_width,self.game_height), borderConfig)
            hwnd = pygame.display.get_wm_info()["window"]
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            # Set window transparency color
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.background), 0, win32con.LWA_COLORKEY)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        else:
            self.gameDisplay = pygame.display.set_mode((self.game_width,self.game_height), borderConfig)
            self.background = (0, 0, 0)
        self.gameDisplay.fill(self.background)
        pygame.display.update()
        self.gameTime = 50
        self.bugTicks = 5
        self.quit = False
        self.flowers = []
        self.bugs = []
        self.flowersPerSquare = 1
        self.xSquares = 30
        self.ySquares = 20
        self.squareGrid = [[self.flowersPerSquare]*(self.ySquares) for _ in range(self.xSquares)]
    def reset(self):
        self.squareGrid = [[self.flowersPerSquare]*(self.ySquares) for _ in range(self.xSquares)]
        self.flowers = []
        self.bugs = []
        self.gameDisplay.fill(self.background)

    def addFlower(self, flower):
        x = math.floor((flower.x/self.game_width)*self.xSquares)
        y = math.floor((flower.y/self.game_height)*self.ySquares)
        if(self.squareGrid[x][y]>0):
            self.squareGrid[x][y]-=1
            self.flowers.append(flower)
    
    def addBug(self, bug):
        self.bugs.append(bug)
    
    def removeFlower(self, flower):
        x = math.floor((flower.x/self.game_width)*self.xSquares)
        y = math.floor((flower.y/self.game_height)*self.ySquares)
        self.squareGrid[x][y]+=1
        self.flowers.remove(flower)

    def displayFlowers(self):
        for flower in self.flowers:
           pygame.draw.circle(self.gameDisplay, flower.color, (flower.x, flower.y), flower.age+1, 1)

    def displayBug(self, bug):
        pygame.draw.circle(self.gameDisplay, self.background, (bug.x, bug.y), bug.size+2, 0)        
        pygame.draw.circle(self.gameDisplay, bug.color, (bug.x, bug.y), bug.size, 0)        
        # pygame.draw.circle(self.gameDisplay, bug.color, (bug.x, bug.y, bug.size, bug.size))
    def growFlowers(self):
        for flower in self.flowers:
           flower.grow(self)

    def numFlowers(self):
        # score_font = pygame.font.SysFont("comicsansms", 35)
        # value = score_font.render("Flowers: " + str(len(self.flowers)), True, (255,128,10))
        pygame.display.set_caption(str(len(self.flowers))+" Flowers by bytewoofer")
        # self.gameDisplay.blit(value, [0,0])

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_r:
                    self.reset()
            if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        self.displayFlowers()
        self.growFlowers()
        self.numFlowers()
        
        for i in range(0,self.bugTicks):
            self.actBugs()
            self.displayBugs()
            self.checkBugsCollide()

        pygame.display.update()
        pygame.time.wait(self.gameTime)
    def checkBugsCollide(self):
        for bug in self.bugs:
            self.checkBugOnFlower(bug)

    def checkCollision(self, collider, collidee):
        if collider.x<=collidee.x and collider.x+collider.size>=collidee.x:
            if collider.y<=collidee.y and collider.y+collider.size>=collidee.y:
                return True
        return False

    def checkBugOnFlower(self, bug):
        for flower in self.flowers:
            if self.checkCollision(bug,flower):
                bug.ateFlower(self, flower)
                flower.die(self)
    def actBugs(self):
        for bug in self.bugs:
            bug.act(self)

    def displayBugs(self):
        for bug in self.bugs:
            self.displayBug(bug)
class Bug(object):
    def __init__(self, game, parent = None):
        if parent is None:
            self.x = int(game.game_width/5)
            self.y = int(game.game_height/5)
            self.size = 26
            self.age = 0
            self.lifespan = 150
            self.energy = 500
            self.maxEnergy = 1000
            self.color = (0,0,0)
            self.targetFlower = None
        else:
            self.x = parent.x+10
            self.y = parent.y+10
            self.size = 26
            self.age = 0
            self.lifespan = parent.lifespan+random.randint(-1,1)
            self.energy = 500
            self.maxEnergy = parent.maxEnergy
            self.color = parent.color
            self.targetFlower = None

    def reproduce(self, game):
        game.bugs.append(Bug(game, self))
    def ateFlower(self, game, flower):
        self.targetFlower = None
        self.color = ((self.color[0]*3+flower.color[0])/4,(self.color[1]*3+flower.color[1])/4,(self.color[2]*3+flower.color[2])/4,)
        self.energy+=flower.age+50
        if(self.energy>self.maxEnergy):
            self.reproduce(game)
            self.energy=self.maxEnergy/2

    def die(self, game):
        game.bugs.remove(self)

    def findNearestFlower(self, game):
        nearestFlower = None
        flowerDist = None
        flower = None
        for flower in game.flowers:
            lenX = abs(flower.x-self.x)
            lenY = abs(flower.y-self.y)
            dist = math.sqrt(lenX*lenX+lenY*lenY)
            if(flowerDist == None or dist<flowerDist):
                nearestFlower = flower
                flowerDist = dist
        return nearestFlower

    def act(self, game):
        self.size=int(self.energy/10)
        if self.targetFlower == None and len(game.flowers)>0 or not (self.targetFlower in game.flowers):
            self.targetFlower = self.findNearestFlower(game)
        if(self.targetFlower != None):
            self.moveTowardsFlower(game, self.targetFlower)
        if(self.energy <= 0):
            self.die(game)
    
    def moveTowardsFlower(self, game, targetFlower):
        moveX = self.x-targetFlower.x
        moveY = self.y-targetFlower.y
        if(moveY>=0):
            self.y-=1
        if(moveY<=0):
            self.y+=1
        if(moveX>=0):
            self.x-=1
        if(moveX<=0):
            self.x+=1
        self.energy-=1

class Flower(object):
    def __init__(self, game, parent = None):
        if parent is None:
            self.x = 0.5 * game.game_width
            self.y = 0.5 * game.game_height
            self.age = 0
            self.life_span = random.randint(1,31)
            self.spread_distance = 31
            self.children = random.randint(1,31)
            self.years_to_maturity = 1
            self.color = ((self.lifeLeft()*self.life_span)%255, (self.lifeLeft()*self.spread_distance)%255, (self.lifeLeft()*self.children)%255)
        else:
            self.x = random.randint(-parent.spread_distance,parent.spread_distance)+parent.x
            self.y = random.randint(-parent.spread_distance,parent.spread_distance)+parent.y
            self.age = 0
            self.life_span = parent.life_span+random.randint(-1,1)
            self.spread_distance = parent.spread_distance+random.randint(-1,1)
            self.children = (parent.children+random.randint(-1,1))
            self.years_to_maturity = parent.years_to_maturity+random.randint(-1,1)
            self.color = ((self.lifeLeft()*self.life_span)%255, (self.lifeLeft()*self.spread_distance)%255, (self.lifeLeft()*self.children)%255)
            if(self.isValid(game)):
                game.addFlower(self)            

    def plant(self, parent, game):
        self.x = random.randint(-parent.spread_distance,parent.spread_distance)+parent.x
        self.y = random.randint(-parent.spread_distance,parent.spread_distance)+parent.y
        self.age = 0
        self.life_span = parent.life_span+random.randint(-1,1)
        self.spread_distance = parent.spread_distance+random.randint(-1,1)
        self.children = (parent.children+random.randint(-1,1))
        self.years_to_maturity = parent.years_to_maturity+random.randint(-1,1)
        self.color = ((self.lifeLeft()*self.life_span)%255, (self.lifeLeft()*self.spread_distance)%255, (self.lifeLeft()*self.children)%255)
        if(self.isValid(game)):
           game.addFlower(self)

    def lifeLeft(self):
        if(self.life_span==0):
            return 8
        return (((self.age/self.life_span)*7)+1)

    def isValid(self, game):
        return (self.x<game.game_width and self.x>0
        and self.y<game.game_height and self.y>0
        and self.life_span > 0 and self.life_span < 31
        and self.spread_distance > 0 and self.spread_distance < 31
        and self.children >= 0 and self.children < 31
        and self.years_to_maturity > 0)


    def grow(self, game):
        self.age += 1
        self.color = ((self.lifeLeft()*self.life_span)%255, (self.lifeLeft()*self.spread_distance)%255, (self.lifeLeft()*self.children)%255)
        if self.age % self.years_to_maturity == 0:
            self.spread(game)
        if self.age > self.life_span:
            self.die(game)
    
    def spread(self, game):
        for child in range(1,int(self.children)):
            newFlower = Flower(game, self)
            # newFlower.plant(self, game)

    def die(self, game):
        game.removeFlower(self)

def run():
    pygame.init()
    game = Game()#800,800, False)
    while not game.quit:
        game.tick()
        if(len(game.flowers)<1 or len(game.bugs)<1):
                game.reset()
                game.addFlower(Flower(game))
                game.addBug(Bug(game))

run()
