import random
from pygame.locals import *
import pygame
import sprites

#from numpy import array, matrix

SCREENRECT=Rect(0,0,800,600)

random.seed(200)

class Nivel():
    bordes=Rect(0,0, 100, 100) #la unidad estandard es el metro
    enteroAzar=random.randint

    
    
    def __init__(self, file=None):
        self.enemies=pygame.sprite.Group()
        self.friends=pygame.sprite.Group()
        self.floors=pygame.sprite.Group()
        self.all=pygame.sprite.OrderedUpdates()
        self.visible=pygame.sprite.OrderedUpdates()
        
        if file is not None:
            self.populate_from_file(file)

    def populate_from_file(self, file):
        
        config= eval(open(file).read())
        self.sanity_check(config)
        
        floors = dict()
        for floor_id in config['Floors']:
            placement=list(config['Relative Placement'][floor_id])
            placement[1]=600-placement[1]
            floors[floor_id]=sprites.Floor(placement, round(config['Floor Sizes'][floor_id]/32.0))
        
        gates= dict()
        for gate1_id in config['Gate Graph']:
            gate2_id=config['Gate Graph'][gate1_id][0]
            gates[gate1_id], gates[gate2_id] = sprites.Gate.create_connected()
                
        for floor_id in config['Hierarchy']:
            for gate_id in config['Hierarchy'][floor_id]:
                floors[floor_id].attach_gate(gates[gate_id], list(config['Relative Placement'][gate_id]))
        
        num_walkers=config['Options'].get('Walkers', 50)
        
        for floor in floors.values():
            self.floors.add(floor)
        
        for i in range(num_walkers):
            caminante=sprites.Caveman([self.enteroAzar(50,700),600-config['Relative Placement']['A'][1]-50], True)
            caminante.id=i
            self.enemies.add(caminante)
    
        #personaje=sprites.Volador([400,500], False)
        #nivel_actual.friends.add(personaje)
        
        for floor_id in config['Initial Bodycount']:
            floors[floor_id].death_toll=config['Initial Bodycount'].get(floor_id, 0)
            
        self.all.add([x.items for x in self.floors])
        self.all.add(self.floors)

        self.all.add(self.friends)
        self.all.add(self.enemies)
        
        self.visible.add(self.all)
        
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
    
class Mouse(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.rect=Rect([position[0], position[1], 10, 10])
        
def main():
    
    pygame.init()

    screen=pygame.display.set_mode(SCREENRECT.size)

    enteroAzar=random.randint

    #make background
    background = pygame.Surface(SCREENRECT.size).convert()
    
 
    
    for i in range(1000):
        brillo=enteroAzar(0,255)
        background.set_at((enteroAzar(0,800),enteroAzar(0,600)), (brillo,brillo,brillo) )

    #debug_rect=pygame.Rect([570,210,65,52])
    
    #pygame.draw.rect(background, (255,255,255), debug_rect)
    
    screen.blit(background, (0,0))
    
    pygame.display.update()

    
    #Creates level from file
    nivel_actual=Nivel('level0.py')


    

    
    sprites.Basic_Actor.set_level(nivel_actual)
    
    #keep track of time
    clock = pygame.time.Clock()
    i=0
    #game loop
    while 1:
        #debug
        i+=1
#        if i==200:
 #           assert False
  #      for sprite in nivel_actual.enemigos:
   #         if sprite.crect.colliderect(debug_rect):
    #            bad_sprite=sprite
     #           print 'Bad sprite found '+str(sprite.id)+' after '+str(i)+' iterations'
      #          assert False, "Error"
        #get input
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
                print 'Click at '+str(event.pos)
                caught=pygame.sprite.spritecollide(Mouse(event.pos),nivel_actual.enemies, False)
                if len(caught)>0:
                    caught[0].kill()
                    print "One dead"
                
        #clear sprites
        
        
        #update sprites
        nivel_actual.all.update(pygame.time.get_ticks())

        #redraw sprites
        rectlist=nivel_actual.visible.draw(screen)
        pygame.display.update(rectlist)

        clock.tick(30)
        nivel_actual.visible.clear(screen, background)
        
    print clock.get_fps()
    pygame.display.quit()
        

if __name__ == '__main__':
    main()
    #import profile
    #profile.run('main()','juego.dat')