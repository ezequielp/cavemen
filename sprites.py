import pygame
import random
import pymunk as pm

from pygame.sprite import Sprite
from pygame import Rect
from math import tanh
from os import path
from pymunk import vec2d
from groups import definitions as groups
from states import Using_Gate as Trigger_Gate

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


class Basic_Sprite(Sprite):
    id=0
    sprites={}
    level=None
    def __init__(self):
        Sprite.__init__(self)
        class FakeBody():
            position=vec2d(0,0)
            def __init__(self):
                pass
            
            def set_position(self, position):
                self.position=position
            
        self.body=FakeBody()
        #self.id=Basic_Sprite.id
        #print self.id
        #Basic_Sprite.id+=1
    
    def set_id(self,id):
        self.id=id
        Basic_Sprite.sprites[id]=self
    
    def get_sprite(self,id):
        return Basic_Sprite.sprites[id]
    
    def set_position(self, coordinates):
        assert hasattr(self, 'body'), "This sprite doesn't have body... "
        self.body.set_position(vec2d(coordinates))


    def get_position(self):
        return self.body.position

    def embody(self, position, group='CAVEMEN', layers=255, friction=0):
        space=Basic_Actor.level.space
        actor=self
        center=actor.rect.center
        radius=actor.rect.width/2.0
        
        body=pm.Body(10,1e100)
        body.position=position[0], position[1]
        
        shape=pm.Circle(body, radius, vec2d(0,0))
        #shape.set_layers(0)
        shape.group=groups[group]
        shape.collision_type = groups[group]
        shape.friction=friction
        actor.set_id(shape.id)
        
        space.add(shape)
        space.add(body)
        actor.body=body 
        actor.shape=shape
        Basic_Actor.level.with_body.add(self)
    
    def update(self):
        Sprite.update(self)
        
    def set_level(level):
        if Basic_Sprite.level is None:
            Basic_Sprite.level=level
        else:
            raise BaseException, "level already defined!..."
    
    set_level=Callable(set_level) 
    def get_level(self):
        return Basic_Actor.level
    

class Basic_Actor(Basic_Sprite):
#    from engine import Physics_Machine
    from engine import State_Machine
    
    flee_from=None
    
    def __init__(self, starting_position):
        Basic_Sprite.__init__(self)
        self.level.all.add(self)
        if hasattr(starting_position,'size' ):
            self.set_position(starting_position)
        else:
            self.rect=pygame.Rect((0,0), (0,0))
            self.rect.center=starting_position
        #self.crect=self.rect
        #self.movement_state=Basic_Actor.Physics_Machine(self, starting_position)

        
    #def reset_PM(self):
        #self.standing_on=None
        #self.movement_state=Basic_Actor.Physics_Machine(self, self.rect.center)
        

    #def set_position(self, coordinates):
        #self.rect.center=[int(coordinates[0]), int(coordinates[1])]
        
        #self.crect.center=self.rect.center

    #def seen(self, object):
        #'''Comunicates to the sprite, that an object was seen'''
        #if not object in self.object_queue:
            #self.object_queue.append(object)
            
    def update(self, current_time):
        Sprite.update(self)
        #self.movement_state.update_state(current_time)
        

    def visible(self):
        Basic_Actor.level.set_visible(self)
        
    def invisible(self):
        Basic_Actor.level.set_invisible(self)
        


        #self.crect.center=self.rect.center

class Caveman(Basic_Actor):
    image=None
    _images=[]
    memory=3000
    energy=400
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
        self.embody(initial_position)
        #self.state.set_state(Wandering)


  
    def set_new_floor(self, parent, coordinates):
        self.set_position(coordinates)
        #self.body.set_position(vec2d(coordinates[0], coordinates[1]))
        #self.body.set_position(vec2d(coordinates[0], coordinates[1]))

        self.displacement=0
        #self.reset_PM()
                       


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
        skeleton=Skeleton(self)
        self.level.all.add(ghost)
        self.level.all.add(skeleton)
        ghost.visible()
        skeleton.visible()    
        Basic_Actor.kill(self)
        
    def damage(self, damage):
        self.energy-=damage
        if self.energy<0:
            self.kill()
        



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
class Skeleton(Basic_Actor):
    _image=None
    last_update=0
    update_interval=400
    def __init__(self, original_body):
        Basic_Actor.__init__(self,original_body.body.get_position())
        if Skeleton._image is None:
            Skeleton._image=load_sequence("Skeleton.png", 1, load_mirror=False)[0]

        self.image=Skeleton._image[0]
        self.rect=self.image.get_rect()
        self.rect.center=original_body.rect.center
        
        self.embody(original_body.body.get_position(), layers=0, friction=0.9)
        self.body.set_velocity(vec2d(0,0))
        
        
    
        
    def update(self, current_time):
        if hasattr(self,'current_floor'):
            if self.get_position()[1]<self.current_floor.get_position()[1]+5:
                if current_time>self.last_update+self.update_interval:
                    self.set_position([self.get_position()[0], self.get_position()[1]+1])
                    self.last_update=current_time
                    return
            else:
                self.current_floor.death_toll-=1
                self.current_floor.image.blit(self.image, [self.rect[0]-self.current_floor.rect[0], self.rect[1]-self.current_floor.rect[1]])
                del self.body
                Basic_Actor.level.with_body.remove(self)
                Basic_Actor.level.all.remove(self)
                Basic_Actor.level.visible.remove(self)
                
        elif hasattr(self, 'body') and (self.body.get_velocity()-vec2d(0,0)).get_length()<0.01:
            floor_collisions=Basic_Actor.State_Machine.floor_collisions
            collision_data=floor_collisions.pop(self.id, None)
            if collision_data is None: return
            self.current_floor=self.get_sprite(collision_data[1])
            space=Basic_Actor.level.space
            space.remove_shape(self.shape)
            space.remove_body(self.body)
            #del self.body
            #Basic_Actor.level.with_body.remove(self)
            self.current_floor.death_toll+=1
        else:
            return
        
