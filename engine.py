from pygame.Time import Clock

class State_Machine():
    __state= None
    __parent_actor=None
    
    def __init__(self, parent_actor):
        self.__parent_actor=parent_actor
    
    def set_state(self, new_state):
        if self.__state:
            self.__state.exit()
            
            
        self.__state=new_state(parent_actor)
        self.__state.enter()
        
    def update_state(self, current_time):
        self.__state.execute()
        
class Physics_Machine(State_Machine):
    __state=None
    __parent_actor=None
    
    velocity=array([0.0, 0.0])
    position=array([0.0, 0.0])
    
    def __init__(self, parent_actor, initial_position=[0,0], initial_velocity=[0,0]):
        self.__parent_actor=parent_actor
        self.position=array(initial_position)
        self.velocity=array(initial_velocity)
        self.previous_time=0

        
    def update_state(self, current_time):
        if previous_time==0:
            previous_time=current_time
        if current_time>self.previous_time+self.__state.interval:
            self.__state.execute(current_time-self.previous_time)
            self.previous_time=current_time
    
