#!/bin/usr/python3
from PIL import Image, ImageDraw
from enum import Enum
import numpy
import sys, os
import requests as r

class CodeType(Enum):
	BITMOJI = 1			# 19x19
	EIGHTEEN = 2		# 18x18

# C in POSITIONS[R] => R,C is a valid position of a dot in the 19x19 snapcode grid
POSITIONS = [[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], [0, 1, 2, 3, 4, 5, 13, 14, 15, 16, 17, 18], [0, 1, 2, 3, 4, 14, 15, 16, 17, 18], [0, 1, 2, 3, 15, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 16, 17, 18], [0, 1, 2, 3, 15, 16, 17, 18], [0, 1, 2, 3, 4, 14, 15, 16, 17, 18], [0, 1, 2, 3, 4, 5, 13, 14, 15, 16, 17, 18], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]

SIZE = 19

# C in POSITIONS-18[R] => R,C is a valid position of a dot in the 18x18 snapcode grid
POSITIONS_18 = [[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16], [0, 1, 2, 3, 14, 15, 16, 17], [0, 1, 2, 3, 4, 13, 14, 15, 16, 17], [0, 1, 2, 3, 4, 13, 14, 15, 16, 17], [0, 1, 2, 3, 4, 13, 14, 15, 16, 17], [0, 1, 2, 15, 16, 17], [0, 1, 2, 15, 16, 17], [0, 1, 2, 3, 14, 15, 16, 17], [0, 1, 2, 3, 14, 15, 16, 17], [0, 1, 2, 15, 16, 17], [0, 1, 16, 17], [0, 1, 16, 17], [0, 1, 2, 3, 14, 15, 16, 17], [1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]]

DATA_ORDER = [(16,5), (17,6), (17,5), (16,6), (18,5), (18,6), (0,7), (1,8), (1,7), (0,8), (2,7), (2,8), (16,3), (17,4), (17,3), (16,4), (18,3),(18,4),(0,5),(1,6), (0,6), (1,5), (2,6), (2,5), (4,16), (5,17), (5,16), (4,17), (4,18), (5,18), (4,0), (5,1), (4,1), (5,0), (4,2), (5,2), (16,16), (17,16), (16,17), (17,17), (16,18), (18,16), (16,0), (17,1), (16,1), (17,2), (16,2), (18,2), (14,16), (15,17), (14,17), (15,18), (14,18), (15,16), (14,0), (15,1), (14,1), (15,2), (14,2), (15,0), (0,3), (1,4), (1,3), (0,4), (2,3), (2,4), (12,16), (13,17), (12,17), (13,18), (12,18), (13,16), (12,0), (13,1), (12,1), (13,2), (12,2), (13,0), (8,16), (9,17), (8,17), (9,18), (8,18), (9,16), (8,0), (9,1), (8,1), (9,2), (8,2), (9,0), (3,13), (4,14), (3,14), (3,15), (4,15), (5,15), (3,3), (4,3), (3,4), (4,4), (3,5), (5,3), (15,13), (14,14), (15,14), (13,15), (14,15), (15,15), (13,3), (14,4), (15,3), (14,3), (15,4), (15,5), (10,16), (11,17), (10,17), (11,18), (10,18), (11,16), (10,0), (11,1), (10,1), (11,2), (10,2), (11,0), (0,2), (1,2)]

