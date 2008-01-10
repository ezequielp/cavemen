from pygame.sprite import Sprite
from pygame.transform import scale
from pygame import Rect
import pygame
from numpy import array
import os
from states import Using_Gate as Trigger_Gate
import copy 
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
    
    def get_trigger_state(self):
        if hasattr(self, 'Trigger_Class'): return self.Trigger_Class
        else: return None
    
    def __init__(self):
        self.Trigger_Class=None

        Sprite.__init__(self)

class Gate(Item):
    
    
    def __init__(self):
        Item.__init__(self)
        self.image=pygame.image.load(os.path.join("media","Door.png")).convert()
        self.image.set_colorkey(self.image.get_at((0,0)), pygame.locals.RLEACCEL)
        self.image=scale(self.image, (30,34))
        self.rect=self.image.get_rect()
        #self.crect=self.rect
        
        class Gate_Trigger(Trigger_Gate):
            gate=self
            def __init__(self, parent_state_machine):
                Trigger_Gate.__init__(self, parent_state_machine)
            
        self.Trigger_Class=Gate_Trigger
        

    def connect_to(self, gate):
        self.destination_gate=gate
        
    def update(self, current_time):
        Sprite.update(self)
        
    def enter(self, character):
        #assert character.crect.colliderect(self.crect), "Error"
        character.set_new_floor(self.destination_gate.parent,self.destination_gate.rect.center)
        #assert character.crect.colliderect(self.destination_gate.crect), "Error"
        

    
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
        
    