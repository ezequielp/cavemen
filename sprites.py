import pygame
from base_sprite import Base_Sprite as Sprite
from math import tanh
from os import path
import pymunk as pm
from pymunk import vec2d
import random
from groups import definitions as groups

from items import *


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

class Basic_Actor(Sprite):
#    from engine import Physics_Machine
    from engine import State_Machine
    
    level=None

    flee_from=None
    
    def __init__(self, starting_position):
        Sprite.__init__(self)
        if hasattr(starting_position,'size' ):
            self.rect=starting_position
        else:
            self.rect=pygame.Rect((0,0), (0,0))
            self.rect.center=starting_position
        #self.crect=self.rect
        #self.movement_state=Basic_Actor.Physics_Machine(self, starting_position)

        
    #def reset_PM(self):
        #self.standing_on=None
        #self.movement_state=Basic_Actor.Physics_Machine(self, self.rect.center)
        
    def set_position(self, coordinates):
        self.rect.center=[int(rect[0]), int(rect[1])]
        
        self.crect.center=self.rect.center

    def seen(self, object):
        '''Comunicates to the sprite, that an object was seen'''
        if not object in self.object_queue:
            self.object_queue.append(object)
            
    def update(self, current_time):
        Sprite.update(self)
        #self.movement_state.update_state(current_time)
        
    def set_level(level):
        if Basic_Actor.level is None:
            Basic_Actor.level=level
        else:
            raise BaseException, "level already defined!..."
    
    set_level=Callable(set_level) 
    def get_level(self):
        return Basic_Actor.level
    
    def visible(self):
        Basic_Actor.level.set_visible(self)
        
    def invisible(self):
        Basic_Actor.level.set_invisible(self)

class Caveman(Basic_Actor):
    image=None
    _images=[]
    memory=3000
    
    def __init__(self, initial_position, AI):
        Basic_Actor.__init__(self, initial_position)
        from states import Wandering

        
        if Caveman.image is None:
            Caveman._images=[[pygame.transform.scale(x, (x.get_width()/2, x.get_height()/2)) for x in y] for y in load_sequence("CavemanAnim.png", 4)]
            
            Caveman.displacement_table=[3, 5, 5, 5]
        self.image=Caveman._images[0][0]
        self.rect.size=self.image.get_size()
        #self.crect=self.rect

        #self.next_image=self.current_image=random.randint(0,3)
        
        #self.orientation=random.randint(0,1)*2-1

        self.image=Caveman._images[0][0]
        self.current_image=0
        self.update_interval=200
        
        self.next_image_update=self.update_interval
        self.displacement=0
        
        #self.steering_acceleration=[0,0]
        self.max_steering=random.gauss(1000,30)
        
        self.state=Basic_Actor.State_Machine(self, Wandering)
        self.standing_on=None
        #self.state.set_state(Wandering)

    def set_position(self, coordinates):
        if not self.standing_on is None:
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
        self.crect.center=self.rect.center
    
    def set_new_floor(self, parent, coordinates):
        self.rect.center=coordinates
        self.body.set_position(vec2d(coordinates[0], coordinates[1]))
        if hasattr(self, 'crect'):
            self.crect.center=self.rect.center
        self.displacement=0
        #self.reset_PM()
                       
    def get_position(self):
        return self.rect.center



    def update(self, current_time):
        #updates actor
        Basic_Actor.update(self,current_time)
        #updates state machine
        self.state.update_state(current_time)

        
        #while self.displacement>=self.displacement_table[self.current_image]:
            #self.displacement-=self.displacement_table[self.current_image]
            #self.next_image+=1
            #if self.next_image==4:
                #self.next_image=0
            
        #if not self.next_image == self.current_image:
            #self.image=Caveman._images[(self.orientation+1)/2][self.current_image]
            #self.current_image=self.next_image

    def set_image(self, orientacion, image_num):
        self.image=Caveman._images[(orientacion+1)/2][image_num]
        
    def kill(self):
        #if hasattr(self, 'current_floor') and self.standing_on is not None:
        #    self.standing_on.death_toll+=1
        ghost=Ghost(self)
        #skeleton=Skeleton(self)
        self.level.all.add(ghost)
        #self.nivel_actual.all.add(skeleton)
        ghost.visible()
        #skeleton.set_visible()
        Sprite.kill(self)
        
    def embody(self):
        space=Basic_Actor.level.space
        cm=self
        rect=cm.rect
        radius=rect.width/2.0
        center=rect.center
        
        body=pm.Body(10,1e100)
        body.position=center[0], center[1]

        shape=pm.Circle(body, radius, vec2d(0,0))
        shape.group=groups['CAVEMEN']
        shape.collision_type = groups['CAVEMEN']
        shape.friction=0
        cm.set_id(shape.id)
        
        space.add(shape)
        space.add(body)
        self.body=body


SCREENRECT=Rect(0,0,800,600)

from pygame.locals import *

random.seed(100)
#print "seed"

