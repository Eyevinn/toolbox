#!/usr/bin/python2.7
#
# Loop input file and output to multicast TS
# Copyright 2019 Eyevinn Technology
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Loop an MP4 file and output to MPEG-TS multicast')
parser.add_argument('inputfile')
parser.add_argument('multicast')
parser.add_argument('--workdir', help='specify a working directory, default is /mnt')
parser.add_argument('--framerate', help='output framerate (DEFAULT 25fps)')
args = parser.parse_args()

workdir = '/mnt'
if args.workdir:
  workdir = args.workdir

framerate = '25'
if args.framerate:
  framerate = args.framerate

# ffmpeg -stream_loop -1 -i IN.mp4 -map 0:v -vcodec copy -bsf:v h264_mp4toannexb -f h264 - | ffmpeg -fflags +genpts -r 23.98 -re -i - -an -vcodec libx264 -preset veryfast -pix_fmt yuv420p -strict -2 -y -f mpegts 'udp://239.0.0.1:1234'
ffmpeg1 = "ffmpeg -stream_loop -1 -i %s/%s -map 0:v -vcodec copy -bsf:v h264_mp4toannexb -f h264 -" % (workdir, args.inputfile)
ffmpeg2 = "ffmpeg -fflags +genpts -r %s -re -i - -an -vcodec libx264 -preset veryfast -pix_fmt yuv420p -strict -2 -y -f mpegts %s" % (framerate, args.multicast)

p1 = subprocess.Popen(ffmpeg1.split(), stdout=subprocess.PIPE)
p2 = subprocess.Popen(ffmpeg2.split(), stdin=p1.stdout)
p1.stdout.close()

output,err = p2.communicate()