DATA_ORDER_18 = [(8, 17), (10, 16), (9, 17), (8, 16), (10, 17), (9, 16), (8, 2), (10, 3), (9, 2), (11, 2), (9, 3), (10, 2), (8, 15), (10, 14), (9, 15), (11, 15), (9, 14), (10, 15), (11, 1), (13, 0), (12, 1), (11, 0), (13, 1), (12, 0), (11, 17), (13, 16), (12, 17), (11, 16), (13, 17), (12, 16), (8, 1), (10, 0), (9, 1), (8, 0), (10, 1), (9, 0), (16, 2), (14, 1), (15, 2), (16, 1), (14, 0), (15, 1), (6, 15), (7, 17), (6, 16), (7, 15), (6, 17), (7, 16), (16, 15), (14, 16), (15, 15), (16, 16), (14, 17), (15, 16), (6, 0), (7, 2), (6, 1), (7, 0), (6, 2), (7, 1), (14, 2), (15, 5), (14, 3), (15, 4), (15, 3), (15, 6), (4, 14), (6, 13), (5, 14), (4, 13), (6, 14), (5, 13), (14, 15), (15, 12), (14, 14), (15, 13), (15, 14), (15, 11), (4, 4), (6, 3), (5, 4), (4, 3), (6, 4), (5, 3), (16, 3), (17, 5), (16, 4), (17, 3), (16, 5), (17, 4), (4, 15), (5, 17), (4, 16), (5, 15), (4, 17), (5, 16), (16, 12), (17, 14), (16, 13), (17, 12), (16, 14), (17, 13), (4, 0), (5, 2), (4, 1), (5, 0), (4, 2), (5, 1), (16, 6), (17, 8), (16, 7), (17, 6), (16, 8), (17, 7), (2, 14), (3, 13), (2, 13), (3, 15), (2, 12), (3, 14), (16, 9), (17, 11), (16, 10), (17, 9), (16, 11), (17, 10), (2, 3), (3, 4)]

USERNAME_DATA = [[46, 47, 48, 33, 34, 35],[56, 41, 42, 43, 44, 45],[50, 51, 52, 53, 54, 55],[60, 61, 62, 63, 64, 49],[70, 71, 72, 57, 58, 59],[80, 65, 66, 67, 68, 69],[74, 75, 76, 77, 78, 79],[84, 85, 86, 87, 88, 73],[94, 95, 96, 81, 82, 83],[104, 89, 90, 91, 92, 93],[98, 99, 100, 101, 102, 103],[108, 109, 110, 111, 112, 97],[118, 119, 120, 105, 106, 107],[128, 113, 114, 115, 116, 117],[122, 123, 124, 125, 126, 127]]

CHAR_MAP = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18: 'i', 19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o', 25: 'p', 26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u', 31: 'v', 32: 'w', 33: 'x', 34: 'y', 35: 'z', 0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 36: '-', 37: '_', 38: '.'  }

# Load an image file
def load(path):
	img = Image.open(path,'r')
	w, h = img.size
	pixel_values = list(img.getdata())
	if (img.mode == "RGBA"):
		pixels = numpy.array(pixel_values).reshape((w,h,4))
	else:
		pixels = numpy.array(pixel_values).reshape((w,h,3))
	return pixels

# Returns True if the pixel corresponding to the grid position is black (0,0,0)
def check_position(pixels, r, c, x0=72, dx=49):
	return (pixels[int(x0)+int(r*dx),int(x0)+int(c*dx)] == 0)[:3].all()


# Load the image file at path, marking dots as ones and empty spaces as zeros in a 2D array
def scan(path, size=1024):
	# These are values I found by trial and error for various common sizes of Snapcode
	if (size == 1024):
		x0, dx = 72, 49
	elif (size == 320):
		x0, dx = 23, 15.3
	elif (size == 150):
		x0, dx = 8.4, 7.33333333333
	elif (size == 500):
		x0, dx = 28.5, 24.5
	else:
		x0, dx = 10, 13

	pixels = load(path)
	dots = numpy.zeros(shape=(SIZE,SIZE))
	for r in range(len(POSITIONS)):
		for c in POSITIONS[r]:
			if (check_position(pixels,r,c, x0, dx)):
				dots[r,c]=1
	return dots

def scan_18(path, size=256):
	if size == 256:
		x0, dx = 11, 13.6
	elif size == 500:
		x0, dx = 30, 26
	elif (size == 320):
		x0, dx = 19, 16.5

	pixels = load(path)
	dots = numpy.zeros(shape=(18,18))
	for r in range(18):
		for c in POSITIONS_18[r]:
			if (check_position(pixels,r,c, x0, dx)):
				dots[r,c]=1
	return dots


