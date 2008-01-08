import random
class Base_State():
        def __init__(self):
                raise AttributeError, "This class shouldn't be instantiated, use a children"
    
        def enter(self):
                pass
        
class Wandering(Base_State):

        def __init__(self, parent_machine):
                self.__parent=parent_machine.get_actor()
                self.__parent_PM=parent_machine
        
                self.position=self.__parent.rect
                self.time_step=20
                self.target=None
        
        def enter(self):
                actor=self.__parent

                
        def execute(self):
                if not hasattr(self.__parent, 'standing_on'): return
                else:
                        if not hasattr(self, 'landmarks'):
                                self.landmarks=self.__parent.standing_on.get_items()
                actor=self.__parent
                if self.target is None:
                        self.target=random.choice(self.landmarks)
                        
                target_pos=self.target.get_position()[0]
                actor_pos=actor.get_position()[0]
                dist=(target_pos-actor_pos)
                if dist*dist<25:
                        self.target=None
                        return
                else:
                        if actor.max_steering*actor.max_steering>0.000001*dist*dist: actor.steering_acceleration=[0.001*dist, 0]
                        else: 
                                if dist>0:
                                        actor.steering_acceleration=[actor.max_steering,0]
                                elif dist<0:
                                        actor.steering_acceleration=[-actor.max_steering,0]
                                else: actor.steering_acceleration=[0,0]
                        
                
                