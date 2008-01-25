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
    '''Wrapper object used to implement class methods'''
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
    '''This is an extension to the sprite class. It defines a sprite that has a body, as defined by pymunk. The default body is just a fake body that implements a position and its getter/setter methods. The real body is created after the embody method is called.
    
    The class has a dictionary sprites[id] that gives access to all the instantiated sprites that have a real body (as opposed to the fake body that exists until the embody function is called).
    
    After the _embody_ function is called, the sprite will also have a shape element corresponding to the body's shape.
    
    After calling the _set_level_ method, the class also contains a reference to the current level.'''
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
    
    def set_id(self,id):
        '''Sets the sprite id to be the same as the body's id. This method shouldn't be called manualy'''
        self.id=id
        Basic_Sprite.sprites[id]=self
    
    def get_sprite(self,id):
        '''Getter method to the class dictionary sprites.
        
          * id: The sprite id, it is the same as its body's id.
          
          Returns the sprite that has the given id or None if the id doesn't exist'''
        return Basic_Sprite.sprites.get(id, None)
    
    def set_position(self, coordinates):
        '''Sets the sprite position to the new coordinates.
        
          * coordinate: can be a vec2d or a Rect'''
        self.body.set_position(vec2d(coordinates))

    def get_position(self):
        '''Returns the current sprite's position, as a vec2d object'''
        return self.body.position

    def embody(self, position, group='CAVEMEN', layers=255, friction=0):
        '''Initializes the sprite's body. See pymunk documentation to understand the parameters.
        
        All bodies will have a circular shape. The diameter of the circle is currently defined to be the sprite's rect width. This is probably wrong and I should think of a better way.
        
        There isn't any distintion between group and collision type at the moment, both are the same.'''
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
        '''The sprite's update method, doesn't do anything at all'''
        Sprite.update(self)
        
    def set_level(level):
        '''This class method plugs the Basic_Sprite class with the current level so all sprites can access to the level. It is called once by the Level class.'''
        if Basic_Sprite.level is None:
            Basic_Sprite.level=level
        else:
            raise BaseException, "level already defined!..."
    
    set_level=Callable(set_level) 
    
    def get_level(self):
        '''getter method to the class level property level. Can be used to get access to the current level'''
        return Basic_Actor.level
    

class Basic_Actor(Basic_Sprite):
    '''This class implements the basic methods for an actor, i.e. a sprite that moves around the world and has an ia attached. The ia is currently a State Machine, accesible through the _engine_ property of the sprite.'''
    from engine import State_Machine
    
    flee_from=None
    
    def __init__(self, starting_position):
        '''The actor will have a starting position. If the starting position is not a rectangle, then the rect attribute will be instantiated with 0 size. If the starting position is a rectangle then only the position is set.'''
        Basic_Sprite.__init__(self)
        self.level.all.add(self)
        if hasattr(starting_position,'size' ):
            self.set_position(starting_position.center)
        else:
            self.rect=pygame.Rect((0,0), (0,0))
            self.rect.topleft=starting_position
            self.set_position(starting_position)
            
    def update(self, current_time):
        '''Required update method...'''
        Basic_Sprite.update(self)        

    def visible(self):
        '''Makes the sprite visible by adding it to the level's visible group.'''
        Basic_Actor.level.set_visible(self)
        
    def invisible(self):
        '''Makes the actor invisible by removing it from the level's visible group.'''
        Basic_Actor.level.set_invisible(self)

