import os, sys; os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
if sys.platform in ["win32", "win64"]: os.environ["SDL_VIDEO_CENTERED"]='1'
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (967,30)
import pygame
from pygame.locals import *
from pygame import *
import pygame.gfxdraw
import numpy as np
import random

pygame.display.init()
pygame.font.init()
pygame.init()

screen = width, height = (1400, 800)
surface = pygame.display.set_mode(screen)
pygame.display.set_caption("test")

fonts = {
    16 : pygame.font.SysFont("Times New Roman", 16, True),
    24 : pygame.font.SysFont("Times New Roman", 24, True),
    32 : pygame.font.SysFont("Times New Roman", 32, True)
}

BLACK = (0, 0, 0)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)
RED = (255, 55, 0)
GREEN = (10, 255, 80)
PURPLE = (255, 50, 255)

running = True
target_fps = 120
target_tick = 17
clean_pass = False
print_collision_info = False
dt = 0
clock = pygame.time.Clock()

def pause(msg="simulation paused, any key to resume"):
	input(msg)

def npify(val):
	return np.array(val, dtype='float64')

def normalize(v):
	return v / np.linalg.norm(v)

mag = np.linalg.norm

#projection of vector u onto vector v
def project_onto(u, v):
	return npify((0,0)) if mag(u) == 0 or mag(v) == 0 else (np.dot(u,v)/np.dot(v,v))*v

class Ball():
	def __init__(self, pos, vel, radius=30, color=WHITE):
		self.pos = npify(pos)
		self.vel = npify(vel)
		self.radius = radius
		self.color = color
		self.recent_partner = None

	def __repr__(self):
		return f"pos: ({self.pos.tolist()})\nvel: <{self.vel.tolist()}>"

	def move(self, du):
		self.pos += (self.vel * du)
		x = self.pos[0]
		y = self.pos[1]
		dx = self.vel[0]
		dy = self.vel[1]

		if x > screen[0] - self.radius:
			x = screen[0] - self.radius
			dx *= -1
			self.recent_partner = None
		elif x < 0 + self.radius:
			x = 0 + self.radius
			dx *= -1
			self.recent_partner = None
		if y > screen[1] - self.radius:
			y = screen[1] - self.radius
			dy *= -1
			self.recent_partner = None
		elif y < 0 + self.radius:
			y = 0 + self.radius
			dy *= -1
			self.recent_partner = None

		self.pos = npify((x,y))
		self.vel = npify((dx, dy))

	def add_force(self, force):
		self.vel += npify(force)

	def set_vel(self, vel):
		self.vel = npify(vel)

	def set_pos(self, pos):
		self.vel = npify(pos)

	def draw(self):
		pygame.draw.circle(surface, self.color, self.pos.astype('int32').tolist(), self.radius, 2)

	def ball_dist(self, other):
		return np.linalg.norm(other.pos - self.pos)

	def set_partner(self, other):
		self.recent_partner = other

	def not_partners(self, other):
		return not self.recent_partner == other

def rand_pos(xrange, yrange):
	xmin,xmax = xrange
	ymin,ymax = yrange

	xrand = random.randrange(xmin,xmax)
	yrand = random.randrange(ymin,ymax)

	return [xrand, yrand]

def rand_vel(min_mag=1, max_mag=10):
	#random.randint(-1,1,2) step of 2 would skip 0?
	xrand_sign = -1 if random.randint(0,1) == 0 else 1
	xrand_mag = random.randrange(min_mag, max_mag)

	yrand_sign = -1 if random.randint(0,1) == 0 else 1
	yrand_mag = random.randrange(min_mag, max_mag)

	return [xrand_mag * xrand_sign, yrand_mag * yrand_sign]

def rand_color():
	return [random.randint(10,255),random.randint(10,255),random.randint(10,255)]

def ball_gen(n):
	return [Ball(rand_pos((0,screen[0]),(0,screen[1])), rand_vel(), color=rand_color()) for i in range(n)]

"""Two Balls, one zero velocity"""
#balls = [Ball((100,300), (1,0), color=WHITE), Ball((200, 300), (0,0), color=PURPLE)]
"""Two Balls, unit velocity"""
#balls = [Ball((100,300), (1,0), color=WHITE), Ball((500, 300), (-1,0), color=PURPLE)]
"""Two Balls, non trivial velocity"""
#balls = [Ball((100,300), (1,0), color=WHITE), Ball((500, 300), (-10,0), color=PURPLE)]
"""Three Balls, non trivial velocity"""
#balls = [Ball((100,300), (1,0), color=WHITE), Ball((500, 300), (-10,0), color=PURPLE), Ball((1000, 300), (-1,0), color=GREEN)]
"""Two Balls, non trivial angle of collision"""
#balls = [Ball((100,300), (1,0), color=WHITE), Ball((500, 295), (-1,0), color=PURPLE)]
"""Two Balls, non trivial angle of collision, non trivial velocity"""
#balls = [Ball((100,300), (1,0), color=WHITE), Ball((500, 295), (-10,0), color=PURPLE)]
"""Two Balls, non trivial angle of collision, non trivial velocity"""
#balls = [Ball((100,100), (1,1), color=WHITE), Ball((500, 500), (-7,-7), color=PURPLE)]
"""Two Balls, non trivial angle of collision, non trivial velocity"""
#balls = [Ball((100,100), (1,2), color=WHITE), Ball((500, 530), (-7,-7), color=PURPLE)]
"""Two Balls, non trivial angle of collision, non trivial velocity"""
balls = [Ball((100,200), (1,-1), color=WHITE), Ball((200, 200), (-1,-1), color=PURPLE)]
"""50 Random Balls"""
#balls = ball_gen(50)

def get_input():
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE: return False
	return True


def update():
	global balls, clean_pass
	surface.fill(BLACK)
	du = dt / target_tick

	clean_pass = True
	for i,ball in enumerate(balls):
		ball.move(du)
		ball.draw()
		for j,ball2 in enumerate(balls):
			if (not ball == ball2 or not i == j) and ball.not_partners(ball2) :
				if ball.ball_dist(ball2) <= ball.radius + ball2.radius:
					clean_pass = False
					ball.set_partner(ball2)
					ball2.set_partner(ball)
					if print_collision_info:
						print("collided")
						print()
						print("ball\n", ball)
						print()
						print("ball2\n", ball2)
						print("================BEFORE================")

					f1 = ball.vel
					f2 = ball2.vel

					#ball 1
					norm1 = (ball2.pos - ball.pos) / 2

					projnf1 = project_onto(f1, norm1)

					newf1 = f1 - projnf1
					newf2 = f2 + projnf1

					#ball 2
					norm2 = (ball.pos - ball2.pos) / 2

					projnf2 = project_onto(f2, norm2)

					newf1 += projnf2
					newf2 -= projnf2

					#update real positions
					ball.vel = newf1
					ball2.vel = newf2
					if print_collision_info:
						print("================AFTER================")
						print("ball\n", ball)
						print()
						print("ball2\n", ball2)
						print()
					#pause()

	pygame.display.flip()
	return True

def main():
	global running,dt
	while running:
		dt = clock.tick(target_fps)
		if not get_input(): running = False
		if not update(): running = False

main()










