from engine import Physics_Machine
from physics_states import *
import pygame

def load_sequence(file_name, total_images, load_mirror=True):
    '''Loads an image an splits it in frames. If load_mirror is True, the function will return a list of two lists, the first with the sequence of images and the second with the images flipped along the y axis. If load_mirror is False, the function will return the list of images
    Should find a better way, maybe loading to an image pool at startup'''
    sequence=[]
    all=pygame.image.load(name).convert()
    all.set_colorkey(all.get_at((0,0)), RLEACCEL)
    
    image_height=all.get_height()
    image_width=all.get_width()/total_images
    

    sequence.append([all.subsurface((x,0,image_width,image_width))for x in range(0,image_width*total_images,image_width)])
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
    
    
    def __init__(self, starting_position):
        pygame.sprite.Sprite.__init__(self)
        self.movement_state=Physics_Machine(starting_position)
        self.movement_state.set_state(PS_freefall)
        #self.next_update=10
        #self.velocidad=array([0.0, 0.0])
        #self.posicion=array([0.0, 0.0])
        #self.aceleracion=array([0.0,0.0])
        #self.update_phys=self.phys_freefall
        #self.object_queue=[]
        
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

class Caveman(Basic_Actor):
    image=None
    _images=[]
    memory=3000
    
    def __init__(self, initial_position, AI):
        Basic_Actor.__init__(self, initial_position)

        if Caminante.image is None:
            Caminante._images=[[pygame.transform.scale(x, (x.get_width()/2, x.get_height()/2)) for x in y] for y in load_sequence("CavemanAnim.png", 4)]
            Caminante.image=Caminante._images[0][0]
            Caminante.displacement_table=[3, 5, 5, 5]

        self.rect=self.image.get_rect()
        self.rect.center=initial_position
        self.crect=self.rect

        self.next_image=self.current_image=0
        
        self.orientation=random.randint(0,1)*2-1

        self.image=Caminante._images[0][0]
        self.current_image=0
        self.update_interval=200
        
        self.next_image_update=self.update_interval
        self.displacement=0

    def set_position(self, coordinates):
        if self.standing_on is not None:
            displacement=coordinates[0]-self.rect.center[0]
            if displacement>0:
                self.orientation=1
                self.displacement+=displacement
            else:
                self.orientation=-1
                self.displacement-=displacement            

        
        self.rect.center=[int(rect[0]), int(rect[1])]
        if hasattr(self, 'crect'):
            self.crect.center=self.rect.center

    def update(self, current_time):
        Base_Actor.update(self,current_time)
        
        while self.displacement>=self.displacement_table[self.current_image]:
            self.displacement-=self.displacement_table[self.current_image]
            self.next_image+=1
            
        if not self.next_image == self.current_image:
            self.image=Caminante._images[(self.orientacion+1)/2][self.current_image]
            self.current_image=self.next_image

                
    def kill(self):
        if self.standing_on is not None:
            self.standing_on.death_toll+=1
        #self.nivel_actual.all.add(Ghost(self))
        pygame.sprite.Sprite.kill(self)

    