class Caveman(Basic_Actor):
    '''The Caveman is the basic NPC unit. Its has an energy parameter. The caveman dies if energy becomes negative.'''
    image=None
    _images=[]

    energy=400
    update_interval=200

    def __init__(self, initial_position):
        '''The caveman starts at the given initial_position in a Wandering state. Must implement sprite animations, probably using a parent class.
        
        Each caveman will have a unique maximum speed, given by the max steering parameter. This parameter should probably be generated in a more formal way using a higher level parameter.
        
        If the sprite has a standing_on parameter, then he is currently standing on a floor.'''
        Basic_Actor.__init__(self, initial_position)
        
        from states import Wandering

        #Older way of generating an image sequence. It is not used at the moment but should be used as a guide when creating an animation class
        if Caveman.image is None:
            Caveman._images=[[pygame.transform.scale(x, (x.get_width()/2, x.get_height()/2)) for x in y] for y in load_sequence("CavemanAnim.png", 4)]
            Caveman.displacement_table=[3, 5, 5, 5]


        self.image=Caveman._images[0][0]
        self.rect.size=self.image.get_size()
        self.current_image=0
        
        #sets up the Caveman unique parameters
        self.max_steering=random.gauss(1000,30)
        
        #parameters related to the caveman current state
        self.state=Basic_Actor.State_Machine(self, Wandering)
        self.standing_on=None
        self.embody(initial_position)

    def set_new_floor(self, parent, coordinates):
        '''Changes the caveman position. It is a left over from the older engine. Should be removed soon'''
        self.set_position(coordinates)

    def update(self, current_time):
        '''Updates the sprite and the state machine'''
        Basic_Actor.update(self,current_time)
        #updates state machine
        self.state.update_state(current_time)

    def set_image(self, orientation, image_num):
        '''Sets the actor's image acording to the orientation(=1 if it is heading to the right, -1 if it is heading left) and the image_num corresponding to the current frame of the animation. It is not in use at the moment and should be deprecated for the animation class/method/whatever.'''
        self.image=Caveman._images[(orientation+1)/2][image_num]
        
    def kill(self):
        '''When the Caveman dies he releases a ghost and a skeleton and dissapears.'''
        ghost=Ghost(self)
        skeleton=Skeleton(self)
        self.level.all.add(ghost)
        self.level.all.add(skeleton)
        ghost.visible()
        skeleton.visible()    
        Basic_Actor.kill(self)
        
    def damage(self, damage):
        '''Damage the caveman. If the energy becomes negative he dies.'''
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
    '''The skeleton of a dead actor. It falls until it heats the ground, and then increases the "death_toll" of any floor it is positioned. It will slowly get burried as times goes by and it dissapears when it is deep enough, leaving an image customization on the parent floor.'''
    _image=None
    last_update=0
    update_interval=400
    def __init__(self, original_body):
        '''Could implement different skeleton images for each actor'''
        Basic_Actor.__init__(self,original_body.body.get_position())
        if Skeleton._image is None:
            Skeleton._image=load_sequence("Skeleton.png", 1, load_mirror=False)[0]

        self.image=Skeleton._image[0]
        self.rect=self.image.get_rect()
        self.rect.center=original_body.rect.center
        
        self.embody(original_body.body.get_position(), layers=0, friction=0.9)
        self.body.set_velocity(vec2d(0,0))
        
        
    
        
    def update(self, current_time):
        '''The skeleton has three states (not implemented through a state machine): 
          * In free fall without touching any floor
          * Over some floor, being slowly buried. It scares the cavemen.
          * Deep into the ground. When the skeleton reaches this state it stops being a sprite and it becomes an fixed image. It also stops scaring the Cavemen.'''
        if hasattr(self,'current_floor'):
            #If it is here, then it means it is over some floor.
            if self.get_position()[1]<self.current_floor.get_position()[1]+5:
                #If the skeleton is not deep enough, it gets burried at a fixed rate
                if current_time>self.last_update+self.update_interval:
                    self.set_position([self.get_position()[0], self.get_position()[1]+1])
                    self.last_update=current_time
                    return
            else:
                #if the skeleton is deep enough, it stops scaring Cavemen and becomes a fixed image instead of a sprite.
                self.current_floor.death_toll-=1
                self.current_floor.image.blit(self.image, [self.rect[0]-self.current_floor.rect[0], self.rect[1]-self.current_floor.rect[1]])
                del self.body
                Basic_Actor.level.with_body.remove(self)
                Basic_Actor.level.all.remove(self)
                Basic_Actor.level.visible.remove(self)
                Sprite.kill(self)
        elif hasattr(self, 'body') and (self.body.get_velocity()-vec2d(0,0)).get_length()<0.01:
            #If the skeleton has a physical body and is not falling then it must mean it is over a floor, and gets attached to it, increasing its death_toll. It also removes its body so the physics engine doesn't affect it anymore. 
            floor_collisions=Basic_Actor.State_Machine.floor_collisions
            collision_data=floor_collisions.pop(self.id, None)
            if collision_data is None: return
            self.current_floor=self.get_sprite(collision_data[1])
            space=Basic_Actor.level.space
            space.remove_shape(self.shape)
            space.remove_body(self.body)

            self.current_floor.death_toll+=1
        else:
            return
        
class Ghost(Basic_Actor):
    '''An incorporeal manifestation of an actor whose only purpose is let it die in a beautiful way. :) It dissapears gradualy as it rises to IA heaven.'''
    __images={}
    prev_time=0
    
    def __init__(self, original_body):
        Basic_Actor.__init__(self, original_body.body.get_position())
        if not original_body.__class__ in Ghost.__images:
            Ghost.__images[original_body.__class__]=original_body.image.copy()

            
        self.image=Ghost.__images[original_body.__class__].copy()
        self.image.set_alpha(255)
        
        #layer=0 and group=INCORPOREAL avoids the ghost from interacting with other things
        self.embody(self.rect.center, group='INCORPOREAL', layers=0)

        #Flies upwards without gravity
        self.body.set_velocity(vec2d(0,-400))
        self.body.apply_force(vec2d(0,-9000), vec2d(0,0))
        
            
    def update(self, current_time):
        '''The update method decreases the ghost alpha to make it gradually dissapear. The sprite is erased when alpha becomes 0'''
        Basic_Actor.update(self, current_time)
        if current_time>self.prev_time:
            self.image.set_alpha(self.image.get_alpha()-15)
            if self.image.get_alpha()<=0:
                self.kill()
            self.prev_time+=100

