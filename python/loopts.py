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
parser.add_argument('--withtc', action='store_true', help='burn in local timecode in video output')
parser.add_argument('--withaudio', action='store_true', help='adds a test tone on the audio track')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

workdir = '/mnt'
if args.workdir:
  workdir = args.workdir

framerate = '25'
if args.framerate:
  framerate = args.framerate

tcstr = ''
framestr = ''
if args.withtc:
  tcstr = ',drawtext=fontfile=/root/Vera.ttf:fontsize=200:text=\'%{localtime\\:%T}\':fontcolor=white@0.9:x=(w-tw)/2:y=250:shadowcolor=black:shadowx=2:shadowy=1'
  framestr = ',drawtext=fontfile=/root/Vera.ttf:fontsize=40:text=\'[%{n}/%{pts}]\':fontcolor=white@0.9:x=(w-tw)/2:y=h-th-10:shadowcolor=black:shadowx=2:shadowy=1'

branding = '-vf drawtext=fontfile=/root/Vera.ttf:fontsize=12:text=\'eyevinntechnology/toolbox-loopts\':fontcolor=white@0.9:x=20:y=20:shadowcolor=black:shadowx=2:shadowy=1'

audiostr = 'anullsrc=r=48000:cl=stereo'
if args.withaudio:
  audiostr = 'sine=frequency=1000:sample_rate=48000'

# ffmpeg -stream_loop -1 -i IN.mp4 -map 0:v -vcodec copy -bsf:v h264_mp4toannexb -f h264 - | ffmpeg -fflags +genpts -r 23.98 -re -i - -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -shortest -vcodec libx264 -preset veryfast -pix_fmt yuv420p -strict -2 -y -f mpegts 'udp://239.0.0.1:1234'
ffmpeg1 = "ffmpeg -stream_loop -1 -i %s/%s -map 0:v -vcodec copy -bsf:v h264_mp4toannexb -f h264 -" % (workdir, args.inputfile)
ffmpeg2 = "ffmpeg -framerate %s -fflags +genpts -r %s -re -i - -f lavfi -i %s -c:a aac -shortest %s%s%s -vcodec libx264 -preset veryfast -pix_fmt yuv420p -strict -2 -y -f mpegts -r %s %s" % (framerate, framerate, audiostr, branding, tcstr, framestr, framerate, args.multicast)

if args.debug:
  print "%s | %s" % (ffmpeg1, ffmpeg2)
  print ffmpeg1.split()
  print ffmpeg2.split()

p1 = subprocess.Popen(ffmpeg1.split(), stdout=subprocess.PIPE)
p2 = subprocess.Popen(ffmpeg2.split(), stdin=p1.stdout)
p1.stdout.close()

output,err = p2.communicate()
