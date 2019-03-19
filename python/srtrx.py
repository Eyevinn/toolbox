#!/usr/bin/python2.7
#
# Receive MPEG-TS over SRT and restream over Multicast
# Copyright 2019 Eyevinn Technology
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Receive MPEG-TS over SRT and restream over Multicast')
parser.add_argument('inputaddress')
parser.add_argument('outputaddress')
parser.add_argument('--listener', action='store_true', help='run as SRT listener')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

ffmpeg = "ffmpeg -re -i srt://%s -vcodec copy -acodec copy -strict -2 -y -f mpegts udp://%s?pkt_size=1316" % (args.inputaddress, args.outputaddress)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()