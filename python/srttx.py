#!/usr/bin/python2.7
#
# Receive RTMP and stream over SRT
# Copyright 2019 Eyevinn Technology
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Receive RTMP and stream over SRT')
parser.add_argument('inputstream')
parser.add_argument('outputaddress')
parser.add_argument('--listener', action='store_true', help='run as SRT listener')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

listenermode = ''
if args.listener:
  listenermode = '&mode=listener'

ffmpeg = "ffmpeg -fflags +genpts -listen 1 -re -i rtmp://0.0.0.0/live/%s -acodec copy -vcodec libx264 -preset veryfast -pix_fmt yuv420p -strict -2 -y -f mpegts srt://%s?pkt_size=1316%s" % (args.inputstream, args.outputaddress, listenermode)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()