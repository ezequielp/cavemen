import random
from pygame.locals import *
import pygame
import sprites
import engine

#from numpy import array, matrix

SCREENRECT=Rect(0,0,800,600)

random.seed(200)

class Nivel():
    #bordes=Rect(0,0, 100, 100) 
    enteroAzar=random.randint
    import pymunk as pm
    from pymunk.vec2d import vec2d
    from collision_handler import Collision_State_Handler
    #sync_list=[]
    coll_handlers=[]
    pm.init_pymunk()
    space = pm.Space()
    space.gravity = vec2d(0.0, 900.0)
    physics_step=40 #in milliseconds
    
    from groups import definitions as groups
    
    def __init__(self,  timer, file=None):
        #create sprite goups
        self.enemies=pygame.sprite.Group()
        self.friends=pygame.sprite.Group()
        self.floors=pygame.sprite.Group()
        self.all=pygame.sprite.OrderedUpdates()
        self.visible=pygame.sprite.OrderedUpdates()
        #connects actors with current level
        sprites.Basic_Actor.set_level(self)
        
        
        #setups physics engine
        self.space.resize_static_hash()
        self.space.resize_active_hash()
        self.space.set_damping(0.2)
        self.background=pygame.Surface(SCREENRECT.size).convert()
        
        self.last_time=0
        if file is not None:
            self.populate_from_file(file, timer)

    def set_as_BG(self, item):
        self.background.blit(item.image, item.rect)
        
    def transform_Y(self, Ycoord):
        return Ycoord
    
    def embody_floor(self, floor):
        vec2d=self.vec2d
        
        transform_Y=self.transform_Y
        rect=floor.rect
        point_a=floor.rect.midleft
        point_b=floor.rect.midright
        width=floor.rect.height/2.0
        
        body = self.pm.Body(1e100, 1e100)
        shape= self.pm.Segment(body, vec2d(point_a[0], transform_Y(point_a[1])), vec2d(point_b[0], transform_Y(point_b[1])), width)
        shape.friction=0
        shape.group=self.groups['FLOORS']
        shape.collision_type = self.groups['FLOORS']
        floor.set_id(shape.id)
        
        self.space.add_static_shape(shape)


        
        
    def populate_from_file(self, file, timer):
        
        config= eval(open(file, 'U').read())
        self.sanity_check(config)
        
        floors = dict()
        for floor_id in config['Floors']:
            placement=list(config['Relative Placement'][floor_id])
            placement[1]=600-self.transform_Y(placement[1])
            floors[floor_id]=sprites.Floor(placement, round(config['Floor Sizes'][floor_id]/32.0))
            self.embody_floor(floors[floor_id])
            self.set_as_BG(floors[floor_id])
        
        gates= dict()
        for gate1_id in config['Gate Graph']:
            gate2_id=config['Gate Graph'][gate1_id][0]
            gates[gate1_id], gates[gate2_id] = sprites.Gate.create_connected()
        
        shelters=dict()
        for shelter_id in config['Shelters']:
            shelters[shelter_id]=sprites.Shelter()
            
        for floor_id in config['Hierarchy']:
            for item_id in config['Hierarchy'][floor_id]:
                if item_id in gates.keys():
                    floors[floor_id].attach_gate(gates[item_id], list(config['Relative Placement'][item_id]))
                    self.set_as_BG(gates[item_id])
                elif item_id in shelters.keys():
                    floors[floor_id].attach_gate(shelters[item_id], list(config['Relative Placement'][item_id]))
                    self.set_as_BG(shelters[item_id])

        
        num_walkers=config['Options'].get('Walkers', 50)
        
        for floor in floors.values():
            self.floors.add(floor)
        
        for i in range(num_walkers):
            caminante=sprites.Caveman([self.enteroAzar(50,700),600-config['Relative Placement']['A'][1]-50], True)
            caminante.id=i
            self.enemies.add(caminante)
            caminante.embody()

    
        #personaje=sprites.Volador([400,500], False)
        #nivel_actual.friends.add(personaje)
        
        for floor_id in config['Initial Bodycount']:
            floors[floor_id].death_toll=config['Initial Bodycount'].get(floor_id, 0)
            
            
        #Register collision function to handle colisions with floor:
        self.coll_handlers.append(self.Collision_State_Handler(self.space, self.groups['FLOORS'], self.groups['CAVEMEN'], timer).get_table())
        

        engine.State_Machine.set_collision_handlers()
        #self.space.add_collisionpair_func(self.groups['FLOORS'], self.groups['INCORPOREAL'], None)
        
        self.all.add([x.items for x in self.floors])
        self.all.add(self.floors)

        self.all.add(self.friends)
        self.all.add(self.enemies)
        
        #self.visible.add([x.items for x in self.floors])
        self.visible.add(self.friends)
        self.visible.add(self.enemies)
        
        #self.Space.add_collisionpair_func(self.groups['CAVEMEN'], self.groups['FLOORS'], )

        
    def sanity_check(self, conf_module):
        main_keys=['Floors', 'Gates', 'Hierarchy', 'Relative Placement', 'Gate Graph', 'Floor Sizes', 'Options']
        for key in main_keys:
            assert conf_module.has_key(key), 'Module key '+key+' missing'
        Floors=conf_module['Floors']
        Gates=conf_module['Gates']
        Placements=conf_module['Relative Placement']
        Graph=conf_module['Gate Graph']
        Sizes=conf_module['Floor Sizes']
        Hierarchy=conf_module['Hierarchy']
        
        for floor in Floors:
            #checks all floors have a position
            assert Placements.has_key(floor), 'Floor '+floor+' position not defined.'
            assert Sizes.has_key(floor), 'Floor '+floor+' size not defined.'
            if not Sizes[floor]%32 == 0:
                print 'Warning, '+floor+' size is not multiple of tile size 32'
            assert 0<=list(Placements[floor])[0]<SCREENRECT.size[0], 'Floor '+floor+' x-coordinate out of range' 
            assert 0<=list(Placements[floor])[1]<SCREENRECT.size[1], 'Floor '+floor+' y-coordinate out of range' 
            assert 0<=list(Placements[floor])[0]+Sizes[floor]<=SCREENRECT.size[0], 'Floor '+floor+' out of bounding box'
            assert 0<=list(Placements[floor])[1]+32<=SCREENRECT.size[1], 'Floor '+floor+' out of bounding box'
        
        Parents_graph=self.invert(Hierarchy)
        Inverse_graph=self.invert(Graph)
        for gate in Gates:
            assert Parents_graph.has_key(gate), 'Gate '+gate+' is an orphan :\'('
            assert len(Parents_graph[gate])==1, 'Gate '+gate+' has more than one parent: '+str(Parents_graph[gate])
            assert Placements.has_key(gate), 'Gate '+gate+' position not defined.'
            assert 32<=list(Placements[gate])[0]<=round(Sizes[Parents_graph[gate][0]]/32.0)*32-32, 'Gate '+gate+' outside parent colision box' 
            assert 0==list(Placements[gate])[1], 'Gate '+gate+' coordinate is not 0 (Must be)'
            assert gate in Inverse_graph or gate in Graph, 'Gate '+gate+' not connected to other gate'
            
        for floor_id in conf_module['Initial Bodycount']:
            assert floor_id in Floors, floor_id+' not defined in floors list'
            
    def invert(self, graph):
        inv = {}
        for k, v_list in graph.iteritems():
            for v in v_list:
                keys = inv.setdefault(v, [])
                keys.append(k)
            
        return inv
    
    def set_visible(self, sprite):
        if sprite in self.all and not sprite in self.visible:
            self.visible.add(sprite)
            
    def set_invisible(self, sprite):
        if sprite in self.all and sprite in self.visible:
            self.visible.remove(sprite)
            
    def update(self, current_time):
        self.all.update(current_time)
        #print current_time, self.last_time+self.physics_step
        if current_time>self.last_time+self.physics_step:
            self.space.step(self.physics_step/1000.0) 
            self.last_time=current_time
            
            #ok... now sincronizes sprites with pymunk
            for sprite in self.visible:
                sprite.rect.center=[sprite.body.position[0], sprite.body.position[1]]
            
