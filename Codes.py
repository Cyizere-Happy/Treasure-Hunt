"""
3D Fox Treasure Hunt Game with Bluetooth Joystick Control
Enhanced environment with houses, landmarks, and treasure hunting mechanics

Requirements:
pip install pygame PyOpenGL pyserial

Hardware Setup:
- Arduino with HC-05/HC-06 Bluetooth module
- Joystick connected to Arduino
- Bluetooth paired with computer
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import serial
import serial.tools.list_ports
import threading
import queue
import time
import random

class Fox3D:
    """A cute cartoon 3D fox character with articulated limbs"""
    
    def __init__(self):
        self.position = [0, 0, -10]
        self.rotation = [0, 0, 0]
        self.arm_rotation = 0
        self.leg_rotation = 0
        self.head_tilt = 0
        self.jump_offset = 0
        self.is_jumping = False
        self.is_waving = False
        self.is_dancing = False
        self.animation_frame = 0
        self.tail_wave = 0
        self.is_walking = False
        self.walk_cycle = 0
        
        self.colors = {
            'body': (1.0, 0.5, 0.1),
            'belly': (1.0, 1.0, 0.95),
            'dark': (0.2, 0.15, 0.1),
            'nose': (0.1, 0.1, 0.1),
            'eyes': (0.0, 0.0, 0.0),
            'inner_ear': (1.0, 0.8, 0.8),
            'tail_tip': (1.0, 1.0, 1.0)
        }
    
    def draw_cube(self, width, height, depth, color):
        """Draw a colored cube"""
        glColor3f(*color)
        w, h, d = width/2, height/2, depth/2
        
        glBegin(GL_QUADS)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        glEnd()
    
    def draw_sphere(self, radius, color, slices=20, stacks=20):
        """Draw a colored sphere"""
        glColor3f(*color)
        quad = gluNewQuadric()
        gluSphere(quad, radius, slices, stacks)
    
    def draw_cylinder(self, radius, height, color, slices=20):
        """Draw a colored cylinder"""
        glColor3f(*color)
        quad = gluNewQuadric()
        gluCylinder(quad, radius, radius, height, slices, 1)
    
    def draw_cone(self, base_radius, height, color, slices=20):
        """Draw a colored cone"""
        glColor3f(*color)
        quad = gluNewQuadric()
        gluCylinder(quad, base_radius, 0, height, slices, 1)
    
    def draw_head(self):
        """Draw the fox's head with ears, eyes, snout"""
        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glRotatef(self.head_tilt, 1, 0, 0)
        
        self.draw_sphere(0.5, self.colors['body'])
        
        glPushMatrix()
        glTranslatef(-0.25, -0.1, 0.35)
        self.draw_sphere(0.2, self.colors['belly'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.25, -0.1, 0.35)
        self.draw_sphere(0.2, self.colors['belly'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.15, 0.45)
        glScalef(1.0, 0.8, 1.2)
        self.draw_sphere(0.18, self.colors['belly'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.15, 0.6)
        self.draw_sphere(0.08, self.colors['nose'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.18, 0.1, 0.42)
        self.draw_sphere(0.08, self.colors['eyes'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.18, 0.1, 0.42)
        self.draw_sphere(0.08, self.colors['eyes'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.16, 0.13, 0.48)
        self.draw_sphere(0.03, (1, 1, 1))
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.20, 0.13, 0.48)
        self.draw_sphere(0.03, (1, 1, 1))
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.25, 0.45, 0.05)
        glRotatef(-20, 0, 0, 1)
        glRotatef(10, 1, 0, 0)
        self.draw_cone(0.15, 0.4, self.colors['body'])
        glTranslatef(0, 0, 0.05)
        self.draw_cone(0.08, 0.3, self.colors['inner_ear'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.25, 0.45, 0.05)
        glRotatef(20, 0, 0, 1)
        glRotatef(10, 1, 0, 0)
        self.draw_cone(0.15, 0.4, self.colors['body'])
        glTranslatef(0, 0, 0.05)
        self.draw_cone(0.08, 0.3, self.colors['inner_ear'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.25, 0.82, 0.08)
        self.draw_sphere(0.08, self.colors['dark'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.25, 0.82, 0.08)
        self.draw_sphere(0.08, self.colors['dark'])
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_body(self):
        """Draw the fox's torso"""
        glPushMatrix()
        glTranslatef(0, 0.6, 0)
        
        glPushMatrix()
        glScalef(1.0, 1.2, 0.9)
        self.draw_sphere(0.5, self.colors['body'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.1, 0.4)
        glScalef(0.7, 1.0, 0.6)
        self.draw_sphere(0.4, self.colors['belly'])
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_arm(self, side):
        """Draw an arm/front leg"""
        glPushMatrix()
        glTranslatef(side * 0.35, 0.4, 0.2)
        
        self.draw_sphere(0.12, self.colors['body'])
        
        if self.is_waving and side == 1:
            glRotatef(math.sin(self.animation_frame * 0.2) * 45 + 90, 1, 0, 0)
        elif self.is_walking or self.is_dancing:
            glRotatef(math.sin(self.arm_rotation + side * math.pi) * 25, 1, 0, 0)
        else:
            glRotatef(math.sin(self.arm_rotation + side * math.pi) * 5, 1, 0, 0)
        
        glPushMatrix()
        glTranslatef(0, -0.25, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_cylinder(0.1, 0.5, self.colors['body'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.5, 0)
        self.draw_sphere(0.1, self.colors['body'])
        glTranslatef(0, -0.25, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_cylinder(0.08, 0.5, self.colors['body'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -1.0, 0)
        glScalef(1.2, 0.6, 1.2)
        self.draw_sphere(0.12, self.colors['dark'])
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_leg(self, side):
        """Draw a back leg"""
        glPushMatrix()
        glTranslatef(side * 0.3, 0.2, -0.2)
        
        self.draw_sphere(0.14, self.colors['body'])
        
        if self.is_dancing:
            glRotatef(math.sin(self.animation_frame * 0.3 + side * math.pi) * 30, 1, 0, 0)
        elif self.is_walking:
            glRotatef(math.sin(self.walk_cycle + side * math.pi) * 25, 1, 0, 0)
        
        glPushMatrix()
        glTranslatef(0, -0.3, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_cylinder(0.11, 0.6, self.colors['body'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.6, 0)
        self.draw_sphere(0.11, self.colors['body'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.6, 0)
        glRotatef(15, 1, 0, 0)
        glTranslatef(0, -0.25, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_cylinder(0.09, 0.5, self.colors['body'])
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -1.1, 0.08)
        glScalef(1.2, 0.6, 1.2)
        self.draw_sphere(0.13, self.colors['dark'])
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_tail(self):
        """Draw the fox's bushy tail"""
        glPushMatrix()
        glTranslatef(0, 0.7, -0.5)
        
        self.tail_wave += 0.05
        tail_angle = math.sin(self.tail_wave) * 10
        if self.is_dancing:
            tail_angle = math.sin(self.animation_frame * 0.2) * 30
        
        glRotatef(45 + tail_angle, 1, 0, 0)
        
        segments = 5
        for i in range(segments):
            t = i / segments
            scale = 1.0 - t * 0.5
            
            glPushMatrix()
            glTranslatef(0, -i * 0.25, 0)
            
            if i == segments - 1:
                glScalef(scale * 0.8, scale * 1.2, scale * 0.8)
                self.draw_sphere(0.25, self.colors['tail_tip'])
            else:
                glScalef(scale, scale * 1.2, scale)
                self.draw_sphere(0.25, self.colors['body'])
            
            glPopMatrix()
        
        glPopMatrix()
    
    def move_continuous(self, direction, speed=0.15):
        """Move continuously in a direction"""
        angle_rad = math.radians(self.rotation[1])
        
        if direction == 'forward':
            self.position[0] -= math.sin(angle_rad) * speed
            self.position[2] -= math.cos(angle_rad) * speed
        elif direction == 'backward':
            self.position[0] += math.sin(angle_rad) * speed
            self.position[2] += math.cos(angle_rad) * speed
        elif direction == 'left':
            self.position[0] -= math.cos(angle_rad) * speed
            self.position[2] += math.sin(angle_rad) * speed
        elif direction == 'right':
            self.position[0] += math.cos(angle_rad) * speed
            self.position[2] -= math.sin(angle_rad) * speed
        
        if not self.is_walking:
            self.is_walking = True
    
    def update_animation(self):
        """Update animation parameters"""
        self.animation_frame += 1
        
        if self.is_jumping:
            self.jump_offset = abs(math.sin(self.animation_frame * 0.2)) * 1.5
            if self.animation_frame > 30:
                self.is_jumping = False
                self.animation_frame = 0
                self.jump_offset = 0
        
        if self.is_walking:
            self.walk_cycle += 0.3
            self.jump_offset = abs(math.sin(self.walk_cycle * 0.5)) * 0.15
            self.arm_rotation += 0.15
        else:
            self.arm_rotation += 0.02
            self.walk_cycle = 0
    
    def draw(self):
        """Draw the complete fox"""
        glPushMatrix()
        
        glTranslatef(*self.position)
        glTranslatef(0, self.jump_offset, 0)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        
        self.draw_body()
        self.draw_head()
        self.draw_arm(-1)
        self.draw_arm(1)
        self.draw_leg(-1)
        self.draw_leg(1)
        self.draw_tail()
        
        glPopMatrix()


class TreasureHuntEnvironment:
    """Large treasure hunting environment with landmarks"""
    
    def __init__(self):
        self.trees = []
        self.bushes = []
        self.flowers = []
        self.houses = []
        self.landmarks = []
        self.current_treasure = None
        self.treasure_found = False
        
        self.generate_environment()
        self.spawn_new_treasure()
    
    def generate_environment(self):
        """Generate a large world with various features"""
        # Dense forest area (north)
        for _ in range(40):
            x = random.uniform(-40, 40)
            z = random.uniform(-80, -40)
            size = random.uniform(0.8, 1.8)
            self.trees.append((x, z, size))
        
        # Scattered trees throughout
        for _ in range(30):
            x = random.uniform(-40, 40)
            z = random.uniform(-40, 40)
            if abs(x) > 5 or abs(z) > 5:
                size = random.uniform(0.7, 1.5)
                self.trees.append((x, z, size))
        
        # Village houses (west side)
        house_positions = [
            (-35, -10), (-35, -20), (-28, -12), (-28, -22),
            (-35, 5), (-28, 8), (-35, 15)
        ]
        for x, z in house_positions:
            color = random.choice([
                (0.8, 0.3, 0.2),
                (0.7, 0.6, 0.3),
                (0.5, 0.4, 0.3),
            ])
            self.houses.append((x, z, color))
        
        # Bushes everywhere
        for _ in range(60):
            x = random.uniform(-45, 45)
            z = random.uniform(-85, 45)
            if abs(x) > 3 or abs(z) > 3:
                size = random.uniform(0.3, 0.7)
                self.bushes.append((x, z, size))
        
        # Flower meadow (east side)
        for _ in range(80):
            x = random.uniform(20, 40)
            z = random.uniform(-20, 20)
            color = random.choice([
                (1.0, 0.2, 0.4), (1.0, 0.8, 0.0),
                (0.6, 0.3, 0.9), (1.0, 0.5, 0.8),
            ])
            self.flowers.append((x, z, color))
        
        # Landmarks
        self.landmarks = [
            {'type': 'well', 'pos': (15, -15), 'name': 'Old Stone Well'},
            {'type': 'statue', 'pos': (0, 30), 'name': 'Ancient Fox Statue'},
            {'type': 'pond', 'pos': (25, 0), 'name': 'Crystal Pond'},
            {'type': 'rock', 'pos': (-20, 25), 'name': 'Giant Boulder'},
            {'type': 'bridge', 'pos': (10, 10), 'name': 'Wooden Bridge'},
            {'type': 'windmill', 'pos': (-15, -35), 'name': 'Old Windmill'},
        ]
    
    def spawn_new_treasure(self):
        """Spawn a new treasure at a random landmark"""
        self.treasure_found = False
        landmark = random.choice(self.landmarks)
        self.current_treasure = {
            'landmark': landmark,
            'pos': landmark['pos'],
            'hint': self.generate_hint(landmark)
        }
        print(f"\n🗺️  NEW TREASURE HUNT!")
        print(f"Hint: {self.current_treasure['hint']}")
        print("="*60)
    
    def generate_hint(self, landmark):
        """Generate a cryptic hint for the treasure location"""
        hints = {
            'well': "Where villagers once drew water from deep below, the treasure awaits near the stone circle.",
            'statue': "Seek the guardian of the south, a monument to foxes of old standing tall.",
            'pond': "By the shimmering waters where flowers dance, reflect upon your eastern journey.",
            'rock': "A titan of stone rests northwest, weathered by ages but standing strong.",
            'bridge': "Cross not over water, but over the path where flowers meet grass, to the southeast.",
            'windmill': "The old miller's companion spins no more, west of the village it stands watching."
        }
        return hints.get(landmark['type'], "The treasure is hidden somewhere special...")
    
    def check_treasure_proximity(self, fox_pos):
        """Check if fox is near the treasure"""
        if self.treasure_found or not self.current_treasure:
            return False
        
        tx, tz = self.current_treasure['pos']
        distance = math.sqrt((fox_pos[0] - tx)**2 + (fox_pos[2] - tz)**2)
        
        if distance < 3.0:
            self.treasure_found = True
            print("\n" + "="*60)
            print("🎉 TREASURE FOUND! 🎉")
            print(f"You discovered the treasure at {self.current_treasure['landmark']['name']}!")
            print("="*60)
            time.sleep(1)
            self.spawn_new_treasure()
            return True
        return False
    
    def draw_cube_helper(self, w, h, d):
        """Helper to draw cube"""
        w, h, d = w/2, h/2, d/2
        glBegin(GL_QUADS)
        glVertex3f(-w, -h, d); glVertex3f(w, -h, d); glVertex3f(w, h, d); glVertex3f(-w, h, d)
        glVertex3f(-w, -h, -d); glVertex3f(-w, h, -d); glVertex3f(w, h, -d); glVertex3f(w, -h, -d)
        glVertex3f(-w, h, -d); glVertex3f(-w, h, d); glVertex3f(w, h, d); glVertex3f(w, h, -d)
        glVertex3f(-w, -h, -d); glVertex3f(w, -h, -d); glVertex3f(w, -h, d); glVertex3f(-w, -h, d)
        glVertex3f(w, -h, -d); glVertex3f(w, h, -d); glVertex3f(w, h, d); glVertex3f(w, -h, d)
        glVertex3f(-w, -h, -d); glVertex3f(-w, -h, d); glVertex3f(-w, h, d); glVertex3f(-w, h, -d)
        glEnd()
    
    def draw_pyramid_helper(self):
        """Draw pyramid for roof"""
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 1, 0); glVertex3f(-1, 0, 1); glVertex3f(1, 0, 1)
        glVertex3f(0, 1, 0); glVertex3f(1, 0, 1); glVertex3f(1, 0, -1)
        glVertex3f(0, 1, 0); glVertex3f(1, 0, -1); glVertex3f(-1, 0, -1)
        glVertex3f(0, 1, 0); glVertex3f(-1, 0, -1); glVertex3f(-1, 0, 1)
        glEnd()
    
    def draw_house(self, x, z, color):
        """Draw a detailed house"""
        glPushMatrix()
        glTranslatef(x, 0, z)
        
        # Foundation
        glColor3f(0.4, 0.3, 0.25)
        glPushMatrix()
        glTranslatef(0, -1.3, 0)
        glScalef(3.2, 0.4, 3.2)
        self.draw_cube_helper(1, 1, 1)
        glPopMatrix()
        
        # Walls
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        glScalef(3, 2, 3)
        self.draw_cube_helper(1, 1, 1)
        glPopMatrix()
        
        # Roof
        glColor3f(0.3, 0.15, 0.1)
        glPushMatrix()
        glTranslatef(0, 2.2, 0)
        glRotatef(90, 0, 1, 0)
        glScalef(2.2, 1, 2.2)
        self.draw_pyramid_helper()
        glPopMatrix()
        
        # Door
        glColor3f(0.2, 0.1, 0.05)
        glPushMatrix()
        glTranslatef(0, -0.1, 1.51)
        glScalef(0.6, 1.2, 0.1)
        self.draw_cube_helper(1, 1, 1)
        glPopMatrix()
        
        # Windows
        glColor3f(0.6, 0.8, 1.0)
        for wx in [-0.8, 0.8]:
            glPushMatrix()
            glTranslatef(wx, 0.6, 1.51)
            glScalef(0.5, 0.5, 0.05)
            self.draw_cube_helper(1, 1, 1)
            glPopMatrix()
        
        # Chimney
        glColor3f(0.5, 0.3, 0.2)
        glPushMatrix()
        glTranslatef(0.8, 2.8, 0.8)
        glScalef(0.4, 1.2, 0.4)
        self.draw_cube_helper(1, 1, 1)
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_landmark(self, landmark):
        """Draw various landmarks"""
        ltype = landmark['type']
        x, z = landmark['pos']
        
        glPushMatrix()
        glTranslatef(x, 0, z)
        
        if ltype == 'well':
            glColor3f(0.5, 0.5, 0.5)
            quad = gluNewQuadric()
            glPushMatrix()
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quad, 0.8, 0.8, 1.5, 16, 1)
            glPopMatrix()
            glColor3f(0.6, 0.3, 0.1)
            glPushMatrix()
            glTranslatef(0, 2.5, 0)
            glRotatef(90, 0, 1, 0)
            glScalef(1.2, 0.8, 1.2)
            self.draw_pyramid_helper()
            glPopMatrix()
            
        elif ltype == 'statue':
            glColor3f(0.6, 0.6, 0.6)
            glPushMatrix()
            glTranslatef(0, 0.5, 0)
            glScalef(1.5, 1, 1.5)
            self.draw_cube_helper(1, 1, 1)
            glPopMatrix()
            glColor3f(0.7, 0.5, 0.2)
            glPushMatrix()
            glTranslatef(0, 2, 0)
            glScalef(0.8, 1.5, 0.8)
            sphere = gluNewQuadric()
            gluSphere(sphere, 1, 12, 12)
            glPopMatrix()
            
        elif ltype == 'pond':
            glColor3f(0.2, 0.4, 0.8)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, -1.4, 0)
            for angle in range(0, 370, 30):
                rad = math.radians(angle)
                glVertex3f(math.cos(rad) * 3, -1.4, math.sin(rad) * 3)
            glEnd()
            
        elif ltype == 'rock':
            glColor3f(0.4, 0.4, 0.4)
            glPushMatrix()
            glTranslatef(0, 1, 0)
            glScalef(2, 1.8, 1.6)
            sphere = gluNewQuadric()
            gluSphere(sphere, 1, 10, 10)
            glPopMatrix()
            
        elif ltype == 'bridge':
            glColor3f(0.5, 0.35, 0.2)
            for i in range(-2, 3):
                glPushMatrix()
                glTranslatef(i * 0.5, -1.3, 0)
                glScalef(0.3, 0.1, 2)
                self.draw_cube_helper(1, 1, 1)
                glPopMatrix()
                
        elif ltype == 'windmill':
            glColor3f(0.9, 0.9, 0.9)
            quad = gluNewQuadric()
            glPushMatrix()
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quad, 0.8, 0.6, 3, 8, 1)
            glPopMatrix()
            glColor3f(0.6, 0.4, 0.2)
            glPushMatrix()
            glTranslatef(0, 3, 0.8)
            for i in range(4):
                glPushMatrix()
                glRotatef(i * 90, 0, 0, 1)
                glTranslatef(0, 1.2, 0)
                glScalef(0.2, 2.5, 0.1)
                self.draw_cube_helper(1, 1, 1)
                glPopMatrix()
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_tree(self, x, z, size):
        """Draw a tree"""
        glPushMatrix()
        glTranslatef(x, 0, z)
        
        glColor3f(0.4, 0.25, 0.1)
        glPushMatrix()
        glTranslatef(0, 0.5 * size, 0)
        glRotatef(-90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.15 * size, 0.12 * size, 1.0 * size, 8, 1)
        glPopMatrix()
        
        glColor3f(0.1, 0.5, 0.1)
        for i in range(3):
            glPushMatrix()
            glTranslatef(0, 1.0 * size + i * 0.4 * size, 0)
            sphere = gluNewQuadric()
            gluSphere(sphere, 0.6 * size * (1.2 - i * 0.2), 12, 12)
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_bush(self, x, z, size):
        """Draw a bush"""
        glPushMatrix()
        glTranslatef(x, 0.3 * size, z)
        glColor3f(0.15, 0.6, 0.15)
        
        for i in range(3):
            offset_x = (i - 1) * 0.3 * size
            glPushMatrix()
            glTranslatef(offset_x, 0, 0)
            sphere = gluNewQuadric()
            gluSphere(sphere, 0.4 * size, 10, 10)
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_flower(self, x, z, color):
        """Draw a flower"""
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        
        glColor3f(0.1, 0.6, 0.1)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.02, 0.02, 0.3, 4, 1)
        glPopMatrix()
        
        glTranslatef(0, 0.3, 0)
        glColor3f(*color)
        sphere = gluNewQuadric()
        gluSphere(sphere, 0.08, 6, 6)
        
        glPopMatrix()
    
    def draw_treasure_indicator(self):
        """Draw spinning treasure chest at current treasure location"""
        if self.treasure_found or not self.current_treasure:
            return
        
        x, z = self.current_treasure['pos']
        
        glPushMatrix()
        glTranslatef(x, 0.5, z)
        glRotatef(time.time() * 50, 0, 1, 0)
        
        # Chest body
        glColor3f(0.6, 0.4, 0.1)
        glPushMatrix()
        glScalef(0.8, 0.5, 0.6)
        self.draw_cube_helper(1, 1, 1)
        glPopMatrix()
        
        # Chest lid
        glColor3f(0.5, 0.3, 0.08)
        glPushMatrix()
        glTranslatef(0, 0.35, 0)
        glScalef(0.85, 0.2, 0.65)
        self.draw_cube_helper(1, 1, 1)
        glPopMatrix()
        
        # Gold lock
        glColor3f(1.0, 0.84, 0.0)
        glPushMatrix()
        glTranslatef(0, 0.0, 0.31)
        sphere = gluNewQuadric()
        gluSphere(sphere, 0.08, 8, 8)
        glPopMatrix()
        
        # Sparkle effect
        glColor3f(1.0, 1.0, 0.5)
        for i in range(4):
            glPushMatrix()
            glRotatef(i * 90 + time.time() * 100, 0, 1, 0)
            glTranslatef(0.6, 0.5, 0)
            sphere = gluNewQuadric()
            gluSphere(sphere, 0.05, 4, 4)
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_ground(self):
        """Draw large textured ground plane"""
        glDisable(GL_LIGHTING)
        
        # Main grass
        glColor3f(0.2, 0.6, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(-50, -1.5, 50)
        glVertex3f(50, -1.5, 50)
        glVertex3f(50, -1.5, -90)
        glVertex3f(-50, -1.5, -90)
        glEnd()
        
        # Dirt path through village
        glColor3f(0.5, 0.4, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-38, -1.48, 30)
        glVertex3f(-25, -1.48, 30)
        glVertex3f(-25, -1.48, -30)
        glVertex3f(-38, -1.48, -30)
        glEnd()
        
        # Grid for reference
        glColor3f(0.25, 0.65, 0.25)
        glBegin(GL_LINES)
        for i in range(-50, 51, 5):
            glVertex3f(i, -1.49, -90)
            glVertex3f(i, -1.49, 50)
            glVertex3f(-50, -1.49, i)
            glVertex3f(50, -1.49, i)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def draw(self):
        """Draw entire environment"""
        self.draw_ground()
        
        for x, z, size in self.trees:
            self.draw_tree(x, z, size)
        
        for x, z, size in self.bushes:
            self.draw_bush(x, z, size)
        
        for x, z, color in self.flowers:
            self.draw_flower(x, z, color)
        
        for x, z, color in self.houses:
            self.draw_house(x, z, color)
        
        for landmark in self.landmarks:
            self.draw_landmark(landmark)
        
        self.draw_treasure_indicator()


class BluetoothReceiver:
    """Handles Bluetooth serial communication"""
    
    def __init__(self):
        self.serial_conn = None
        self.command_queue = queue.Queue()
        self.running = False
        self.connected = False
        self.port = None
        
    def find_port(self):
        """Find available serial ports"""
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        print("\n" + "="*60)
        print("Available Serial Ports:")
        print("="*60)
        
        for i, port in enumerate(ports):
            print(f"  [{i}] {port.device} - {port.description}")
            available_ports.append(port.device)
            
            if 'HC-05' in port.description or 'HC-06' in port.description or 'Bluetooth' in port.description:
                print(f"      ^ Bluetooth device detected!")
                self.port = port.device
        
        if not available_ports:
            print("  No serial ports found!")
            return None
            
        return available_ports
    
    def connect(self, port=None, baudrate=38400):
        """Connect to serial port"""
        if port:
            self.port = port
        
        if not self.port:
            available = self.find_port()
            if not available:
                return False
                
            if not self.port:
                try:
                    print("\nEnter port number to use (or 'q' to skip): ", end='')
                    choice = input().strip()
                    if choice.lower() == 'q':
                        print("Skipping Bluetooth - keyboard only")
                        return False
                    idx = int(choice)
                    if 0 <= idx < len(available):
                        self.port = available[idx]
                except (ValueError, IndexError):
                    print("Invalid selection")
                    return False
        
        try:
            print(f"\nConnecting to {self.port} at {baudrate} baud...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=baudrate,
                timeout=0.1
            )
            time.sleep(2)
            self.connected = True
            print("✓ Bluetooth connected!")
            return True
        except serial.SerialException as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def start_listening(self):
        """Start listening thread"""
        if not self.connected:
            return False
            
        self.running = True
        listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listen_thread.start()
        return True
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        self.command_queue.put(line)
            except serial.SerialException:
                self.connected = False
                break
            except UnicodeDecodeError:
                pass
            
            time.sleep(0.01)
    
    def get_command(self):
        """Get next command"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop and close"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()


class FoxTreasureHuntGame:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        self.display = (1024, 768)
        self.screen = pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Fox Treasure Hunt - Bluetooth Control")
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glClearColor(0.53, 0.81, 0.92, 1.0)
        
        glLight(GL_LIGHT0, GL_POSITION, (10, 15, 5, 1))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.6, 0.6, 0.55, 1))
        glLight(GL_LIGHT0, GL_DIFFUSE, (1.0, 0.95, 0.8, 1))
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.fox = Fox3D()
        self.environment = TreasureHuntEnvironment()
        self.clock = pygame.time.Clock()
        self.running = True
        self.bt_receiver = BluetoothReceiver()
        
        self.current_direction = None
        self.movement_timeout = 0
        
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
        # Game state
        self.game_state = 'intro'  # intro, playing, won, lost
        self.timer = 120  # 2 minutes per treasure
        self.score = 0
        self.treasures_found = 0
        self.intro_screen_shown = False
        self.game_over_time = 0
        
        # Camera settings
        self.camera_view = 'back'  # 'back' or 'front'Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
        # Game state
        self.game_state = 'intro'  # intro, playing, won, lost
        self.timer = 120  # 2 minutes per treasure
        self.score = 0
        self.treasures_found = 0
        self.intro_screen_shown = False
        self.game_over_time = 0
    
    def handle_command(self, command):
        """Handle control commands"""
        command = command.lower().strip()
        
        if command == 'forward':
            self.current_direction = 'forward'
            self.movement_timeout = 60
        elif command == 'backward':
            self.current_direction = 'backward'
            self.movement_timeout = 60
        elif command == 'left':
            self.current_direction = 'left'
            self.movement_timeout = 60
        elif command == 'right':
            self.current_direction = 'right'
            self.movement_timeout = 60
        elif command == 'stop':
            self.current_direction = None
            self.movement_timeout = 0
        elif command == 'rotate_left':
            self.fox.rotation[1] -= 15
        elif command == 'rotate_right':
            self.fox.rotation[1] += 15
        elif command == 'jump':
            if not self.fox.is_jumping:
                self.fox.is_jumping = True
                self.fox.animation_frame = 0
        elif command == 'wave':
            self.fox.is_waving = not self.fox.is_waving
        elif command == 'dance':
            self.fox.is_dancing = not self.fox.is_dancing
    
    def process_movements(self):
        """Process movements"""
        if self.movement_timeout > 0:
            self.movement_timeout -= 1
        else:
            self.current_direction = None
        
        if self.current_direction:
            self.fox.is_walking = True
            self.fox.move_continuous(self.current_direction)
        else:
            self.fox.is_walking = False
        
        # Check if treasure found
        if self.environment.check_treasure_proximity(self.fox.position):
            self.treasures_found += 1
            self.score += int(self.timer * 10)  # Bonus points for time remaining
            self.timer = 120  # Reset timer for next treasure
            
            # Celebrate!
            self.fox.is_dancing = True
            self.fox.is_jumping = True
    
    def update_timer(self):
        """Update game timer"""
        if self.game_state == 'playing':
            self.timer -= 1/60  # Decrease by 1 second per 60 frames
            
            if self.timer <= 0:
                self.game_state = 'lost'
                self.game_over_time = time.time()
                print("\n" + "="*60)
                print("⏰ TIME'S UP! GAME OVER!")
                print(f"Treasures Found: {self.treasures_found}")
                print(f"Final Score: {self.score}")
                print("="*60)
    
    def draw_text_2d(self, text, x, y, font, color=(255, 255, 255)):
        """Draw 2D text on screen"""
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glWindowPos2d(x, self.display[1] - y - text_surface.get_height())
        glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                    GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND)
    
    def draw_intro_screen(self):
        """Draw introduction/tutorial screen"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Switch to 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Background
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.3, 0.5, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(50, 50)
        glVertex2f(self.display[0] - 50, 50)
        glVertex2f(self.display[0] - 50, self.display[1] - 50)
        glVertex2f(50, self.display[1] - 50)
        glEnd()
        
        # Border
        glColor4f(1.0, 0.84, 0.0, 1.0)
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(50, 50)
        glVertex2f(self.display[0] - 50, 50)
        glVertex2f(self.display[0] - 50, self.display[1] - 50)
        glVertex2f(50, self.display[1] - 50)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Title
        self.draw_text_2d("🦊 FOX TREASURE HUNT 🦊", 280, 100, self.big_font, (255, 215, 0))
        
        # Instructions
        y_pos = 180
        instructions = [
            "HOW TO PLAY:",
            "",
            "🎯 OBJECTIVE: Find hidden treasures using cryptic hints!",
            "⏰ TIME LIMIT: You have 2 minutes to find each treasure",
            "🏆 SCORING: Faster finds = Higher scores!",
            "",
            "🕹️  JOYSTICK CONTROLS:",
            "   Forward/Backward/Left/Right - Move the fox",
            "   Stop - Stop moving",
            "",
            "⌨️  KEYBOARD CONTROLS:",
            "   Arrow Keys - Move in all directions",
            "   Q / E - Rotate camera left/right",
            "   SPACE - Jump (just for fun!)",
            "   W - Wave, D - Dance",
            "",
            "💡 TIPS:",
            "   • Read the hint carefully - it describes the location!",
            "   • Look for the golden spinning treasure chest",
            "   • Explore houses, landmarks, and nature areas",
            "   • You'll see sparkles when near the treasure!",
            "",
            "Press ENTER or SPACE to start your adventure!"
        ]
        
        for line in instructions:
            if line.startswith("HOW TO PLAY") or line.startswith("🕹️") or line.startswith("⌨️") or line.startswith("💡"):
                color = (255, 215, 0)
                font = self.font
            elif line.startswith("🎯") or line.startswith("⏰") or line.startswith("🏆"):
                color = (100, 255, 100)
                font = self.small_font
            else:
                color = (255, 255, 255)
                font = self.small_font
            
            self.draw_text_2d(line, 80, y_pos, font, color)
            y_pos += 30
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        pygame.display.flip()
    
    def draw_game_over_screen(self):
        """Draw game over screen"""
        # Still render the 3D world in background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        camera_distance = 12
        camera_height = 6
        camera_angle = math.radians(self.fox.rotation[1])
        
        cam_x = self.fox.position[0] + math.sin(camera_angle) * camera_distance
        cam_z = self.fox.position[2] + math.cos(camera_angle) * camera_distance
        
        gluLookAt(
            cam_x, camera_height, cam_z,
            self.fox.position[0], self.fox.position[1] + 1, self.fox.position[2],
            0, 1, 0
        )
        
        self.environment.draw()
        self.fox.update_animation()
        self.fox.draw()
        
        # Switch to 2D
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Semi-transparent overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        if self.game_state == 'lost':
            glColor4f(0.5, 0.0, 0.0, 0.8)
        else:
            glColor4f(0.0, 0.5, 0.0, 0.8)
            
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.display[0], 0)
        glVertex2f(self.display[0], self.display[1])
        glVertex2f(0, self.display[1])
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Game over text
        if self.game_state == 'lost':
            self.draw_text_2d("⏰ TIME'S UP!", 350, 250, self.big_font, (255, 100, 100))
        else:
            self.draw_text_2d("🎉 TREASURE FOUND!", 300, 250, self.big_font, (100, 255, 100))
        
        self.draw_text_2d(f"Treasures Found: {self.treasures_found}", 380, 330, self.font, (255, 255, 255))
        self.draw_text_2d(f"Final Score: {self.score}", 400, 370, self.font, (255, 215, 0))
        self.draw_text_2d("Press ENTER to play again or ESC to quit", 260, 450, self.small_font, (200, 200, 200))
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def draw_hud(self):
        """Draw HUD overlay with hints, timer, and score"""
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Hint box background
        if self.environment.current_treasure:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(0.1, 0.1, 0.1, 0.85)
            glBegin(GL_QUADS)
            glVertex2f(10, 10)
            glVertex2f(self.display[0] - 10, 10)
            glVertex2f(self.display[0] - 10, 100)
            glVertex2f(10, 100)
            glEnd()
            
            # Gold border
            glColor4f(1.0, 0.84, 0.0, 1.0)
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            glVertex2f(10, 10)
            glVertex2f(self.display[0] - 10, 10)
            glVertex2f(self.display[0] - 10, 100)
            glVertex2f(10, 100)
            glEnd()
            
            glDisable(GL_BLEND)
        
        # Timer box (top right)
        timer_color = (255, 100, 100) if self.timer < 30 else (255, 215, 0) if self.timer < 60 else (100, 255, 100)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.1, 0.1, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(self.display[0] - 220, 10)
        glVertex2f(self.display[0] - 10, 10)
        glVertex2f(self.display[0] - 10, 120)
        glVertex2f(self.display[0] - 220, 120)
        glEnd()
        glDisable(GL_BLEND)
        
        # Score box (top right, below timer)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.1, 0.1, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(self.display[0] - 220, 130)
        glVertex2f(self.display[0] - 10, 130)
        glVertex2f(self.display[0] - 10, 210)
        glVertex2f(self.display[0] - 220, 210)
        glEnd()
        glDisable(GL_BLEND)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        # Draw text on top
        if self.environment.current_treasure:
            hint = self.environment.current_treasure['hint']
            self.draw_text_2d("🗺️  TREASURE HINT:", 25, 30, self.font, (255, 215, 0))
            
            # Word wrap hint text
            words = hint.split()
            line = ""
            y = 60
            for word in words:
                test_line = line + word + " "
                if len(test_line) > 80:
                    self.draw_text_2d(line, 25, y, self.small_font, (255, 255, 255))
                    line = word + " "
                    y += 25
                else:
                    line = test_line
            if line:
                self.draw_text_2d(line, 25, y, self.small_font, (255, 255, 255))
        
        # Timer
        minutes = int(self.timer // 60)
        seconds = int(self.timer % 60)
        self.draw_text_2d("⏰ TIME:", self.display[0] - 200, 30, self.font, (255, 215, 0))
        self.draw_text_2d(f"{minutes}:{seconds:02d}", self.display[0] - 150, 65, self.big_font, timer_color)
        
        # Score
        self.draw_text_2d("🏆 SCORE:", self.display[0] - 200, 150, self.font, (255, 215, 0))
        self.draw_text_2d(f"{self.score}", self.display[0] - 150, 180, self.font, (100, 255, 100))
        
        # Distance to treasure (helper)
        if self.environment.current_treasure:
            tx, tz = self.environment.current_treasure['pos']
            distance = math.sqrt((self.fox.position[0] - tx)**2 + (self.fox.position[2] - tz)**2)
            
            if distance < 10:
                proximity_text = "🔥 VERY CLOSE!"
                color = (255, 100, 100)
            elif distance < 20:
                proximity_text = "🌟 Getting warmer..."
                color = (255, 200, 100)
            elif distance < 30:
                proximity_text = "💨 Keep searching..."
                color = (200, 200, 255)
            else:
                proximity_text = "🧭 Far away"
                color = (150, 150, 150)
            
            self.draw_text_2d(proximity_text, self.display[0] - 200, 240, self.small_font, color)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def reset_game(self):
        """Reset game to initial state"""
        self.fox.position = [0, 0, -10]
        self.fox.rotation = [0, 0, 0]
        self.fox.is_walking = False
        self.fox.is_dancing = False
        self.fox.is_waving = False
        self.environment.spawn_new_treasure()
        self.timer = 120
        self.score = 0
        self.treasures_found = 0
        self.game_state = 'playing'
        self.current_direction = None
        self.movement_timeout = 0
    
    def run(self):
        """Main game loop"""
        print("\n" + "="*60)
        print("🦊 FOX TREASURE HUNT GAME 🦊")
        print("="*60)
        
        if self.bt_receiver.connect():
            self.bt_receiver.start_listening()
            print("\n✓ Bluetooth active!")
        else:
            print("\n⚠ Keyboard only")
        
        print("\n" + "="*60)
        
        while self.running:
            # Handle intro screen
            if self.game_state == 'intro':
                self.draw_intro_screen()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                            self.game_state = 'playing'
                            print("\n🎮 GAME STARTED! Good luck finding the treasure!")
                            print("="*60)
                
                self.clock.tick(60)
                continue
            
            # Handle game over screen
            if self.game_state in ['won', 'lost']:
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_RETURN:
                            self.reset_game()
                
                pygame.display.flip()
                self.clock.tick(60)
                continue
            
            # Normal gameplay
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_UP:
                        self.handle_command('forward')
                    elif event.key == pygame.K_DOWN:
                        self.handle_command('backward')
                    elif event.key == pygame.K_LEFT:
                        self.handle_command('left')
                    elif event.key == pygame.K_RIGHT:
                        self.handle_command('right')
                    elif event.key == pygame.K_SPACE:
                        self.handle_command('jump')
                    elif event.key == pygame.K_w:
                        self.handle_command('wave')
                    elif event.key == pygame.K_d:
                        self.handle_command('dance')
                    elif event.key == pygame.K_q:
                        self.handle_command('rotate_left')
                    elif event.key == pygame.K_e:
                        self.handle_command('rotate_right')
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP and self.current_direction == 'forward':
                        self.handle_command('stop')
                    elif event.key == pygame.K_DOWN and self.current_direction == 'backward':
                        self.handle_command('stop')
                    elif event.key == pygame.K_LEFT and self.current_direction == 'left':
                        self.handle_command('stop')
                    elif event.key == pygame.K_RIGHT and self.current_direction == 'right':
                        self.handle_command('stop')
            
            command = self.bt_receiver.get_command()
            if command:
                self.handle_command(command)
            
            self.process_movements()
            self.update_timer()
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            camera_distance = 12
            camera_height = 6
            camera_angle = math.radians(self.fox.rotation[1])
            
            cam_x = self.fox.position[0] + math.sin(camera_angle) * camera_distance
            cam_z = self.fox.position[2] + math.cos(camera_angle) * camera_distance
            
            gluLookAt(
                cam_x, camera_height, cam_z,
                self.fox.position[0], self.fox.position[1] + 1, self.fox.position[2],
                0, 1, 0
            )
            
            self.environment.draw()
            self.fox.update_animation()
            self.fox.draw()
            
            self.draw_hud()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.bt_receiver.stop()
        pygame.quit()


if __name__ == '__main__':
    try:
        game = FoxTreasureHuntGame()
        game.run()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")