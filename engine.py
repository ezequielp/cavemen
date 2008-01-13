from numpy import array, matrix
#from physics_states import PS_freefall as Most_General_PS
#from states import Wandering as Initial_State
import random 

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable
  
  
class State_Machine():
    __state= None
    __parent_actor=None
    import actors
    from pymunk import vec2d


        
    
    class Base_State():
        #from pymunk import Body
        #from pymunk import vec2d
        #apply_force=Body.apply_force
        level=None
        def __init__(self, parent_machine):
                #raise AttributeError, "This class shouldn't be instantiated, use a children"
                self.__parent=parent_machine.get_actor()
                self.__parent_SM=parent_machine
                if not State_Machine.Base_State.level:
                    State_Machine.Base_State.level=self.__parent.get_level()
                                
        def get_parent(self):
                return self.__parent
        
        def set_collision_handlers():
            State_Machine.Base_State.floor_collisions=State_Machine.Base_State.level.coll_handlers[0]
            
        set_collision_handlers=Callable(set_collision_handlers)
                
        def get_parent_SM(self):
                return self.__parent_SM
                
        def enter(self):
                pass
        
        def exit(self):
                pass
            
    def __init__(self, parent_actor, Initial_State):
        assert isinstance(parent_actor, State_Machine.actors.Basic_Actor), str(parent_actor)+" is not an actor."
        self.__parent_actor=parent_actor
        self.set_state(Initial_State) #The machine starts in the initial state 

    
    def set_state(self, new_state):
        if self.__state:
            self.__state.exit()
            
            
        self.__state=new_state(self)
        self.previous_time=random.uniform(0, self.__state.time_step)

        self.__state.enter()
        
    def update_state(self, current_time):
        #if not self.previous_time:
            #self.previous_time=current_time
        #self.__parent_actor.body.apply_force(self.vec2d(-100,0),self.vec2d(0,0))

        if current_time>self.previous_time+self.__state.time_step:
            self.__state.execute()
            self.previous_time=current_time

        
    def get_actor(self):
        return self.__parent_actor
    
    def get_current_state(self):
        return self.__state
        
#class Physics_Machine(State_Machine):
    #def __init__(self, parent_actor, initial_position=[0,0], initial_velocity=[0,0]):
        #State_Machine.__init__(self, parent_actor)
        #self.position=array(initial_position)
        #self.velocity=array(initial_velocity)
        #self.set_state(Most_General_PS) #most generic state so far

        
    #def update_state(self, current_time):
        #State_Machine.update_state(self, current_time)
    