class Ghost(Basic_Actor):
    __images={}
    prev_time=0
    
    def __init__(self, original_body):
        Basic_Actor.__init__(self, original_body.body.position)
        if not original_body.__class__ in Ghost.__images:
            Ghost.__images[original_body.__class__]=original_body.image.copy()

            
        self.image=Ghost.__images[original_body.__class__].copy()
        self.image.set_alpha(255)
        #self.rect.size=self.image.get_size()
        self.embody(self.rect.center, group='INCORPOREAL', layers=0)

        #self.body.set_position(vec2d(original_body.rect.center[0],original_body.rect.center[1]))
        self.body.set_velocity(vec2d(0,-400))
        self.body.apply_force(vec2d(0,-9000), vec2d(0,0))
        

        #self.aceleracion=-Basic_Actor.GRAVEDAD
        #self.prev_time=0
        
            
    def update(self, current_time):
        Basic_Actor.update(self, current_time)
        if current_time>self.prev_time:
            self.image.set_alpha(self.image.get_alpha()-15)
            if self.image.get_alpha()<=0:
                self.kill()
            self.prev_time+=100

class Floor(Basic_Sprite):
    image=None
    _images=[]
    total_images=8
    def __init__(self, initial_position, ancho=2):
        pygame.sprite.Sprite.__init__(self)
        assert ancho>=2, 'Width too small'
        

        
        Floor._images=load_sequence("floor.png", total_images=self.total_images, load_mirror=False)[0]
        self.image=pygame.Surface((int(Floor._images[0].get_width()*ancho),int(Floor._images[0].get_height()))).convert()
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

        
class Item(Basic_Sprite):
    name="generic"
    def update(self, current_time):
        Sprite.update(self)
        
    def set_position(self, position):
        self.rect.midbottom=position
        Basic_Sprite.set_position(self, self.rect.topleft)
        #if hasattr(self, 'crect'): self.crect=self.rect
    
    #def get_position(self):
        #return self.rect.center
    
    def get_trigger_state(self):
        if hasattr(self, 'Trigger_Class'): return self.Trigger_Class
        else: return None
    
    def __init__(self):
        Basic_Sprite.__init__(self)
        self.Trigger_Class=None


class Gate(Item):
    label="Gate"
    
    def __init__(self):
        Item.__init__(self)
        self.image=pygame.image.load(path.join("media","Door.png")).convert()
        self.image.set_colorkey(self.image.get_at((0,0)), pygame.locals.RLEACCEL)
        self.image=pygame.transform.scale(self.image, (30,34))
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
        character.set_new_floor(self.destination_gate.parent,self.destination_gate.get_position())
        return True
        #assert character.crect.colliderect(self.destination_gate.crect), "Error"
        
    def destination_death_toll(self):
        return self.destination_gate.parent.death_toll
    
    def create_connected():
        gate1=Gate()
        gate2=Gate()
        gate1.connect_to(gate2)
        gate2.connect_to(gate1)
        return gate1, gate2
    
    create_connected=Callable(create_connected)

    
class Shelter(Gate):
    def __init__(self):
        Gate.__init__(self)
        
    def destination_death_toll(self):
        return 0
    
    def enter(self, character):
        character.body.set_velocity(vec2d(0,0))
        if self.parent.death_toll==0:
            return True
        else:
            character.body.set_velocity(vec2d(0,-200))

            return False
        
class Cliff(Item):
    def __init__(self,parent):
        Item.__init__(self)
        self.image=pygame.Surface([10,10])
        self.parent=parent

        self.rect=pygame.Rect([0,0],self.image.get_size())
