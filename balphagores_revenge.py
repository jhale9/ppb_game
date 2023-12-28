import ppb
from ppb import keycodes
from ppb.events import KeyPressed, KeyReleased
import numpy as np
from itertools import chain


def puke_direction(direction, pos=(0,0), size = 0):
    angle = direction.angle((0,1))

    new_angle = angle+np.random.uniform(-25,25)

    rads = np.radians(new_angle)

    x = np.sin(rads)
    y = np.cos(rads)

    if direction:
        pos_offset = direction.normalize()*(size/2)
        vel_offset = ppb.Vector((0,0))  
    elif not direction:
        pos_offset = ppb.Vector((0,1))*(size/2)
        vel_offset = ppb.Vector((0,0))  

    pos = ppb.Vector(pos[0], pos[1])+pos_offset
    vel = ppb.Vector((x, y))+vel_offset
    return(pos,vel)

def deg_to_dir(deg):
    rads = np.radians(deg)
    x = np.sin(rads)
    y = np.cos(rads)
    direction = ppb.Vector((x,y))
    return direction



class Projectile(ppb.Sprite):
    size = 0.25
    speed = 6

    def on_update(self, update_event, signal):
        if self.direction:
            direction = self.direction.normalize()
        else:
            direction = self.direction
        self.position += direction * self.speed * update_event.time_delta


class Hon1(ppb.Sprite):
    size = 0.25
    speed = 8
    dist_traveled = 0
    def on_update(self, update_event, signal):
        #handle movement
        if self.direction:
            direction = self.direction.normalize()
        else:
            direction = self.direction
        
        self.position += direction * self.speed * update_event.time_delta
        self.dist_traveled += self.speed * update_event.time_delta
        ##
        ##
        if self.dist_traveled > 10:
            update_event.scene.remove(self)

class Hon2(ppb.Sprite):
    size = 0.25
    speed = 8
    dist_traveled = 0
    def on_update(self, update_event, signal):
        #handle movement
        if self.direction:
            direction = self.direction.normalize()
        else:
            direction = self.direction
        
        self.position += direction * self.speed * update_event.time_delta
        self.dist_traveled += self.speed * update_event.time_delta
        ##
        ##
        if self.dist_traveled > 10:
            update_event.scene.remove(self)


class Puke(ppb.Sprite):
    size = 0.25
    #direction = ppb.Vector(0, 1)
    #direction = direction
    speed = 8
    dist_traveled = 0

    def __init__(self, position, direction):
        self.position = position
        
        self.direction = direction

    def on_update(self, update_event, signal):
        #if self.direction:
        #    direction = self.direction.normalize()
        #else:

        #movement
        direction = self.direction
            
        self.position += direction * self.speed * update_event.time_delta
        self.dist_traveled += self.speed * update_event.time_delta


        if self.dist_traveled > 4:
            update_event.scene.remove(self)

class Shooting(ppb.Sprite):
    size = 0.5

class Target(ppb.Sprite):
    def __init__(self, position):
        self.position = position
        #move randomly
        x = np.random.uniform(-1,1,2)
        self.direction = ppb.Vector(x[0], x[1])
        self.speed = 1.5

        #state vars
        self.t_shoot = 0
        self.shoot_timer = np.random.uniform(8, 12)
        self.shooting = False
        

    def on_update(self, update_event, signal):
        #movement
        if self.direction:
            direction = self.direction.normalize()
        else:
            direction = self.direction

        self.position += direction * self.speed * update_event.time_delta
        self.position += self.direction * self.speed * update_event.time_delta
        #
        if self.position['x'] > 12 or self.position['x'] < -12:
            self.direction = self.direction.reflect( (-1, 0) )
        if self.position['y'] > 8 or self.position['y'] < -8:
            self.direction = self.direction.reflect( (0, -1) )
        
        #shooting state
        if self.t_shoot > self.shoot_timer:
            self.t_shoot = 0
            self.speed = 0
            self.t_stopped = 0
            self.shooting = True
            a = update_event.scene.add(Shooting(position=(self.position+(0,1))))
            self.shooter = a
        
        if not self.shooting:
            #update reload if moving
            self.t_shoot += update_event.time_delta
        
        elif self.shooting:
            #update shooting if stopped
            self.t_stopped  += update_event.time_delta

            if self.t_stopped > 3.5:

                #reset shooting state
                self.shooting = False
                self.t_stopped = 0
                self.speed = 1


                #shoot
                for p in update_event.scene.get(kind=Player):
                    ppos = p.position
                shot_vector = self.shoot(ppos, mypos = self.position)
                update_event.scene.add(Projectile(position=self.position, direction = shot_vector))
                update_event.scene.remove(self.shooter)

        
        lethal_objects = chain(update_event.scene.get(kind=Puke), update_event.scene.get(kind=Hon1), update_event.scene.get(kind=Hon2))
        for p in lethal_objects:
            if (p.position - self.position).length <= self.size:
                update_event.scene.remove(self)
                #update_event.scene.remove(p)
                break
        

    def shoot(self, ppos, mypos):
        shot_vector = ppos- mypos
        return shot_vector
        


