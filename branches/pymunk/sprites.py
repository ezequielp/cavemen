import pygame
from base_sprite import Base_Sprite as Sprite
from math import tanh
import random

from actors import *
from items import *

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

#class Ghost(Basic_Actor):
    #__images={}
    #def __init__(self, original_body):
        #Basic_Actor.__init__(self)
        #if not original_body.__class__ in Ghost.__images:
            #Ghost.__images[original_body.__class__]=original_body.image.copy()

            
        #self.image=Ghost.__images[original_body.__class__].copy()
        #self.image.set_alpha(255)
        #self.rect=original_body.rect
        ##self.crect=pygame.Rect([0,0,0,0])
        #self.posicion=numpy.array(original_body.rect.center)
        #self.velocidad=numpy.array([0,-0.8])
        #self.aceleracion=-Basic_Actor.GRAVEDAD
        #self.prev_time=0
        
    #def update(self, current_time):
        #self.update_phys(current_time)
        #if current_time>self.prev_time:
            #self.image.set_alpha(self.image.get_alpha()-15)
            #if self.image.get_alpha()<=0:
                #self.kill()
            #self.prev_time+=200

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

        
