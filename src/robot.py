import time
import string
import random
import socket
import struct

from threading import Thread

from typing import Callable



GROUP = "224.1.1.1"
PORT = 25535
TTL = 2

DELTA = 0.1

STOP_CODE = "STOP!"


class PositionTransmitter(Thread):
	def __init__(self, robot_id: str, get_robot_pos: Callable[[], str]):
		super().__init__()

		self.robot_id = robot_id
		self.get_robot_pos = get_robot_pos

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

		self.running = True

	def run(self):
		while self.running:
			self.sock.sendto(self.get_robot_pos().encode(), (GROUP, PORT))
			time.sleep(DELTA)
		self.sock.sendto(f"{self.robot_id} {STOP_CODE}".encode(), (GROUP, PORT))
		

class Receiver(Thread):

	def __init__(self, callback: Callable[[], str]):
		super().__init__()
		self.callback = callback
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', PORT))

		mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		self.running = True

	def run(self):
		while self.running:
			try:
				msg = self.sock.recv(1024, socket.MSG_DONTWAIT)
			except:
				time.sleep(DELTA / 2)
			else:
				self.callback(msg.decode())
		

class Robot(Thread):

	def __init__(self):
		super().__init__()

		self.id = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(10)])
		self.x = random.randint(10, 1270)
		self.y = random.randint(10, 710)
		self.size = (10, 10)

		self.speed_x = 0.5
		self.speed_y = 0.5

		self.transmitter = PositionTransmitter(self.id, self.get_pos_msg)
		self.receiver = Receiver(self.parse_pos_msg)

		self.robots_positions = dict()
		self.robots_count = 0

		self.running = True

	def get_pos_msg(self) -> str:
		return f"{self.id} {self.x} {self.y}"
	
	def parse_pos_msg(self, msg: str):
		values = msg.split()
		r_id = values[0]
		if r_id == self.id:
			return

		# Removing a robot that stopped operating.		
		if STOP_CODE in msg:
			return self.robots_positions.pop(r_id)
		
		r_x, r_y = float(values[1]), float(values[2])
		self.robots_positions[r_id] =  (r_x, r_y)

		if (new_len := self.robots_count != len(self.robots_positions)):
			self.calculate_dest()
			self.robots_count = new_len
	
	def calculate_dest(self):
		print("New destination : ")
		pass

	def run(self):
		while self.running:
			self.x += self.speed_x
			self.y += self.speed_y
			time.sleep(DELTA)
	
	def start_robot(self):
		self.receiver.start()
		self.transmitter.start()
		self.start()

	def stop(self):
		self.transmitter.running = False
		self.transmitter.join()

		self.running = False
		self.join()

		self.receiver.running = False
		self.receiver.join()
		print("Robot stopped. Goodbye !")
	
	def __str__(self) -> str:
		return f"Robot {self.id} at (x: {self.x:>4}, y: {self.y:>3})."


if __name__ == "__main__":
	robot = Robot()
	robot.start_robot()

	input("Press 'Enter' to stop the robot.\n")
	robot.stop()
