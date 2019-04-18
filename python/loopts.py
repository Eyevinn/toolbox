#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Loop input file and output to multicast TS
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
parser.add_argument('--kfinterval', help='specify keyframe interval (DEFAULT 2 sec)')
parser.add_argument('--bitrate', help='specify video bitrate in kbps (e.g. 2500)')
parser.add_argument('--hevc', action='store_true', help='use HEVC encoded output')
parser.add_argument('--withtc', action='store_true', help='burn in local timecode in video output')
parser.add_argument('--withaudio', action='store_true', help='adds a test tone on the audio track')
parser.add_argument('--nologo', action='store_true', help='remove logo')
parser.add_argument('--useflv', action='store_true', help='use FLV for RTMP output')
parser.add_argument('--multibitrate', action='store_true', help='output multiple video bitrates')
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

branding = 'drawtext=fontfile=/root/Vera.ttf:fontsize=12:text=\'eyevinntechnology/toolbox-loopts\':fontcolor=white@0.9:x=20:y=20:shadowcolor=black:shadowx=2:shadowy=1'
if args.nologo:
  branding = ''

audiostr = '-f lavfi -i anullsrc=r=48000:cl=stereo'
if args.withaudio:
  audiostr = '-f lavfi -i sine=frequency=1000:sample_rate=48000'

audiocopy = '-map 0:v -vcodec copy'

kfinterval = float(framerate) * 2
forcekf = 2

if args.kfinterval:
  kfinterval = float(framerate) * float(args.kfinterval)
  forcekf = args.kfinterval

streamidstr = ''
overlayfilter = '-filter_complex [0:v]%s%s%s[overlay]' % (branding, tcstr, framestr)
scalefilter = '[overlay]scale=1280:720[out720]'
mapstr = '%s;%s -map [out720] -map 1:0' % (overlayfilter, scalefilter)

bitratestr = ''
if args.bitrate:
  bitratestr = '-b:v %sk -minrate %sk -maxrate %sk -bufsize %sk' % (args.bitrate, args.bitrate, args.bitrate, float(args.bitrate) / float(framerate))

outputencoding = '-vcodec libx264 -preset veryfast -pix_fmt yuv420p -g %s -keyint_min %s %s' % (kfinterval, kfinterval, bitratestr)
if args.hevc:
  outputencoding = '-vcodec libx265 -preset superfast -pix_fmt yuv420p -g %s -keyint_min %s %s' % (kfinterval, kfinterval, bitratestr)

if args.multibitrate:
  scalefilter = '[overlay]split=4[o1][o2][o3][o4];'
  scalefilter += '[o1]scale=480:360,drawtext=fontfile=/root/Vera.ttf:fontsize=12:text=\'480x360\':fontcolor=white@0.9:x=(w-tw)/2:y=20:shadowcolor=black:shadowx=2:shadowy=1[out360];'
  scalefilter += '[o2]scale=854:480,drawtext=fontfile=/root/Vera.ttf:fontsize=12:text=\'854x480\':fontcolor=white@0.9:x=(w-tw)/2:y=20:shadowcolor=black:shadowx=2:shadowy=1[out480];'
  scalefilter += '[o3]scale=1280:720,drawtext=fontfile=/root/Vera.ttf:fontsize=12:text=\'1280x720\':fontcolor=white@0.9:x=(w-tw)/2:y=20:shadowcolor=black:shadowx=2:shadowy=1[out720];'
  scalefilter += '[o4]scale=1920:1080,drawtext=fontfile=/root/Vera.ttf:fontsize=12:text=\'1920x1080\':fontcolor=white@0.9:x=(w-tw)/2:y=20:shadowcolor=black:shadowx=2:shadowy=1[out1080]'
  mapstr = '%s;%s -map [out360] -map 1:0 -map [out480] -map [out720] -map [out1080]' % (overlayfilter, scalefilter)
  outputencoding = '-c:v:0 libx264 -preset veryfast -pix_fmt yuv420p -g %s -keyint_min %s -force_key_frames expr:gte(t,n_forced*%s) -b:v:0 400k -maxrate 400k -bufsize %sk' % (kfinterval, kfinterval, forcekf, 400 / float(framerate))
  outputencoding += ' -c:v:1 libx264 -preset veryfast -pix_fmt yuv420p -g %s -keyint_min %s -force_key_frames expr:gte(t,n_forced*%s) -b:v:1 1000k -maxrate 1000k -bufsize %sk' % (kfinterval, kfinterval, forcekf, 1000 / float(framerate))
  outputencoding += ' -c:v:2 libx264 -preset veryfast -pix_fmt yuv420p -g %s -keyint_min %s -force_key_frames expr:gte(t,n_forced*%s) -b:v:2 2000k -maxrate 2000k -bufsize %sk' % (kfinterval, kfinterval, forcekf, 2000 / float(framerate))
  outputencoding += ' -c:v:3 libx264 -preset veryfast -pix_fmt yuv420p -g %s -keyint_min %s -force_key_frames expr:gte(t,n_forced*%s) -b:v:3 4500k -maxrate 4500k -bufsize %sk' % (kfinterval, kfinterval, forcekf, 4500 / float(framerate))

outputformat = 'mpegts'
if args.useflv:
  outputformat = 'flv'
  streamidstr = ''

# ffmpeg -stream_loop -1 -i IN.mp4 -map 0:v -vcodec copy -bsf:v h264_mp4toannexb -f h264 - | ffmpeg -fflags +genpts -r 23.98 -re -i - -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -shortest -vcodec libx264 -preset veryfast -pix_fmt yuv420p -strict -2 -y -f mpegts 'udp://239.0.0.1:1234'
ffmpeg1 = "ffmpeg -stream_loop -1 -i %s/%s %s -bsf:v h264_mp4toannexb -f h264 -" % (workdir, args.inputfile, audiocopy)
ffmpeg2 = "ffmpeg -thread_queue_size 512 -threads 4 -framerate %s -fflags +genpts -r %s -re -i - %s %s -c:a aac -shortest %s -strict -2 -y -f %s -r %s %s %s" % (framerate, framerate, audiostr, mapstr, outputencoding, outputformat, framerate, streamidstr, args.multicast)

if args.debug:
  print "%s | %s" % (ffmpeg1, ffmpeg2)
  print ffmpeg1.split()
  print ffmpeg2.split()

p1 = subprocess.Popen(ffmpeg1.split(), stdout=subprocess.PIPE)
p2 = subprocess.Popen(ffmpeg2.split(), stdin=p1.stdout)
p1.stdout.close()

output,err = p2.communicate()
