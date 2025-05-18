import pygame
import sys
import random
import time
import pygame_menu as pm
import pygame_widgets as pw
from pygame_widgets.slider import Slider

width = 600
height = 800

colorIndex = 0

brickH = 50
brickW = 120
score = 0
highScore = 0
speed = 5
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
containers = []
backgroundImage = None
display = None
clock = None
loop = True
newBrick = None
brickList = []
extra = 0
sound = None



def load_args():
    """
    Load the game arguments from the yaml config file.

    Also prepares the game constants.
    """

    global brickW, brickH, score, highScore, colorIndex, speed  
    global hasMusic, gameMusic, musicVolume, start_time
    global brickList, startingHeight, backgroundImage, unscaledContainers, containers
    global display, clock

    #setting the display
    pygame.init()
    pygame.display.set_caption('Simple Stacking Game') 
    display = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    #background image
    backgroundImage = "containerTowerAssets/blue_sky.jpg"
    backgroundImage = pygame.image.load(backgroundImage).convert_alpha()
    backgroundImage = pygame.transform.scale(backgroundImage, (width, height))

    #rescaling containers
    for i in range(len(image_paths)):
        unscaledContainers.append(pygame.image.load(image_paths[i]).convert_alpha())

    for image in unscaledContainers:
        containers.append(pygame.transform.scale(image, (brickW, brickH)))

    global hasMusic, gameMusic, musicVolume

    #initialize the music
    if (hasMusic):
        global sound
        sound = pygame.mixer.Sound(gameMusic)
        sound.set_volume(musicVolume)
        sound.play(loops=-1)


class Brick:
    """
    Brick object used in the game.

    used to store location, speed and other parameters.
    """
    def __init__(self, x, y, isRandom):
        self.imageIndex = random.randint(0, len(containers) - 1)
        if isRandom:
            self.x = random.uniform(0, width - brickW)
        else:
            self.x = x

        self.y = y
        self.w = brickW
        self.h = brickH
        self.dir = -1 + 2 * random.randint(0, 1)
    
    def draw(self):
        display.blit(containers[self.imageIndex], (self.x, self.y))
        # pygame.draw.rect(display, self.color, (self.x, self.y, self.w, self.h))

    def move(self):
        """
        Move and checks for boundary collision.
        """
        global speed

        if self.x + brickW + self.dir * speed > width:
            self.dir *= -1
        elif self.x + self.dir * speed < 0:
            self.dir *= -1
        self.x += self.dir * speed

def gameOver(message):
    """
    Render game over screen.

    parameters:
        message: message to be displayed on death screen

    """

    global highScore
    highScore = max(score, highScore)
    loop = True

    font = pygame.font.SysFont("ARIAL", width//25)
    text = font.render(message, True, textColor)

    textRect = text.get_rect()
    textRect.center = (width/2, height/2)

    #detect what the player wants to do
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
                if event.key == pygame.K_r:
                    startGame()
            if event.type == pygame.MOUSEBUTTONDOWN:
                startGame()
        display.blit(text, textRect)
        
        pygame.display.update()
        clock.tick()


def showScore(extra):
    """
    Display the score and time left.
    """
    global start_time, score, highScore, timeLimit
    global textColor, width, height, display

    font = pygame.font.SysFont("ARIAL", width//25)
    text = font.render(f"Score: {score}", True, textColor)
    display.blit(text, (10, 10))

    text = font.render(f"High Score: {highScore}", True, textColor)
    display.blit(text, (width // 2 - text.get_size()[0] // 2, 10))

    text = font.render(f"Time Left: {int(start_time + timeLimit + extra - time.time()):d}", True, textColor)
    display.blit(text, (10, 50))


def close():
    pygame.quit()
    sys.exit()

def intersect(blockL, blockR):
    """
    checks if 2 brick intersect

    parameters:
        BlockL: first brick object
        blockR: second brick object
    """
    l, r = blockL.x, blockL.x + brickW
    a, b = blockR.x, blockR.x + brickW

    if (l > a):
        l, a = a, l
        r, b = b, r

    return a <= r


def updateFrame(currentBrick, extra):
    """
    Rerenders all the bricks and GUI.
    """
    display.blit(backgroundImage, (0, 0))
    currentBrick.draw()

    for brick in brickList:
        brick.draw()
    
    showScore(extra)
    pygame.display.update()

def gameLoop():
    """
    One frame of the game loop.
    """
    global start_time, loop, brickList, newBrick, speed
    global height, width, display, brickH, brickW
    global score, highScore, colorIndex, speed
    global hasMusic, gameMusic, musicVolume, start_time
    global startingHeight, extra
    
    while loop:
        if (time.time() - start_time - extra > timeLimit):
            gameOver("Time Over! :(, press R to restart.")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    bef = time.time()
                    gameSettings()
                    extra = extra + time.time() - bef
                if event.key == pygame.K_q:
                    close()


                if event.key == pygame.K_SPACE:
                    #make the brick fall
                    while newBrick.y + brickH <= brickList[-1].y:
                        newBrick.y += 1
                        updateFrame(newBrick, extra)

                    if not (intersect(newBrick, brickList[-1])):
                        gameOver("You Failed!, press R to restart.")
                    
                    score += 1
                    if (score % 3 == 0 and speed + 1 <= 9):
                        speed += 1

                    brickList.append(newBrick)

                    #tower to high, remove 1 brick below
                    if (height / 2 + 2 * brickH > brickList[-1].y):
                        brickList = brickList[1:]
                        for brick in brickList:
                            brick.y += brickH

                    newBrick = Brick(width, startingHeight, True)
        

        newBrick.move()
        updateFrame(newBrick, extra)
        clock.tick(60)

def set_speed(value):
    global speed

    speed = value


def gameSettings():
    """
    Function for displaying the settings menu.
    """
    
    global loop, display, width, height
    global width, height, display, speed, musicVolume
    
    font = pygame.font.SysFont("ARIAL", width // 25)
    speedText = font.render("Speed:", True, textColor)
    speedSlider = Slider(display, width // 4, 4 * height // 20, width // 2, height // 40 \
                    , min=1, max=15, step=1, colour=(0, 0, 0), handleColour=textColor, text='Speed', initial=speed)
    
    volumeText = font.render("Volume:", True, textColor)
    volumeSlider = Slider(display, width // 4, 6 * height // 20, width // 2, height // 40 \
                    , min=0, max=1, step=0.05, colour=(0, 0, 0), handleColour=textColor, text='Speed', initial=musicVolume)

    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        #sky blue rgb code
        display.fill((135, 206, 235))

        display.blit(speedText, (width // 4, 3 * height // 20))
        speed = speedSlider.getValue()

        display.blit(volumeText, (width // 4, 5 * height // 20))
        musicVolume = volumeSlider.getValue()
        sound.set_volume(musicVolume)

        # print(speed)

        pw.update(pygame.event.get())   
        pygame.display.update()


def startGame():
    """
    Main game function.
    """
    global brickW, brickH, score, highScore, colorIndex, speed
    global hasMusic, gameMusic, musicVolume, start_time
    global brickList, startingHeight
    global loop, brickList, start_time, newBrick, extra

    colorIndex = 0
    extra = 0
    score = 0

    newBrick = Brick(width, startingHeight, True)
    brickList = []
    brickList.append(Brick(width / 2 - brickW / 2, height - brickH, False))
    updateFrame(newBrick, 0)
    
    start_time = time.time()
    gameLoop()
    

if __name__ == "__main__":
    load_args()
    startGame()


