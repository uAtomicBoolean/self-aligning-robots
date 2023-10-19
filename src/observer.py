import time
import pygame
import struct
import socket
from threading import Thread


GROUP = "224.1.1.1"
PORT = 25535
WHITE = (255, 255, 255)
RED = (255, 0, 0)

STOP_CODE = "STOP!"


class Receiver(Thread):

	def __init__(self):
		super().__init__()

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', PORT))

		mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		self.robots = dict()
		self.running = True
	
	def run(self):
		while self.running:
			try:
				msg = self.sock.recv(1024, socket.MSG_DONTWAIT)
			except:
				time.sleep(0.02)
			else:
				self.parse_message(msg.decode())
	
	def parse_message(self, msg: str):
		values = msg.split()
		r_id = values[0]

		if STOP_CODE in msg:
			return self.robots.pop(r_id)

		r_x, r_y = float(values[1]), float(values[2])
		self.robots[r_id] = (r_x, r_y)


pygame.init()

window = pygame.display.set_mode((1280, 720))
window.fill(WHITE)
pygame.display.flip()

receiver = Receiver()
receiver.start()

clock = pygame.time.Clock()

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key in (pygame.K_ESCAPE, pygame.K_q):
				running = False
	
	window.fill(WHITE)

	for r_id, pos in receiver.robots.items():
		pygame.draw.circle(window, RED, pos, 5)

	pygame.display.flip()

	clock.tick(60)

receiver.running = False
receiver.join()

pygame.quit()
