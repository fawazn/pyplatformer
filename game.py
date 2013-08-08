'''A simple platformer. Uses Pygame and the Python Imaging Library. Left, right keys to move.'''

import pygame
import pil

def quitGame(event):
    return  event.type == pygame.QUIT \
        or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

def isKeyDown(event, key):
    return event.type == pygame.KEYDOWN and event.key == key

class Services:
    def blit(self, image, position):
        screen.blit(image, position)

    def imageLoad(self, filename):
        return pygame.image.load(filename)

    def loadGif(self, filename):
        return pil.load_gif(filename)

    def flipImg(self, image):
        return pygame.transform.flip(image, True, False)

    def getElapsed(self):
        return pygame.time.get_ticks()

    def isPressed(self, key):
        return pygame.key.get_pressed()[key]

def generateSprite(filename, services):
    sprite = Sprite(services)
    if filename.endswith(".gif"):
        (sprite.dT, sprite.images) = services.loadGif(filename)
    else:
        sprite.images.append(services.imageLoad(filename))
    return sprite

def flipHorizontalSprite(sprite, services):
    new_sprite = Sprite(services)
    for image in sprite.images:
        new_sprite.images.append(services.flipImg(image))
    new_sprite.dT = sprite.dT
    return new_sprite

class Sprite:
    def __init__(self, services):
        self.position = (0, 0)
        self.images = []
        self.currentImage = 0
        self.dT = 0
        self.millisecond = 0
        self.services = services
        self.millisecsToMove = 0
        self.setDtMov = 0

    def paint(self):
        self.services.blit(self.images[self.currentImage], self.position)

    def animate(self):
        self.millisecond += 1
        if  self.millisecond >= self.dT:
            self.millisecond = 0
            self.currentImage += 1
            self.currentImage %= len(self.images)

    def move(self, delta):
        self.millisecsToMove += 1
        if  self.millisecsToMove >= self.setDtMov:
            self.millisecsToMove = 0
            self.position = (self.position[0] + delta[0], self.position[1] + delta[1])

class Scene:
    def __init__(self, sprites, services):
        self.sprites = sprites
        self.lastAnim = 0
        self.services = services
        self.player = None

    def paint(self):
        for sprite in self.sprites:
            sprite.paint()
        pygame.display.flip()

    def animate(self):
        now = self.services.getElapsed()
        elapsedMillisecs = now - self.lastAnim
        for real_millisecond in range(elapsedMillisecs):
            for sprite in self.sprites:
                sprite.animate()
            if  self.player is not None:
                self.player.apply_movement()
        self.lastAnim = now

def generateCharacter(leftIdleFile, rightIdleFile, characterLeftWalkFile, walk_right_filename, services):
    character = Character(services)

    if leftIdleFile is not None:
        character.leftIdleSprite = generateSprite(leftIdleFile, services)
    if rightIdleFile is not None:
        character.rightIdleSprite = generateSprite(rightIdleFile, services)

    if  character.leftIdleSprite is None and character.rightIdleSprite is not None:
        character.leftIdleSprite = flipHorizontalSprite(character.rightIdleSprite, services)
    if  character.rightIdleSprite is None and character.leftIdleSprite is not None:
        character.rightIdleSprite = flipHorizontalSprite(character.leftIdleSprite, services)

    if characterLeftWalkFile is not None:
        character.leftWalkSprite = generateSprite(characterLeftWalkFile, services)
    if walk_right_filename is not None:
        character.rightWalkSprite = generateSprite(walk_right_filename, services)

    if  character.leftWalkSprite is None and character.rightWalkSprite is not None:
        character.leftWalkSprite = flipHorizontalSprite(character.rightWalkSprite, services)
    if  character.rightWalkSprite is None and character.leftWalkSprite is not None:
        character.rightWalkSprite = flipHorizontalSprite(character.leftWalkSprite, services)

    character.facing = Facing.RIGHT
    character.walking = False
    character.yDifferenceBetweenIdleAndWalk = character.rightWalkSprite.images[0].getHeight() - character.rightIdleSprite.images[0].getHeight()

    return character

class Facing:
    LEFT = 0
    RIGHT = 1

class Character:
    def __init__(self, services):
        self.services = services
        self.leftIdleSprite = None
        self.rightIdleSprite = None
        self.leftWalkSprite = None
        self.rightWalkSprite = None
        self.yDifferenceBetweenIdleAndWalk = 0
        self.facing = Facing.RIGHT
        self.walking = False

    def getCurrentSprite(self):
        sprite = None
        if self.facing == Facing.LEFT:
            sprite = self.leftIdleSprite
            if self.walking:
                sprite = self.leftWalkSprite
        else:
            sprite = self.rightIdleSprite
            if self.walking:
                sprite = self.rightWalkSprite
        return  sprite

    def paint(self):
        self.getCurrentSprite().paint()

    def move(self, delta):
        self.leftIdleSprite.move(delta)
        self.rightIdleSprite.move(delta)
        self.leftWalkSprite.move(delta)
        self.rightWalkSprite.move(delta)

    def setDt(self, timeBetween):
        self.leftIdleSprite.setDtMov = timeBetween
        self.rightIdleSprite.setDtMov = timeBetween
        self.leftWalkSprite.setDtMov = timeBetween
        self.rightWalkSprite.setDtMov = timeBetween

    def apply_movement(self):
        if not self.walking:
            return
        delta = +1
        if self.facing == Facing.LEFT:
            delta = -1
        self.move((delta, 0))

    def handleInput(self, event):
        if self.services.isPressed(pygame.K_LEFT):
            if  self.facing == Facing.LEFT:
                self.walking = True
            self.facing = Facing.LEFT
        elif self.services.isPressed(pygame.K_RIGHT):
            if  self.facing == Facing.RIGHT:
                self.walking = True
            self.facing = Facing.RIGHT
        else:
            if  self.walking:
                self.walking = False

    def set_position(self, position):
        self.leftIdleSprite.position  = position
        self.rightIdleSprite.position = position
        self.leftWalkSprite.position  = position
        self.rightWalkSprite.position = position

    def animate(self):
        self.getCurrentSprite().animate()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((500, 375))
    pygame.mouse.set_visible(False)
    services = Services()

    background = generateSprite('bg.jpg', services)
    player = generateCharacter(None, 'char.gif', None, 'walkanim.gif', services)
    player.set_position((30, 230))
    player.rightWalkSprite.dT /= 2
    player.leftWalkSprite.dT /= 2
    player.setDt(7)
    scene = Scene([background, player], services)
    scene.player = player

    while 1:
        scene.paint()
        scene.animate()

        event = pygame.event.poll()
        player.handleInput(event)
        if quitGame(event):
            break
