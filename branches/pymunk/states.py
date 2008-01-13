import random
from math import tanh
from engine import State_Machine
from pymunk import vec2d

Base_State=State_Machine.Base_State
        
class Wandering(Base_State):
        def __init__(self, parent_machine):
                Base_State.__init__(self, parent_machine)
                               
                self.position=self.get_parent().rect
                self.time_step=20
                self.last_time_on_floor=0
                self.target=None
        
        def enter(self):
                self.actor=self.get_parent()
                pass
                        
                
                
        def execute(self):
                parent=self.get_parent()
                parent_id=parent.id
                floor_collisions=self.floor_collisions
                collision_data=floor_collisions.pop(parent_id, None)
                
                if collision_data is None:
                        return
                
                current_floor=parent.get_sprite(collision_data[1])
                collision_time=collision_data[0]
                
                #print "Sprite", parent_id, "standing on floor", floor_collisions[parent_id][1], "at time", floor_collisions[parent_id][0]
                #if not hasattr(self, 'landmarks'):
                self.landmarks=current_floor.get_items()
 

                #target selection
                while self.target is None or not self.target in self.landmarks:
                        self.target=random.choice(self.landmarks)
                        if hasattr(self.target,'destination_gate'):
                                deltaDeath=self.target.parent.death_toll-self.target.destination_gate.parent.death_toll
                                decision_number=random.uniform(0,1)
                                probability=0.5*tanh(1*deltaDeath)+0.5
                                if probability <decision_number:
                                        self.target=None
                        
                
                target_pos=self.target.get_position()[0]
                actor_pos=self.actor.get_position()[0]
                dist=(target_pos-actor_pos)
                parent.body.reset_forces()
                force=100*dist
                #print dist
                if dist*dist<25:
                        target_state=self.target.get_trigger_state()
                        if  target_state is not None:
                                self.get_parent_SM().set_state(target_state) #swich state!
                        self.target=None
                        return
                else:
                        if self.actor.max_steering*self.actor.max_steering>force*force: 
                                parent.body.apply_force(force*vec2d(1,0), vec2d(0,0))
                        else: 
                                if dist>0:
                                        parent.body.apply_force(self.actor.max_steering*vec2d(1,0), vec2d(0,0))
                                elif dist<0:
                                        parent.body.apply_force(-self.actor.max_steering*vec2d(1,0), vec2d(0,0))
                                else: 
                                        parent.body.set_velocity(vec2d(0,0))

                                
        def exit(self):
                self.get_parent().body.reset_forces()
                        
class Using_Gate(Base_State):
        
        def __init__(self, parent_machine):
                Base_State.__init__(self, parent_machine)
                self.time_step=10
                
        def enter(self):
                self.get_parent().body.set_velocity(vec2d(0,0))
                #self.get_parent().invisible()
        
        def execute(self):
                #What should happen inside a door besides changing location?
                #deltaDeath=self.gate.parent.death_toll-self.gate.destination_gate.parent.death_toll
                #decision_number=random.uniform(0,1)
                #probability=0.5*tanh(1*deltaDeath)+0.5
                #if probability >decision_number:
                        #self.gate.enter(self.get_parent())
                #else:
                        #self.gate.destination_gate.enter(self.get_parent())
                        
                self.gate.enter(self.get_parent())
                self.get_parent_SM().set_state(Wandering)
                #self.get_parent().standing_on=self.gate.destination_gate.parent
        
        def exit(self):
                self.get_parent().visible()
                
                