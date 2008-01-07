from engine import Physics_Machine
from pygame.sprite import spritecollide

class Base_Physics_State():

    def __init__():
        raise AttributeError, "This class shouldn't be instantiated, use a children"
    
    def enter():
        pass
    
class PS_freefall(Base_Physics_State):
    GRAVITY=numpy.array([0, 0.00045])
    
    def __init__(self, parent_physics_machine):
        self.__parent=parent_physics_machine.__parent_actor
        self.__parent_PM=parent_physics_machine
        
        self.position=self.__parent.rect
        self.time_step=10
        
    def enter(self):
        self.velocity=array([self.__parent_PM.velocity[0], self.__parent_PM.velocity[1]])
        self.position=array([self.__parent_PM.position[0], self.__parent_PM.position[1]])

    def exit(self):
        self.__parent_PM.velocity[0], self.__parent_PM.velocity[1]=self.velocity[0], self.velocity[1]
        self.__parent_PM.position[0], self.__parent_PM.position[1]=self.position[0], self.position[1]

    def execute(self, current_time):
        '''Controls the actor movement as a regular object under Newton's laws. Checks collisions with grounds'''
        self.velocity=self.velocity+(__parent.steering_acceleration+BP_freefall.GRAVITY)*self.time_step
        
        self.position=self.position+self.position*self.time_step
        
        for floor in spritecollide(self, Basic_Actor.current_level.floors, False):
            if not self.crect.colliderect(floor.crect):
                continue
            if -16<floor.crect.top-self.__parent.crect.bottom<3 and self.velocity[1]>=0:
                self.velocity[1]=0
                self.__parent_PM.standing_on=floor
                self.__parent_PM.set_state(PS_walking)
                continue
            
            elif -16<floor.crect.left-self.crect.right<3 and self.velocity[0]>0:
                self.velocity[0]=-self.velocity[0]
            elif -3<floor.crect.right-self.crect.left<16 and self.velocity[0]<0:
                self.velocity[0]=-self.velocity[0]
            elif -3<floor.crect.bottom-self.crect.top<16 and self.velocity[1]<0:
                self.velocity[1]=-self.velocity[1]

        self.__parent.set_position([self.position[0], self.position[1]])
        
class PS_walking():
    def __init__(self, parent_physics_machine):
        self.__parent=parent_physics_machine.__parent_actor
        self.__parent_PM=parent_physics_machine
        
        self.position=self.__parent.rect[0]
        self.time_step=10
        
    def enter(self):
        self.velocity=self.__parent_PM.velocity[0]
        self.position=self.__parent_PM.position[0]
        self.right_cliff=self.__parent.standing_on.crect.right
        self.left_cliff=self.__parent.standing_on.crect.left


    def exit(self):
        self.__parent_PM.velocity[0], self.__parent_PM.velocity[1]=self.velocity[0], 0
        self.__parent_PM.position[0]=self.position[0]
        self.__parent.standing_on=None
    
    def execute(self):
        '''Controls the sprite movement as if it was moving over a surface.
    Todo: surfaces with different coefficient index and properties.'''
        self.velocity=self.velocity+__parent.steering_acceleration[0]*self.time_step
        self.velocity[0]=self.velocity[0]*0.9 #must be configured. Can be set by the object itself
            
        self.position=self.position+self.velocity*self.time_step
        
        self.__parent.set_position(self.position)
        
        #checks if the sprite is walking to a cliff

        #should be replaced by a proper evade in a wandering state to generate more interesting outcomes like walkers falling
        if self.left_cliff>self.position.left and self.velocity<0:
            self.velocity=-self.velocity
        elif self.right_cliff<self.position.right and self.velocity>0:
            self.velocity=-self.velocity


    