class Player(ppb.Sprite):
    position = ppb.Vector(0, -3)
    direction = ppb.Vector(0, 0)  
    speed = 2
    size = 1

    left = keycodes.Left
    right = keycodes.Right
    up = keycodes.Up
    down = keycodes.Down

    projector = keycodes.Space


    t_puke = 0
    t_respawn = 0

    ult_stage = 0
    ult_time = 0
    is_ulting = False

    scout_shots = 0

    def on_update(self, update_event, signal):
        #movement
        self.position += self.direction * self.speed * update_event.time_delta
        #update_event.scene.add(Projectile(position=self.position + ppb.Vector(0, 0.5), direction = self.direction))
        
        #upadte times
        self.t_puke += update_event.time_delta
        self.t_respawn += update_event.time_delta

        
        if self.t_puke > .025:
            (pos, vol) = puke_direction(self.direction, self.position, self.size)
            update_event.scene.add(Puke(position=pos, direction = vol))
            self.t_puke = 0
        
        if self.t_respawn > 8:
            for x in range(-4, 5, 2):
                update_event.scene.add(Target(position=ppb.Vector(x, 3)))
            self.t_respawn = 0
        
        if self.is_ulting:
            self.handle_ult(update_event)
    

    def handle_ult(self, update_event):
        if self.ult_stage ==0:
            self.ult_time += update_event.time_delta
            self.ult_stage = 1
            for i in range(0,360,6):
                direction = deg_to_dir(i)
                update_event.scene.add(Hon1(position = self.position, direction = direction))

        elif self.ult_stage ==1:
            self.ult_time += update_event.time_delta
            if self.ult_time > .25:
                self.ult_stage = 2
                for i in range(2,360,6):
                    direction = deg_to_dir(i)
                    update_event.scene.add(Hon2(position = self.position, direction = direction))

        elif self.ult_stage ==2:
            self.ult_time += update_event.time_delta
            if self.ult_time > .5:
                self.ult_stage = 3
                for i in range(4,360,6):
                    direction = deg_to_dir(i)
                    update_event.scene.add(Hon1(position = self.position, direction = direction))


        elif self.ult_stage ==3:
            self.ult_time += update_event.time_delta
            if self.ult_time > .75:
                self.ult_stage = 4
                for i in range(0,360,6):
                    direction = deg_to_dir(i)
                    update_event.scene.add(Hon2(position = self.position, direction = direction))


        elif self.ult_stage ==4:
            self.ult_time += update_event.time_delta
            if self.ult_time > 1:
                #reset all
                self.ult_stage = 0
                self.is_ulting = False
                self.ult_time = 0
                for i in range(2,360,6):
                    direction = deg_to_dir(i)
                    update_event.scene.add(Hon1(position = self.position, direction = direction))


        
    


    def on_key_pressed(self, key_event: KeyPressed, signal):
        if key_event.key == self.left:
            self.direction += ppb.Vector(-1, 0)
        elif key_event.key == self.right:
            self.direction += ppb.Vector(1, 0)
        elif key_event.key == self.up:
            self.direction += ppb.Vector(0, 1)
        elif key_event.key == self.down:
            self.direction += ppb.Vector(0, -1)

    def on_key_released(self, key_event: KeyReleased, signal):
        #if key_event.key == self.left:
        #    self.direction += ppb.Vector(1, 0)
        
        #elif key_event.key == self.right:
        #    self.direction += ppb.Vector(-1, 0)

        if key_event.key == self.projector:
            #key_event.scene.add(Projectile(position=self.position + ppb.Vector(0, 0.5), direction = self.direction))
            #todo only if charged
            self.is_ulting = True





def setup(scene):
    scene.add(Player())


    for x in range(-4, 5, 2):
        scene.add(Target(position=ppb.Vector(x, 3)))

    


ppb.run(setup=setup)
