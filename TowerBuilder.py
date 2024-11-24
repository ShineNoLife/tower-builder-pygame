import pygame
import sys
import random
import time

pygame.init()

width = 600
height = 800
pygame.display.set_caption('Simple Stacking Game')
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

colorIndex = 0

brickH = 50
brickW = 120
score = 0
highScore = 0
speed = 3
startingHeight = height / 3
textColor = (1, 120, 1)

#time limit of a game
timeLimit = 10
start_time = 0

#game music
hasMusic = True
gameMusic = "containerTowerAssets/chill_music.mp3"
musicVolume = 0.1

#containers image
image_paths = ["containerTowerAssets/blue_container.jpg",
               "containerTowerAssets/grey_container.jpg",
               "containerTowerAssets/orange_container.jpg",
               "containerTowerAssets/green_container.jpg"]

unscaledContainers = []
for i in range(len(image_paths)):
    unscaledContainers.append(pygame.image.load(image_paths[i]).convert_alpha())

containers = []
for image in unscaledContainers:
    containers.append(pygame.transform.scale(image, (brickW, brickH)))

#background image
backgroundImage = "C:/Users/Shine/Downloads/containerTowerAssets/blue_sky.jpg"
backgroundImage = pygame.image.load(backgroundImage).convert_alpha()
backgroundImage = pygame.transform.scale(backgroundImage, (width, height))









class Brick:
    def __init__(self, x, y, speed, isRandom):
        self.imageIndex = random.randint(0, len(containers) - 1)
        if isRandom:
            self.x = random.uniform(0, width - brickW)
        else:
            self.x = x

        self.y = y
        self.w = brickW
        self.h = brickH
        self.speed = speed

    def draw(self):
        display.blit(containers[self.imageIndex], (self.x, self.y))
        # pygame.draw.rect(display, self.color, (self.x, self.y, self.w, self.h))

    def move(self):
        if self.x + brickW + self.speed > width:
            self.speed *= -1
        elif self.x + self.speed < 0:
            self.speed *= -1
        self.x += self.speed

def gameOver(message):
    global highScore
    highScore = max(score, highScore)
    loop = True

    font = pygame.font.SysFont("ARIAL", 60)
    text = font.render(message, True, textColor)

    textRect = text.get_rect()
    textRect.center = (width/2, height/2 - 80)

    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
                if event.key == pygame.K_r:
                    gameLoop()
            if event.type == pygame.MOUSEBUTTONDOWN:
                gameLoop()
        display.blit(text, textRect)
        
        pygame.display.update()
        clock.tick()


def showScore():
    font = pygame.font.SysFont("ARIAL", 30)
    text = font.render(f"Score: {score}", True, textColor)
    display.blit(text, (10, 10))

    text = font.render(f"High Score: {highScore}", True, textColor)
    display.blit(text, (width - 190, 10))

    text = font.render(f"Time Left: {int(start_time + timeLimit - time.time()):d}", True, textColor)
    display.blit(text, (10, 50))


def close():
    pygame.quit()
    sys.exit()

def intersect(blockL, blockR):
    l, r = blockL.x, blockL.x + brickW
    a, b = blockR.x, blockR.x + brickW

    if (l > a):
        l, a = a, l
        r, b = b, r

    return a <= r


def updateFrame(currentBrick):
    display.blit(backgroundImage, (0, 0))
    currentBrick.draw()

    for brick in brickList:
        brick.draw()
    
    showScore()
    pygame.display.update()

def gameLoop():
    global brickW, brickH, score, highScore, colorIndex, speed
    global hasMusic, gameMusic, musicVolume, start_time
    global brickList, startingHeight
    loop = True

    colorIndex = 0
    speed = 3

    score = 0

    newBrick = Brick(width, startingHeight, speed, True)
    brickList = []
    brickList.append(Brick(width / 2 - brickW / 2, height - brickH, speed, False))
    updateFrame(newBrick)
        
    start_time = time.time()
    while loop:
        if (time.time() - start_time > timeLimit):
            gameOver("Time Over! :(")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()


                if event.key == pygame.K_SPACE:
                    #make the brick fall
                    while newBrick.y + brickH <= brickList[-1].y:
                        newBrick.y += 1
                        updateFrame(newBrick)

                    if not (intersect(newBrick, brickList[-1])):
                        gameOver("You Failed!")
                    
                    score += 1
                    if (score % 3 == 0 and speed + 1 <= 9):
                        speed += 1

                    brickList.append(newBrick)

                    #tower to high, remove 1 brick below
                    if (height / 2 + 2 * brickH > brickList[-1].y):
                        brickList = brickList[1:]
                        for brick in brickList:
                            brick.y += brickH

                    newBrick = Brick(width, startingHeight, speed, True)
        

        newBrick.move()
        updateFrame(newBrick)
        clock.tick(60)

def startGame():
    global hasMusic, gameMusic, musicVolume

    if (hasMusic):
        sound = pygame.mixer.Sound(gameMusic)
        sound.set_volume(musicVolume)
        sound.play(loops=-1)

    gameLoop()

startGame()


