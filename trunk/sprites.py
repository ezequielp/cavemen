import pygame
from numpy import array, matrix
import numpy
import items
from math import tanh
import random

from variables import SCREENRECT

from pygame.locals import *

random.seed(100)
#print "seed"

class Basic_Actor(pygame.sprite.Sprite):
    GRAVEDAD=numpy.array([0, 0.00045]) #9.8 m/s^2 si 52 pixeles=4m
    intervalo_tiempo=10
    rX=array([[-1,0],
               [0,1]])
    rY=array([[1,0],
               [0,-1]])
    
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.next_update=10
        self.velocidad=array([0.0, 0.0])
        self.posicion=array([0.0, 0.0])
        self.aceleracion=array([0.0,0.0])
        self.update_phys=self.phys_freefall
        self.object_queue=[]
        
    
    def phys_freefall(self, current_time):
        '''Controls the sprite movement as a regular object under Newton's laws. Checks collisions with grounds'''
        pygame.sprite.Sprite.update(self, current_time)
        if self.next_update<current_time:
            self.velocidad=self.velocidad+(self.aceleracion+Basic_Actor.GRAVEDAD)*Basic_Actor.intervalo_tiempo
            self.posicion=self.posicion+self.velocidad*Basic_Actor.intervalo_tiempo
            self.rect.center=map(round, self.posicion%SCREENRECT.size)
            if hasattr(self,'crect'):
                self.crect.center=self.rect.center
                for piso in pygame.sprite.spritecollide(self, Basic_Actor.nivel_actual.pisos, False):
                    if not self.crect.colliderect(piso.crect):
                        continue
                    if -16<piso.crect.top-self.crect.bottom<3 and self.velocidad[1]>=0:
                        self.crect.bottom=piso.crect.top+1
                        self.velocidad[1]=0
                        self.aceleracion[1]=0
                        self.posicion=array(self.crect.center)
                        self.standing_on=piso
                        self.update_phys=self.phys_walking
                    
                    elif -16<piso.crect.left-self.crect.right<3 and self.velocidad[0]>0:
                        self.crect.right=piso.crect.left
                        self.velocidad[0]=-self.velocidad[0]
                    elif -3<piso.crect.right-self.crect.left<16 and self.velocidad[0]<0:
                        self.crect.left=piso.crect.right
                        self.velocidad[0]=-self.velocidad[0]
                    elif -3<piso.crect.bottom-self.crect.top<16 and self.velocidad[1]<0:
                        self.crect.top=piso.crect.bottom
                        self.velocidad[1]=-self.velocidad[1]
                self.rect.center=self.crect.center   
            self.next_update = current_time+Basic_Actor.intervalo_tiempo
            
    def phys_walking(self, current_time):
        '''Controls the sprite movement as if it was moving over a surface.
        Todo: surfaces with different coefficient index and properties.'''
        pygame.sprite.Sprite.update(self, current_time)
        if self.next_update<current_time:
            self.velocidad=self.velocidad+self.aceleracion*Basic_Actor.intervalo_tiempo
            self.velocidad[0]=self.velocidad[0]*0.9 #must be configured. Can be set by the object itself
                
            self.posicion=self.posicion+self.velocidad*Basic_Actor.intervalo_tiempo
            self.rect.center=round(self.posicion[0]),round(self.posicion[1])
            self.crect.center=self.rect.center
            
            #checks if the sprite is walking to a cliff
            piso=self.standing_on
            if piso.crect.left>self.crect.left and self.orientacion<0:
                self.seen(items.Cliff(piso))
            elif piso.crect.right<self.crect.right and self.orientacion>0:
                self.seen(items.Cliff(piso))
            #checks if sprite is waling through a gate
            for gate in pygame.sprite.spritecollide(self, piso.gates, False):
                self.seen(gate)
            
            if not self.crect.colliderect(self.standing_on.crect):
                self.standing_on=None
                self.update_phys=self.phys_freefall
                
            self.next_update = current_time+Basic_Actor.intervalo_tiempo
    
    def seen(self, object):
        '''Comunicates to the sprite, that an object was seen'''
        if not object in self.object_queue:
            self.object_queue.append(object)
        
    

