#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Pull live HLS and output to multicast TS
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Pull live HLS and output to multicast TS')
parser.add_argument('hlsurl')
parser.add_argument('outputaddress')
parser.add_argument('--srt', action='store_true', help='use SRT as transport protocol')
parser.add_argument('--channelbug', help='overlay logo as channel bug (poc)')
parser.add_argument('--bitrate', help='which bitrate to use')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

protocol = 'udp'
if args.srt:
  protocol = 'srt'

bitrate = ''
if args.bitrate:
  bitrate = "-map m:variant_bitrate:%s" % args.bitrate

ffmpeg = "ffmpeg -fflags +genpts -re -i %s %s -strict -2 -y -vcodec copy -f mpegts %s://%s?pkt_size=1316" % (args.hlsurl, bitrate, protocol, args.outputaddress)
if args.channelbug:
  ffmpeg = "ffmpeg -fflags +genpts -re -i %s -r 25 -i %s -filter_complex [0:1][1:v]#overlay=10:10:eval=init -c:v libx264 -preset ultrafast -strict -2 -y -f mpegts -max_muxing_queue_size 2048 %s://%s?pkt_size=1316" % (args.hlsurl, args.channelbug, protocol, args.outputaddress)


arglist = ffmpeg.split()
if args.debug:
  print "%s" % ffmpeg
  print map(lambda x: x.replace("#", " "), arglist)

p1 = subprocess.Popen(map(lambda x: x.replace("#", " "), arglist))
output,err = p1.communicate()