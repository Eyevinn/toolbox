#!/usr/bin/python2.7
#
# Copyright 2020 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Receive RTMP and restream over SRT
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Receive RTMP and restream over multicast')
parser.add_argument('streamkey', help='RTMP stream key (path)')
parser.add_argument('address', help='SRT address (IP:PORT)')
parser.add_argument('--caller', dest='caller', action='store_true', help='SRT in caller mode (default listener)')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

mode = '&mode=listener'
if args.caller:
  mode = ''

ffmpeg = "ffmpeg -fflags +genpts -listen 1 -re -i rtmp://0.0.0.0/rtmp/%s -acodec copy -vcodec copy -strict -2 -y -f mpegts srt://%s?pkt_size=1316%s" % (args.streamkey, args.address, mode)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()