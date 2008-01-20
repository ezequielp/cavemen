class Collision_State_Handler():
    shape_type_a=0
    shape_type_b=0
    collision_tables={} #will implement a borg-like pattern
    collision={}
    def __init__(self, space, type_a, type_b, timer, allow_collision=True):
        '''Creates a collision handler that saves the last collision detection of type_a with type_b objects.
        Indexing will be done using type_b as key.'''
        self.clock=timer
        self.allow_collision=allow_collision
        
        if type_a in Collision_State_Handler.collision_tables.keys():
            self.collision=Collision_State_Handler.collision_tables[type_a]
        #elif (type_a,type_b) in Collision_State_Handler.collision_tables.keys():
            #self.collision=Collision_State_Handler.collision_tables[(type_b,type_a)]
        else:
            Collision_State_Handler.collision_tables[type_a]=self.collision
            space.add_collisionpair_func(type_a, type_b, self.collision_handler, ())
        
        
    def get_table(self):
        return self.collision
    

    def collision_handler(self, shape1, shape2, cs, normal_coef, data):
        self.collision[shape2.id]=(self.clock.get_ticks(), shape1.id)
        return self.allow_collision
    