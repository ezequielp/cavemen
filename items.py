from pygame.sprite import Sprite
from pygame.transform import scale
from pygame import Rect
import pygame
from numpy import array
import os

#static method trick
class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable
        
class Item(Sprite):
    name="generic"
    def set_position(self, position):
        self.rect.midbottom=position
        if hasattr(self, 'crect'): self.crect=self.rect
    
    def get_position(self):
        return self.rect.center
    def __init__(self):
        Sprite.__init__(self)

class Gate(Item):
    def __init__(self):
        Item.__init__(self)
        self.name="gate"
        self.image=pygame.image.load(os.path.join("media","Door.png")).convert()
        self.image.set_colorkey(self.image.get_at((0,0)), pygame.locals.RLEACCEL)
        self.image=scale(self.image, (30,34))
        self.rect=self.image.get_rect()
        self.crect=self.rect


    def connect_to(self, gate):
        self.destination_gate=gate
        
    def update(self, current_time):
        Sprite.update(self)
        
    def enter(self, character):
        assert character.crect.colliderect(self.crect), "Error"
        character.posicion=array(self.destination_gate.rect.midbottom)
        character.posicion[1]-=character.crect.height/2
        character.standing_on=self.destination_gate.parent
        character.crect.center=list(character.posicion)
        character.rect.center=list(character.posicion)
        assert character.crect.colliderect(self.destination_gate.crect), "Error"
        
    
    def create_connected():
        gate1=Gate()
        gate2=Gate()
        gate1.connect_to(gate2)
        gate2.connect_to(gate1)
        return gate1, gate2
    
    create_connected=Callable(create_connected)
        
class Cliff(Item):
    def __init__(self,parent):
        Item.__init__(self)
        self.image=pygame.Surface([10,10])
        self.parent=parent
        self.rect=pygame.Rect([0,0],self.image.get_size())