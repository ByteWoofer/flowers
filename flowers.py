import platform
import pygame
import time
import random
import math




class Game:
    def __init__(self, game_width=None, game_height=None):
        if game_width is None:
            infoObject = pygame.display.Info()
            self.game_width = infoObject.current_w
            self.game_height = infoObject.current_h
        else:
            self.game_width = game_width
            self.game_height = game_height
        self.gameDisplay = pygame.display.set_mode((self.game_width,self.game_height), pygame.NOFRAME)
        if platform.system().startswith("Win"):
            import win32api
            import win32con
            import win32gui
            self.background = (255, 0, 128)
            # Create layered window
            hwnd = pygame.display.get_wm_info()["window"]
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            # Set window transparency color
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
        else:
            self.background = (255, 0, 128)
        self.gameTime = 33
        self.quit = False
        self.flowers = []
        self.flowersPerSquare = 1
        self.xSquares = 25
        self.ySquares = 25
        self.squareGrid = [[self.flowersPerSquare]*(self.ySquares) for _ in range(self.xSquares)]
    def reset(self):
        self.squareGrid = [[self.flowersPerSquare]*(self.ySquares) for _ in range(self.xSquares)]
        self.flowers = []
        self.gameDisplay.fill(self.background)

    def addFlower(self, flower):
        x = math.floor((flower.x/self.game_width)*self.xSquares)
        y = math.floor((flower.y/self.game_height)*self.ySquares)
        if(self.squareGrid[x][y]>0):
            self.squareGrid[x][y]-=1
            self.flowers.append(flower)
    
    def removeFlower(self, flower):
        x = math.floor((flower.x/self.game_width)*self.xSquares)
        y = math.floor((flower.y/self.game_height)*self.ySquares)
        self.squareGrid[x][y]+=1
        self.flowers.remove(flower)

    def displayFlowers(self):
        for flower in self.flowers:
           pygame.draw.circle(self.gameDisplay, flower.color, (flower.x, flower.y), flower.age+1, 1)

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

        pygame.display.update()
        pygame.time.wait(self.gameTime)

class Flower(object):
    def __init__(self, game, parent = None):
        if parent is None:
            self.x = 0.5 * game.game_width
            self.y = 0.5 * game.game_height
            self.age = 0
            self.life_span = random.randint(1,31)
            self.spread_distance = 20
            self.children = random.randint(1,31)
            self.years_to_maturity = random.randint(1,31)
            self.color = ((8*self.life_span)%255, (8*self.spread_distance)%255, (8*self.children)%255)
        else:
            self.x = random.randint(-parent.spread_distance,parent.spread_distance)+parent.x
            self.y = random.randint(-parent.spread_distance,parent.spread_distance)+parent.y
            self.age = 0
            self.life_span = parent.life_span+random.randint(-1,1)
            self.spread_distance = parent.spread_distance+random.randint(-1,1)
            self.children = (parent.children+random.randint(-1,1))
            self.years_to_maturity = parent.years_to_maturity+random.randint(-1,1)
            self.color = ((8*self.life_span)%255, (8*self.spread_distance)%255, (8*self.children)%255)
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
        self.color = ((8*self.life_span)%255, (8*self.spread_distance)%255, (8*self.children)%255)
        if(self.isValid(game)):
           game.addFlower(self)

    def isValid(self, game):
        return (self.x<game.game_width and self.x>0
        and self.y<game.game_height and self.y>0
        and self.life_span > 0 and self.life_span < 31
        and self.spread_distance > 0 and self.spread_distance < 31
        and self.children >= 0 and self.children < 31
        and self.years_to_maturity > 0)


    def grow(self, game):
        self.age += 1
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
    game = Game()
    while not game.quit:
        game.tick()
        if(len(game.flowers)<1):
                game.reset()
                game.addFlower(Flower(game))

run()