# Print a reconstructed snapcode to the terminal based on a 2D array
def ascii_print(dots):
	for r in range(len(dots)):
		print(' '.join(['O' if x == 1 else '.' for x in dots[r]]))

# Generate a snapchat-readable snapcode based on a 2D array
def generate_snapcode(dots, outfile, type=CodeType.BITMOJI):
	if type == CodeType.BITMOJI:
		pos = POSITIONS
		size = 19
		img = Image.new('RGB',(320,320),(255,252,0))
		x0, dx = 23, 15

	elif type == CodeType.EIGHTEEN:
		pos = POSITIONS_18
		size = 18
		img = Image.open('template18.png','r')
		x0, dx = 30, 26

	draw = ImageDraw.Draw(img)

	for r in range(size):
		for c in range(size):
			x = x0 + (dx*c)
			y = x0 + (dx*r)
			# Black circle
			if dots[r,c] == 1:
				draw.ellipse((x-2,y-2, x+10, y+10), fill=(0,0,0), outline=(0,0,0))
			# White circle
			elif dots[r,c] == -1 and c in pos[r]:
				draw.ellipse((x,y, x+10, y+10), fill=(255,255,255), outline=(0,0,0))
			elif c in pos[r]:
				draw.ellipse((x,y, x+10, y+10), fill=(255,0,0), outline=(0,0,0))
	img.save(outfile,quality=95)

# Takes an iterable of 2D arrays
# Returns a 2D array with cells that have value:
#	1, if the dot is present in all input arrays
#	-1, if the dot is present in none of the input arrays AND include_inverse is set to True
#	0, if the dot is present in some but not all input arrays
def intersection(all_dots, size=19, include_inverse=True):
	dots_intersection = numpy.zeros(shape=(size,size))
	for r in range(size):
		for c in range(size):
			x = numpy.array([dots[r,c] == 1 for dots in all_dots])
			if x.all():
				dots_intersection[r,c] = 1
			elif include_inverse and (~x).all():
				dots_intersection[r,c] = -1
	return dots_intersection

# Return a list of ints [0,1] whose value represents the raw bits stored in the snapcode
def get_bits(dots, type=CodeType.BITMOJI):
	if type == CodeType.BITMOJI:
		return [int(dots[p]) for p in DATA_ORDER]
	elif type == CodeType.EIGHTEEN:
		return [int(dots[p]) for p in DATA_ORDER_18]
	else:
		print("Error: unrecognized CodeType")

# Return a bitstring representing the raw bits stored in the snapcode
def get_bitstring(dots, include_inverse=False, type=CodeType.BITMOJI):
	a = get_bits(dots, type=type)
	if (include_inverse):
		m = {0:'x', 1:'1', -1:'0'}
		return ''.join([m[i] for i in a])
	else:
		return ''.join([str(i) for i in a])

# Decode a Snapcode bitstring to the underlying username
def get_username(string):
	username = ''
	for arr in USERNAME_DATA:
		bits = ''.join([ string[x-1] for x in arr  ])
		val = int(bits,2)
		if val in CHAR_MAP.keys():
			username += CHAR_MAP[val]
		else:
			return username

# Decode bitstring to UUID
def get_uuid(string):
	return hex(int(string,2))[2:]

'''
# POC:

dots = scan('aaaaa-ggg.png', size=1024)
username = get_username(get_bitstring(dots))
print (f"Username='{username}'. Visit 'https://www.snapchat.com/add/{username}' for the user's current snapcode.")

dots = scan('bright_white.png', size=320)
uuid = get_uuid(get_bitstring(dots))
print(f"UUID='{uuid}'. Visit 'https://www.snapchat.com/unlock/?type=SNAPCODE&uuid={uuid}' for confirmation.")
'''
