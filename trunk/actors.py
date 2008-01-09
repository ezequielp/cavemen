import engine
from physics_states import *
from states import *
from os import path
import pygame
from pygame.locals import *
import random

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable
  

def load_sequence(file_name, total_images, load_mirror=True):
    '''Loads an image an splits it in frames. If load_mirror is True, the function will return a list of two lists, the first with the sequence of images and the second with the images flipped along the y axis. If load_mirror is False, the function will return the list of images
    Should find a better way, maybe loading to an image pool at startup'''
    sequence=[]
    all=pygame.image.load(path.join("media",file_name)).convert()
    all.set_colorkey(all.get_at((0,0)), RLEACCEL)
    
    image_height=all.get_height()
    image_width=all.get_width()/total_images
    

    sequence.append([all.subsurface((x,0,image_width,image_height))for x in range(0,image_width*total_images,image_width)])
        #Creates characters looking to the right
    if load_mirror:
        sequence.append([pygame.transform.flip(sequence[0][x],True,False) for x in range(total_images)])

    return sequence

class Basic_Actor(pygame.sprite.Sprite):
    #GRAVEDAD=numpy.array([0, 0.00045]) #9.8 m/s^2 si 52 pixeles=4m
    #intervalo_tiempo=10
    #rX=array([[-1,0],
               #[0,1]])
    #rY=array([[1,0],
               #[0,-1]])
    __level=None
    
    def __init__(self, starting_position):
        pygame.sprite.Sprite.__init__(self)
        
        self.rect=pygame.Rect((0,0), (0,0))
        self.rect.center=starting_position
        
        self.movement_state=engine.Physics_Machine(self, starting_position)
        self.movement_state.set_state(PS_freefall)
        #self.next_update=10
        #self.velocidad=array([0.0, 0.0])
        #self.posicion=array([0.0, 0.0])
        #self.aceleracion=array([0.0,0.0])
        #self.update_phys=self.phys_freefall
        #self.object_queue=[]
        
    def reset_PM(self):
        self.standing_on=None
        self.movement_state=engine.Physics_Machine(self, self.rect.center)
        self.movement_state.set_state(PS_freefall)
        
    def set_position(self, coordinates):
        self.rect.center=[int(rect[0]), int(rect[1])]
        if hasattr(self, 'crect'):
            self.crect.center=self.rect.center

    def seen(self, object):
        '''Comunicates to the sprite, that an object was seen'''
        if not object in self.object_queue:
            self.object_queue.append(object)
            
    def update(self, current_time):
        pygame.sprite.Sprite.update(self)
        self.movement_state.update_state(current_time)
        
    def set_level(level):
        if Basic_Actor.__level is None:
            Basic_Actor.__level=level
        else:
            raise BaseException, "level already defined!..."
    
    set_level=Callable(set_level) 
    def get_level(self):
        return Basic_Actor.__level
    
    def visible(self):
        Basic_Actor.__level.set_visible(self)
        
    def invisible(self):
        Basic_Actor.__level.set_invisible(self)

class Caveman(Basic_Actor):
    image=None
    _images=[]
    memory=3000
    
    def __init__(self, initial_position, AI):
        Basic_Actor.__init__(self, initial_position)

        if Caveman.image is None:
            Caveman._images=[[pygame.transform.scale(x, (x.get_width()/2, x.get_height()/2)) for x in y] for y in load_sequence("CavemanAnim.png", 4)]
            
            Caveman.displacement_table=[3, 5, 5, 5]
        self.image=Caveman._images[0][0]
        self.rect.size=self.image.get_size()
        self.crect=self.rect

        self.next_image=self.current_image=random.randint(0,3)
        
        self.orientation=random.randint(0,1)*2-1

        self.image=Caveman._images[0][0]
        self.current_image=0
        self.update_interval=200
        
        self.next_image_update=self.update_interval
        self.displacement=0
        
        self.steering_acceleration=[0,0]
        self.max_steering=random.gauss(0.002, 0.0002)
        
        self.state=engine.State_Machine(self)
        self.state.set_state(Wandering)

    def set_position(self, coordinates):
        if hasattr(self,'standing_on'):
            displacement=coordinates[0]-self.rect.center[0]
            self.displacement+=self.orientation*displacement
            if displacement>0:
                self.orientation=1
                self.rect.center=[int(coordinates[0]), int(coordinates[1])]
            else:
                self.orientation=-1
                self.rect.center=[int(coordinates[0])+1, int(coordinates[1])]
        else:
            self.rect.center=[int(coordinates[0]), int(coordinates[1])]
        if hasattr(self, 'crect'):
            self.crect.center=self.rect.center
    
    def set_new_floor(self, parent, coordinates):
        self.rect.center=coordinates
        if hasattr(self, 'crect'):
            self.crect.center=self.rect.center
        self.displacement=0
        self.reset_PM()
                       
    def get_position(self):
        return self.rect.center



    def update(self, current_time):
        Basic_Actor.update(self,current_time)
        
        self.state.update_state(current_time)

        while self.displacement>=self.displacement_table[self.current_image]:
            self.displacement-=self.displacement_table[self.current_image]
            self.next_image+=1
            if self.next_image==4:
                self.next_image=0
            
        if not self.next_image == self.current_image:
            self.image=Caveman._images[(self.orientation+1)/2][self.current_image]
            self.current_image=self.next_image

                
    def kill(self):
        if hasattr(self, 'standing_on') and self.standing_on is not None:
            self.standing_on.death_toll+=1
        #self.nivel_actual.all.add(Ghost(self))
        pygame.sprite.Sprite.kill(self)

    