class Floor(Basic_Sprite):
    '''An expansible, general, floor. It contains 2 cliffs as objects contained in the items group and probably some doors to travel to other floors.'''
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
        
        #The cliff objects are used to simplify navigating through the floor. It will probably be replaced soon
        right_cliff=Cliff(self)
        left_cliff=Cliff(self)
        right_cliff.set_position(self.crect.topright)
        left_cliff.set_position(self.crect.topleft)
        self.items.extend([right_cliff, left_cliff])
       
    def update(self, current_time):
        Sprite.update(self)


    def attach_gate(self, gate, position):
        '''Attaches gate to position, the position is understood to be the midbottom coordinates of the gate, relative to the topleft corner of the floor'''
        gate.parent=self
        self.items.append(gate)
        
        position[0]=self.crect.topleft[0]+position[0]
        position[1]=self.crect.topleft[1]+position[1]

        gate.set_position(position)
        
    def get_items(self):
        return self.items

        
class Item(Basic_Sprite):
    '''The class parent for every item object, that is an inert object that an actor can use for specific tasks. To act over the Item, the actor should change his state to a trigger state, obtained with the get_trigger_state method'''
    name="generic" 
    def update(self, current_time):
        Sprite.update(self)
        
    def set_position(self, position):
        '''Change's the Item position. The position parameter should be the location of the midbottom point of the item. This is different from the usual set position method'''
        self.rect.midbottom=position
        new_position=(position[0]-self.rect.width/2.0, position[1]-self.rect.height)
        Basic_Sprite.set_position(self,new_position)
    
    def get_trigger_state(self):
        '''Returns the trigger state class or None if there isn't any defined'''
        if hasattr(self, 'Trigger_Class'): return self.Trigger_Class
        else: return None
        
    def get_object_type(selt):
        '''Returns a custom label identifying the kind of Item'''
        return self.name
    
    def __init__(self):
        Basic_Sprite.__init__(self)
        self.Trigger_Class=None


class Gate(Item):
    '''An object that connects two floors.'''
    label="Gate"
    
    def __init__(self):
        '''The trigger state is defined in the states list and is subclassed here to add a gate property. This is the best way I found to do this. Note that the get trigger state method must return a class object and not an instantiated object, that means we can't use the trigger state's init method to pass the parameter.
        The usual way of creating a gate is using the class method create_connected'''
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
        '''Makes the current gate connect to the gate given in the gate parameter'''
        self.destination_gate=gate
        
    def update(self, current_time):
        Sprite.update(self)
        
    def enter(self, character):
        '''Modifies character as if it had entered the gate. It changes the character position to the destination gate position.'''
        character.set_new_floor(self.destination_gate.parent,self.destination_gate.get_position())
        return True
        #assert character.crect.colliderect(self.destination_gate.crect), "Error"
        
    def destination_death_toll(self):
        '''Returns the death toll of the destination floor.'''
        return self.destination_gate.parent.death_toll
    
    def create_connected():
        '''A class method that instantiates and returns 2 connected gates. This is the best way of instantiating gates'''
        gate1=Gate()
        gate2=Gate()
        gate1.connect_to(gate2)
        gate2.connect_to(gate1)
        return gate1, gate2
    
    create_connected=Callable(create_connected)

    
class Shelter(Gate):
    '''A disconnected gate that takes the character to an off-screen place. The shelter is simulated as a gate with a destination floor of a fixed death toll of 0.'''
    label="shelter"
    def __init__(self):
        Gate.__init__(self)
        
    def destination_death_toll(self):
        return 0
    
    def enter(self, character):
        '''The actor will remain inside as long as the parent's death toll is not 0.'''
        character.body.set_velocity(vec2d(0,0))
        if self.parent.death_toll==0:
            return True
        else:
            character.body.set_velocity(vec2d(0,0))
            return False
        
class Cliff(Item):
    '''A dummy item that represents a floor's gate. It is used internally by that object to allow an easier navigation'''
    def __init__(self,parent):
        Item.__init__(self)
        self.image=pygame.Surface([10,10])
        self.parent=parent
        self.rect=pygame.Rect([0,0],self.image.get_size())
