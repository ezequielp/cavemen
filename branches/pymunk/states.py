
import random
from math import tanh
from engine import State_Machine
from pymunk import vec2d

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
                                
def state_init(state, parent_machine):
        state.parent=parent_machine.get_actor()
        state.parent_SM=parent_machine
        
class Wandering():
        def __init__(self, parent_machine):
                state_init(self, parent_machine)
                self.position=self.parent.rect
                self.time_step=80
                self.last_time_on_floor=0
                self.target=None
        
        def enter(self):
                self.actor=self.parent

        def execute(self):
                parent=self.parent
                parent_id=parent.id
                floor_collisions=State_Machine.floor_collisions
                collision_data=floor_collisions.pop(parent_id, None)
                velocity=parent.body.get_velocity()
                if collision_data is None:
                        fall_speed=velocity[1]
                        if abs(fall_speed)>200:
                                self.parent_SM.set_state(Falling)
                        return
                
                
                current_floor=parent.get_sprite(collision_data[1])

                #target selection
                self.landmarks=current_floor.get_items()

                if self.target is None or not self.target in self.landmarks:
                        self.target=random.choice(self.landmarks)
                        
                target_pos=self.target.get_position()[0]
                actor_pos=self.actor.get_position()[0]
                parent.body.reset_forces()
                dist=target_pos-actor_pos
                
                if dist*dist<25:
                        target_state=self.target.get_trigger_state()
                        if  target_state is not None:
                                self.parent_SM.set_state(target_state) #swich state!
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

                velocity=velocity[0]
                if abs(velocity)>0.01:
                        parent.orientation=int(velocity/abs(velocity))
                        parent.set_image(parent.orientation, parent.current_image)



        def exit(self):
                self.parent.body.reset_forces()
                
class Falling():
        max_velocity=0
        def __init__(self, parent_machine):
                state_init(self, parent_machine)
                self.time_step=40
        

        def execute(self):
                parent=self.parent
                parent_id=parent.id
                floor_collisions=State_Machine.floor_collisions
                collision_data=floor_collisions.pop(parent_id, None)
                velocity=parent.body.get_velocity()
                if self.max_velocity<abs(velocity[1]):
                        self.max_velocity=abs(velocity[1])
                
                if collision_data==None:
                        return
                else:
                        print "Damage taken proportional to", self.max_velocity
                        parent.damage(self.max_velocity)
                        if parent.alive():
                                self.parent_SM.set_state(Wandering)
                        else:
                                return
        
        def exit(self):
                pass
                

class Using_Gate():
        def __init__(self, parent_machine):
                state_init(self, parent_machine)
                self.time_step=1000
                
        def enter(self):
                self.parent.body.set_velocity(vec2d(0,0))
                deltaDeath=self.gate.parent.death_toll-self.gate.destination_death_toll()
                decision_number=random.uniform(0,1)
                probability=0.5*tanh(1*deltaDeath)+0.5
                if decision_number<probability:
                        self.parent.invisible()
                else:
                        self.parent_SM.set_state(Wandering)      
                        
        def execute(self):
                if self.gate.enter(self.parent):
                        self.parent.body.set_velocity(vec2d(0,0))
                        self.parent_SM.set_state(Wandering)      
                        
                        
        
        def exit(self):
                self.parent.visible()
                
                