from pygame.sprite import Sprite

class Base_Sprite(Sprite):
    id=0
    sprites={}
    def __init__(self):
        Sprite.__init__(self)
        
        #self.id=Base_Sprite.id
        #print self.id
        #Base_Sprite.id+=1
    
    def set_id(self,id):
        self.id=id
        Base_Sprite.sprites[id]=self
    
    def get_sprite(self,id):
        return Base_Sprite.sprites[id]
    
    def update(self):
        Sprite.update(self)
        