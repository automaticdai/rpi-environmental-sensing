#!/usr/bin/env python3

import argparse
import requests
import json

from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from font_intuitive import Intuitive
from inky import InkyPHAT, InkyWHAT


# Command line arguments to set display type and colour, and enter your name

#parser = argparse.ArgumentParser()
#parser.add_argument('--type', '-t', type=str, required=True, choices=["what", "phat"], help="type of display")
#parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
#parser.add_argument('--name', '-n', type=str, required=True, help="Your name")
#args = parser.parse_args()

#colour = args.colour

# Set up the correct display and scaling factors

inky_display = InkyPHAT("red")
scale_size = 1
padding = 0


# inky_display.set_rotation(180)
inky_display.set_border(inky_display.RED)

# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the fonts

intuitive_font = ImageFont.truetype(HankenGroteskBold, int(18 * scale_size))
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(28 * scale_size))
hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(16 * scale_size))

# Grab the name to be displayed

name = "Steven"

link = "http://192.168.1.120/cgi-bin/main.py"
f = requests.get(link)
print(f.text)

d = json.loads(f.text)
print(d["Date"])
print(d["Time"])
print(d["Temperature"])
print(d["Humidity"])


# Top and bottom y-coordinates for the white strip

y_top = int(inky_display.HEIGHT * (5.0 / 10.0))
y_bottom = y_top + int(inky_display.HEIGHT * (4.0 / 10.0))

# Draw the red, white, and red strips

for y in range(0, y_top):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.RED)

for y in range(y_top, y_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

for y in range(y_bottom, inky_display.HEIGHT):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.RED)

# Calculate the positioning and draw the "Hello" text

text1 = d["Date"]
hello_w, hello_h = hanken_bold_font.getsize(text1)
hello_x = int((inky_display.WIDTH - hello_w) / 2)
hello_y = 0 + padding
draw.text((hello_x, hello_y), text1, inky_display.WHITE, font=hanken_bold_font)

# Calculate the positioning and draw the "my name is" text

text2 = d["Time"]
mynameis_w, mynameis_h = hanken_medium_font.getsize(text2)
mynameis_x = int((inky_display.WIDTH - mynameis_w) / 2)
mynameis_y = hello_h + padding
draw.text((mynameis_x, mynameis_y), text2, inky_display.WHITE, font=hanken_medium_font)

# Calculate the positioning and draw the name text

name = d["Temperature"] + "C   " + d["Humidity"] + "%"
name_w, name_h = intuitive_font.getsize(name)
name_x = int((inky_display.WIDTH - name_w) / 2)
name_y = int(y_top + ((y_bottom - y_top - name_h) / 2))
draw.text((name_x, name_y), name, inky_display.BLACK, font=intuitive_font)

# Display the completed name badge

inky_display.set_image(img)
inky_display.show()