def cargar_secuencia(nombre, cantidad_imagenes, load_mirror=True):
    '''Loads an image an splits it in frames. If load_mirror is True, the function will return a list of two lists, the first with the sequence of images and the second with the images flipped along the y axis. If load_mirror is False, the function will return the list of images'''
    secuencia=[]
    todos=pygame.image.load(nombre).convert()
    todos.set_colorkey(todos.get_at((0,0)), RLEACCEL)
    
    alto_imagen=todos.get_height()
    ancho_imagen=todos.get_width()/cantidad_imagenes
    

    secuencia.append([todos.subsurface((x,0,ancho_imagen,alto_imagen))for x in range(0,ancho_imagen*cantidad_imagenes,ancho_imagen)])
        #crea los personajes mirando a la derecha
    if load_mirror:
        secuencia.append([pygame.transform.flip(secuencia[0][x],True,False) for x in range(cantidad_imagenes)])

    return secuencia

class Volador(Basic_Actor):
    image=None
    _images=[]
    def __init__(self, initial_position, AI):
        Basic_Actor.__init__(self)
        if Volador.image is None:
            Volador._images=cargar_secuencia("voladorAnim.png", 5)
            Volador.image = Volador._images[0][0]

        self.imagen_actual=random.randint(0,4)
        self.image=Volador._images[1][self.imagen_actual]
        
        self.rect=self.image.get_rect()

        self.rect.center=initial_position
        
        
        self.crect=self.rect.inflate(-10,-10)
        
        self.impulso_acumulado=0
        
        if not AI:
            self.AI=False
        else:
            self.AI=True
        
        self.orientacion=-1
        self.direccion=0
        self.proxima_imagen=0

        self.posicion=array(self.rect.center)

        self.aleteando=False
        self.estado=""
        


    def update(self, current_time):
        self.update_phys( current_time)
        
        if self.velocidad[0]*self.orientacion<0:
            self.orientacion=self.orientacion*-1
            self.image=Volador._images[(self.orientacion+1)/2][self.imagen_actual]

        if self.AI:
            if self.velocidad[1]>0.03:
                if self.estado=="bajando ala" and self.imagen_actual is 4:
                    self.estado="subiendo ala"
                elif self.estado=="subiendo ala" and self.imagen_actual is 0:
                    self.estado="bajando ala"
                elif self.estado is not "bajando ala" and self.estado is not "subiendo ala":
                    self.estado="bajando ala"
            if self.velocidad[1]<-0.03:
                if self.estado is not "bajando ala":
                    self.estado="bajando ala"


        if self.estado=="bajando ala" and self.imagen_actual is not 4 and self.proxima_imagen<current_time:
            self.imagen_actual=self.imagen_actual+1
            self.impulso_acumulado=self.impulso_acumulado+1
            
            self.image=Volador._images[(self.orientacion+1)/2][self.imagen_actual]
            self.proxima_imagen=current_time+100
            self.aceleracion[1]=-0.0015*self.impulso_acumulado-self.velocidad[1]/200
            self.aceleracion[0]=self.direccion*0.002*self.impulso_acumulado
            
        elif self.estado=="subiendo ala" and self.imagen_actual is not 0 and self.proxima_imagen<current_time:
            self.impulso_acumulado=0
            self.aceleracion[0]=0
            self.aceleracion[1]=0
            self.imagen_actual=self.imagen_actual-1
            self.image=Volador._images[(self.orientacion+1)/2][self.imagen_actual]
            self.proxima_imagen=current_time+100
        if self.imagen_actual==4:
            self.aceleracion[0]=0
            self.aceleracion[1]=-self.velocidad[1]/200
        
    def bajar_ala(self):
        self.estado="bajando ala"
    def subir_ala(self):
        self.estado="subiendo ala"
    def acelerar(self, direccion):
        self.direccion=direccion