class Mouse(pygame.sprite.Sprite):
    def __init__(self, position, radius):
        pygame.sprite.Sprite.__init__(self)
        self.rect=Rect(0,0,radius,radius)
        self.rect.center=[position[0], position[1]]
        
def main():
    pygame.init()
    screen=pygame.display.set_mode(SCREENRECT.size)
  
    #keep track of time
    clock = pygame.time.Clock()
    
    #create level
    nivel_actual=Nivel(pygame.time, 'Level0.py') 
    
    background=nivel_actual.background

    screen.blit(background, (0,0))
    
    pygame.display.update()

    i=0
    #game loop
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT \
               or (event.type == KEYDOWN and \
                   event.key == K_ESCAPE):
                print clock.get_fps()
                pygame.display.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    personaje.bajar_ala()
                elif event.key == K_RIGHT:
                    personaje.acelerar(1)
                elif event.key == K_LEFT:
                    personaje.acelerar(-1)
            elif event.type == KEYUP:
                if event.key == K_UP:
                    personaje.subir_ala()
                elif event.key == K_RIGHT:
                    personaje.acelerar(0)
            elif event.type == MOUSEBUTTONUP:
                #print 'Click at '+str(event.pos)
                caught=pygame.sprite.spritecollide(Mouse(event.pos, 200),nivel_actual.enemies, False)
                if len(caught)>0:
                    for sprite in caught:
                        sprite.flee_from=event.pos
                    caught=pygame.sprite.spritecollide(Mouse(event.pos, 10),nivel_actual.enemies, False)
                    if len(caught)>0:
                        caught[0].kill()

                
        #clear sprites
        
        
        #update physics and AI
        nivel_actual.update(pygame.time.get_ticks())

        #redraw sprites
        rectlist=nivel_actual.visible.draw(screen)
        pygame.display.update(rectlist)

        clock.tick(50)
        nivel_actual.visible.clear(screen, background)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))

        
    print clock.get_fps()
    pygame.display.quit()
        
if __name__ == '__main__':
    main()
    #import profile
    #profile.run('main()','juego.dat')
