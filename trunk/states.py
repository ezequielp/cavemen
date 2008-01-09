import random
class Base_State():
        def __init__(self, parent_machine):
                #raise AttributeError, "This class shouldn't be instantiated, use a children"
                self.__parent=parent_machine.get_actor()
                self.__parent_SM=parent_machine
                
        def get_parent(self):
                return self.__parent
        
        def get_parent_SM(self):
                return self.__parent_SM
                
        def enter(self):
                pass
        
        def exit(self):
                pass
        
class Wandering(Base_State):

        def __init__(self, parent_machine):
                Base_State.__init__(self, parent_machine)
                self.position=self.get_parent().rect
                self.time_step=20
                self.target=None
        
        def enter(self):
                pass
                        
                
                
        def execute(self):
                if (not hasattr(self.get_parent(), 'standing_on')) or self.get_parent().standing_on==None: return
                else:
                        if not hasattr(self, 'landmarks'):
                                self.landmarks=self.get_parent().standing_on.get_items()
                actor=self.get_parent()
                if self.target is None:
                        self.target=random.choice(self.landmarks)
                        
                target_pos=self.target.get_position()[0]
                actor_pos=actor.get_position()[0]
                dist=(target_pos-actor_pos)
                if dist*dist<25:
                        target_state=self.target.get_trigger_state()
                        if  target_state is not None:
                                self.get_parent_SM().set_state(target_state) #swich state!
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
                                
        def exit(self):
                self.get_parent().steering_acceleration=[0,0]
                        
class Using_Gate(Base_State):
        
        def __init__(self, parent_machine):
                Base_State.__init__(self, parent_machine)
                self.time_step=10
                
        def enter(self):
                self.get_parent().invisible()
        
        def execute(self):
                #What should happen inside a door besides changing location?
                self.gate.enter(self.get_parent())
                self.get_parent_SM().set_state(Wandering)
                #self.get_parent().standing_on=self.gate.destination_gate.parent
        
        def exit(self):
                self.get_parent().visible()
                
                