class Caminante(Basic_Actor):

    image=None
    _images=[]
    memory=3000
    
    def __init__(self, initial_position, AI):
        Basic_Actor.__init__(self)

        if Caminante.image is None:
            Caminante._images=[[pygame.transform.scale(x, (x.get_width()/2, x.get_height()/2)) for x in y] for y in cargar_secuencia("CavernicolaAnim.png", 4)]
            Caminante.image=Caminante._images[0][0]
            Caminante.desplazamiento=[3, 5, 5, 5]



        self.rect=self.image.get_rect()
        self.rect.center=initial_position
        self.crect=self.rect

        
        self.velocidad[0]=0
        self.velocidad[1]=0
        self.orientacion=random.randint(0,1)*2-1

        self.posicion=array(self.rect.center)
        self.image=Caminante._images[0][0]
        self.imagen_actual=0
        self.proxima_imagen=200
        
        self.estado="caminando"

        if not AI:
            self.AI=False
        else:
            self.AI=True
        
        self.last_time_switch=-self.memory
    

    def update(self, current_time):
        self.update_phys(current_time)
        
        #if len(self.object_queue)>1:
         #   print len(self.object_queue), str(self.object_queue[0]),str(self.object_queue[1].rect.midbottom)
        for object in self.object_queue:
            if object.__class__ is items.Gate:
                if self.last_time_switch+Caminante.memory<current_time:
                    #floor switch algorithm, based on montecarlo with an inverse energy given by the death toll of the floors
                    deltaDeath=self.standing_on.death_toll-object.destination_gate.parent.death_toll
                    decision_number=random.uniform(0,1)
                    
                    probability=0.5*tanh(1*deltaDeath)+0.5
                    #print probability
                    if probability >decision_number:
                        object.enter(self)
                    
                    self.last_time_switch=current_time
                
            elif object.__class__ is items.Cliff:
                self.orientacion= -self.orientacion
            elif object.__class:
                print object.__class__
            self.object_queue.remove(object)
        
        if self.velocidad[0]*self.orientacion<0:
            self.orientacion=self.orientacion*-1
            self.image=Caminante._images[(self.orientacion+1)/2][self.imagen_actual]

        if (self.estado is "caminando") and (self.proxima_imagen<current_time) and (self.velocidad[1]==0):
            if self.imagen_actual==3:
                self.imagen_actual=0
                self.rect.centerx=self.rect.centerx+Caminante.desplazamiento[self.imagen_actual]*self.orientacion

            self.imagen_actual=self.imagen_actual+1
            self.image=Caminante._images[(self.orientacion+1)/2][self.imagen_actual]
            self.rect.centerx=self.rect.centerx+Caminante.desplazamiento[self.imagen_actual]*self.orientacion
            self.posicion[0]=self.rect.centerx

            self.proxima_imagen=current_time+200
            
            if self.rect.right>SCREENRECT.right:
                self.orientacion=-1*self.orientacion
                
                
                
            elif self.rect.left<SCREENRECT.left:
                self.orientacion=-1*self.orientacion
                
    def kill(self):
        self.standing_on.death_toll+=1
        self.nivel_actual.all.add(Ghost(self))
        pygame.sprite.Sprite.kill(self)

class Ghost(Basic_Actor):
    __images={}
    def __init__(self, original_body):
        Basic_Actor.__init__(self)
        if not original_body.__class__ in Ghost.__images:
            Ghost.__images[original_body.__class__]=original_body.image.copy()

            
        self.image=Ghost.__images[original_body.__class__].copy()
        self.image.set_alpha(255)
        self.rect=original_body.rect
        #self.crect=pygame.Rect([0,0,0,0])
        self.posicion=numpy.array(original_body.rect.center)
        self.velocidad=numpy.array([0,-0.8])
        self.aceleracion=-Basic_Actor.GRAVEDAD
        self.prev_time=0
        
    def update(self, current_time):
        self.update_phys(current_time)
        if current_time>self.prev_time:
            self.image.set_alpha(self.image.get_alpha()-15)
            if self.image.get_alpha()<=0:
                self.kill()
            self.prev_time+=200
class Piso(pygame.sprite.Sprite):
    image=None
    _images=[]
    cantidad_imagenes=8
    gates=[]
    def __init__(self, initial_position, ancho=2):
        pygame.sprite.Sprite.__init__(self)
        assert ancho>=2, 'Width too small'
        
        Piso._images=cargar_secuencia("piso.png", cantidad_imagenes=self.cantidad_imagenes, load_mirror=False)[0]
        self.image=pygame.Surface((Piso._images[0].get_width()*ancho,Piso._images[0].get_height())).convert()
        self.image.blit(Piso._images[0], [0,0])
        
        for i in range(1,ancho-1):
            self.image.blit(Piso._images[random.randint(1,self.cantidad_imagenes-2)], [Piso._images[0].get_width()*i,0])
        
        self.image.blit(Piso._images[self.cantidad_imagenes-1], [Piso._images[0].get_width()*(ancho-1),0] )
        
        self.image.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        
        self.rect=self.image.get_rect()
        self.rect.topleft=initial_position

        self.crect=self.rect.inflate(-32,0)
        self.death_toll=0
        
       

    def update(self, current_time):
        pygame.sprite.Sprite.update(self)


    def attach_gate(self, gate, position):
        gate.parent=self
        self.gates.append(gate)
        
        position[0]=self.crect.topleft[0]+position[0]
        position[1]=self.crect.topleft[1]+position[1]

        gate.set_position(position)
        

        
