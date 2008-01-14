import random
from math import tanh
from engine import State_Machine
from pymunk import vec2d

Base_State=State_Machine.Base_State

def seek1D(current_pos, target_pos, max_force):
        dist=target_pos-current_pos
        #force=40*dist
        
        #if max_force*max_force>force*force: 
                #return force*vec2d(1,0)
        #else: 
        if dist>0:
                return max_force*vec2d(1,0)
        elif dist<0:
                return -max_force*vec2d(1,0)
        return vec2d(0,0)

def evade(current_pos, target_pos, max_force):
        x_dist=target_pos[0]-current_pos[0]
        #y_dist=target_pos[1]-current_pos[1]
        #dist=(x_dist**2+y_dist**2)**0.5
        
        if x_dist==0:
                x_dist=1
        if abs(x_dist)>100:
                return vec2d(0,0)
        else:
                return -4*vec2d(max_force,0)*x_dist/abs(x_dist)
        #if dist==0:
                #dist=1
        
        #force=-400.0*vec2d(x_dist,0)/dist
        
        #if 400.0*x_dist/dist>max_force*10:
                #force=10*max_force*vec2d(1,0)*x_dist/abs(x_dist)
                
        return force
                                        
class Wandering(Base_State):
        def __init__(self, parent_machine):
                Base_State.__init__(self, parent_machine)
                               
                self.position=self.get_parent().rect
                self.time_step=50
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
                parent.body.reset_forces()
                dist=target_pos-actor_pos
                #print dist
                
                if dist*dist<25:
                        target_state=self.target.get_trigger_state()
                        if  target_state is not None:
                                self.get_parent_SM().set_state(target_state) #swich state!
                        self.target=None
                        return
                else:
                        total_force=seek1D(actor_pos, target_pos, self.actor.max_steering)
                        #total_force=vec2d(0,0)

                if not parent.flee_from is None:
                        total_force+=evade(self.actor.get_position(), parent.flee_from, self.actor.max_steering)
                        if abs(parent.flee_from[0]-actor_pos)>100:
                                parent.fle_from=None
                                
                parent.body.apply_force(total_force, vec2d(0,0))
                
                velocity=parent.body.get_velocity()[0]
                if abs(velocity)>0.01:
                        #print velocity/abs(velocity), parent.current_image

                        parent.orientation=int(velocity/abs(velocity))
                        parent.set_image(parent.orientation, parent.current_image)

                                
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
                
                