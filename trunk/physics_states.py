from engine import Physics_Machine
from pygame.sprite import spritecollide
from numpy import array
import sprites 

class Base_Physics_State():

    def __init__():
        raise AttributeError, "This class shouldn't be instantiated, use a children"
    
    def enter():
        pass
    
class PS_freefall(Base_Physics_State):
    GRAVITY=array([0, 0.00045])
    
    def __init__(self, parent_physics_machine):
        self.__parent=parent_physics_machine.get_actor()
        self.__parent_PM=parent_physics_machine
        
        self.position=self.__parent.rect
        self.time_step=10
        
    def enter(self):
        self.velocity=array([self.__parent_PM.velocity[0], self.__parent_PM.velocity[1]])
        self.position=array([self.__parent_PM.position[0], self.__parent_PM.position[1]])

    def exit(self):
        self.__parent_PM.velocity[0], self.__parent_PM.velocity[1]=self.velocity[0], self.velocity[1]
        self.__parent_PM.position[0], self.__parent_PM.position[1]=self.position[0], self.position[1]

    def execute(self):
        '''Controls the actor movement as a regular object under Newton's laws. Checks collisions with grounds'''
        actor=self.__parent
        self.velocity=self.velocity+(actor.steering_acceleration+PS_freefall.GRAVITY)*self.time_step
        
        self.position=self.position+self.velocity*self.time_step
        
        for floor in spritecollide(actor, actor.get_level().floors, False):
            if not actor.crect.colliderect(floor.crect):
                continue
            if -16<floor.crect.top-actor.crect.bottom<3 and self.velocity[1]>=0:
                self.velocity[1]=0
                actor.standing_on=floor
                self.position[1]=floor.crect.top-actor.rect.height/2
                self.__parent_PM.set_state(PS_walking)
                continue
            
            elif -16<floor.crect.left-actor.crect.right<3 and self.velocity[0]>0:
                self.velocity[0]=-self.velocity[0]
            elif -3<floor.crect.right-actor.crect.left<16 and self.velocity[0]<0:
                self.velocity[0]=-self.velocity[0]
            elif -3<floor.crect.bottom-actor.crect.top<16 and self.velocity[1]<0:
                self.velocity[1]=-self.velocity[1]

        actor.set_position([self.position[0], self.position[1]])
        
class PS_walking():
    def __init__(self, parent_physics_machine):
        self.__parent=parent_physics_machine.get_actor()
        self.__parent_PM=parent_physics_machine
        
        self.position=self.__parent.rect[0]
        self.time_step=10
        
    def enter(self):
        self.velocity=self.__parent_PM.velocity[0]
        self.position=self.__parent_PM.position[0]
        self.positionY=self.__parent_PM.position[1]
        self.right_cliff=self.__parent.standing_on.crect.right
        self.left_cliff=self.__parent.standing_on.crect.left


    def exit(self):
        self.__parent_PM.velocity[0], self.__parent_PM.velocity[1]=self.velocity[0], 0
        self.__parent_PM.position[0]=self.position[0]
        self.__parent.standing_on=None
    
    def execute(self):
        '''Controls the sprite movement as if it was moving over a surface.
        Todo: surfaces with different coefficient index and properties.'''
        self.velocity=self.velocity+self.__parent.steering_acceleration[0]*self.time_step
        self.velocity=self.velocity*0.9 #must be configured. Can be set by the object itself
            
        self.position=self.position+self.velocity*self.time_step
        
        self.__parent.set_position([self.position, self.positionY])
        
        #checks if the sprite is walking to a cliff

        #should be replaced by a proper evade in a wandering state to generate more interesting outcomes like walkers falling
    
        if self.left_cliff>self.position and self.velocity<0:
            self.velocity=0
            self.__parent.steering_acceleration[0]=-self.__parent.steering_acceleration[0]
        elif self.right_cliff<self.position and self.velocity>0:
            self.velocity=0
            self.__parent.steering_acceleration[0]=-self.__parent.steering_acceleration[0]



    