#class Volador(Basic_Actor):
    #image=None
    #_images=[]
    #def __init__(self, initial_position, AI):
        #Basic_Actor.__init__(self)
        #if Volador.image is None:
            #Volador._images=cargar_secuencia("voladorAnim.png", 5)
            #Volador.image = Volador._images[0][0]

        #self.imagen_actual=random.randint(0,4)
        #self.image=Volador._images[1][self.imagen_actual]
        
        #self.rect=self.image.get_rect()

        #self.rect.center=initial_position
        
        
        #self.crect=self.rect.inflate(-10,-10)
        
        #self.impulso_acumulado=0
        
        #if not AI:
            #self.AI=False
        #else:
            #self.AI=True
        
        #self.orientacion=-1
        #self.direccion=0
        #self.proxima_imagen=0

        #self.posicion=array(self.rect.center)

        #self.aleteando=False
        #self.estado=""
        


    #def update(self, current_time):
        #self.update_phys( current_time)
        
        #if self.velocidad[0]*self.orientacion<0:
            #self.orientacion=self.orientacion*-1
            #self.image=Volador._images[(self.orientacion+1)/2][self.imagen_actual]

        #if self.AI:
            #if self.velocidad[1]>0.03:
                #if self.estado=="bajando ala" and self.imagen_actual is 4:
                    #self.estado="subiendo ala"
                #elif self.estado=="subiendo ala" and self.imagen_actual is 0:
                    #self.estado="bajando ala"
                #elif self.estado is not "bajando ala" and self.estado is not "subiendo ala":
                    #self.estado="bajando ala"
            #if self.velocidad[1]<-0.03:
                #if self.estado is not "bajando ala":
                    #self.estado="bajando ala"


        #if self.estado=="bajando ala" and self.imagen_actual is not 4 and self.proxima_imagen<current_time:
            #self.imagen_actual=self.imagen_actual+1
            #self.impulso_acumulado=self.impulso_acumulado+1
            
            #self.image=Volador._images[(self.orientacion+1)/2][self.imagen_actual]
            #self.proxima_imagen=current_time+100
            #self.aceleracion[1]=-0.0015*self.impulso_acumulado-self.velocidad[1]/200
            #self.aceleracion[0]=self.direccion*0.002*self.impulso_acumulado
            
        #elif self.estado=="subiendo ala" and self.imagen_actual is not 0 and self.proxima_imagen<current_time:
            #self.impulso_acumulado=0
            #self.aceleracion[0]=0
            #self.aceleracion[1]=0
            #self.imagen_actual=self.imagen_actual-1
            #self.image=Volador._images[(self.orientacion+1)/2][self.imagen_actual]
            #self.proxima_imagen=current_time+100
        #if self.imagen_actual==4:
            #self.aceleracion[0]=0
            #self.aceleracion[1]=-self.velocidad[1]/200
        
    #def bajar_ala(self):
        #self.estado="bajando ala"
    #def subir_ala(self):
        #self.estado="subiendo ala"
    #def acelerar(self, direccion):
        #self.direccion=direccion

class Ghost(Basic_Actor):
    __images={}
    prev_time=0
    def __init__(self, original_body):
        Basic_Actor.__init__(self, original_body.rect)
        if not original_body.__class__ in Ghost.__images:
            Ghost.__images[original_body.__class__]=original_body.image.copy()

            
        self.image=Ghost.__images[original_body.__class__].copy()
        self.image.set_alpha(255)
        self.rect.size=self.image.get_size()

        self.embody()
        #self.body.set_position(vec2d(original_body.rect.center[0],original_body.rect.center[1]))
        self.body.set_velocity(vec2d(0,-400))
        self.body.apply_force(vec2d(0,-9000), vec2d(0,0))
        

        #self.aceleracion=-Basic_Actor.GRAVEDAD
        #self.prev_time=0
        
    def embody(self):
        space=Basic_Actor.level.space
        cm=self
        center=cm.rect.center
        radius=cm.rect.width/2.0
        
        body=pm.Body(10,1e100)
        body.position=center[0], center[1]
        
        shape=pm.Circle(body, radius, vec2d(0,0))
        shape.set_layers(0)
        #shape.group=groups['CAVEMEN']
        shape.collision_type = groups['INCORPOREAL']
        shape.friction=0
        cm.set_id(shape.id)
        
        space.add(shape)
        space.add(body)
        self.body=body
            
    def update(self, current_time):
        Basic_Actor.update(self, current_time)
        if current_time>self.prev_time:
            self.image.set_alpha(self.image.get_alpha()-15)
            if self.image.get_alpha()<=0:
                self.kill()
            self.prev_time+=100

class Floor(Sprite):
    image=None
    _images=[]
    total_images=8
    def __init__(self, initial_position, ancho=2):
        pygame.sprite.Sprite.__init__(self)
        assert ancho>=2, 'Width too small'
        

        
        Floor._images=load_sequence("floor.png", total_images=self.total_images, load_mirror=False)[0]
        self.image=pygame.Surface((Floor._images[0].get_width()*ancho,Floor._images[0].get_height())).convert()
        self.image.blit(Floor._images[0], [0,0])
        
        for i in range(1,ancho-1):
            self.image.blit(Floor._images[random.randint(1,self.total_images-2)], [Floor._images[0].get_width()*i,0])
        
        self.image.blit(Floor._images[self.total_images-1], [Floor._images[0].get_width()*(ancho-1),0] )
        
        self.image.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        
        self.rect=self.image.get_rect()
        self.rect.topleft=initial_position

        self.crect=self.rect.inflate(-32,0)
        self.death_toll=0
        
        self.items=[]
        right_cliff=Cliff(self)
        left_cliff=Cliff(self)
        right_cliff.set_position(self.crect.topright)
        left_cliff.set_position(self.crect.topleft)
        self.items.extend([right_cliff, left_cliff])
       

    def update(self, current_time):
        Sprite.update(self)


    def attach_gate(self, gate, position):
        gate.parent=self
        self.items.append(gate)
        
        position[0]=self.crect.topleft[0]+position[0]
        position[1]=self.crect.topleft[1]+position[1]

        gate.set_position(position)
        
    def get_items(self):
        return self.items

        
