# Eyevinn Toolbox

The Eyevinn Toolbox is a set of Docker containers with tools that may come in handy. They are all free to use and if you have any suggestions feel free to create a ticket.

## Loop input file and output MPEG-TS multicast

```
$ docker run --rm -v $PWD:/mnt eyevinntechnology/toolbox-loopts IN.mp4 udp://239.0.0.1.1234?pkt_size=1316
```

where `$PWD` is your working directory where you have your input file.

The following options are available:

```
$ docker run --rm -v $PWD:/mnt eyevinntechnology/toolbox-loopts -h
usage: loopts.py [-h] [--workdir WORKDIR] [--framerate FRAMERATE] [--withtc]
                 [--withaudio]
                 inputfile multicast

Loop an MP4 file and output to MPEG-TS multicast

positional arguments:
  inputfile
  multicast

optional arguments:
  -h, --help             show this help message and exit
  --workdir WORKDIR      specify a working directory, default is /mnt
  --framerate FRAMERATE  output framerate (DEFAULT 25fps)
  --withtc               burn in local timecode in video
  --withaudio            adds a test tone on the audio track
```

To test this locally on your computer (Mac + VLC) assuming the file to loop is called IN.mp4 and in your working directory

```
$ docker run --rm -p 9998:9998/udp -v $PWD:/mnt eyevinntechnology/toolbox-loopts IN.mp4 udp://host.docker.internal:9998?pkt_size=1316 --withtc
```

Then open VLC with the following network address: `udp://@127.0.0.1:9998`

### Output MPEG-TS over SRT

To use SRT (Secure Reliable Transport) instead of multicast you can run `loopts` as an SRT listener.

```
docker run --rm -p 9998:9998/udp -v $PWD:/mnt eyevinntechnology/toolbox-loopts IN.mp4 "srt://0.0.0.0:9998?pkt_size=1316&mode=listener" --withtc
```

Then open VLC with the following network address: `srt://@127.0.0.1:9998`

## Receive MPEG-TS over SRT and restream over multicast

Use the `srtrx` tool to receive an MPEG-TS stream over SRT (Secure Reliable Transport) and restream over multicast. This can be used in the following scenario:

```
+-----------+                     +-----------------+                       +------------+
|           |                     |                 |                       |            |
|  SRT Tx   | ===> INTERNET ===>  |  toolbox-srtrx  | ====> MULTICAST ====> | TRANSCODER |
|           |                     |                 |                       |            |
+-----------+                     +-----------------+                       +------------+
```

Assuming that the `SRT Tx` is running in listener mode and can be reached on 10.0.110.178:9998 you start the restreamer with the following commmand:

```
$ docker run --rm -p 1234:1234/udp eyevinntechnology/toolbox-srtrx 10.0.110.178:9998 239.0.0.1:1234
```

This setup can be emulated by running loopts tool as the `SRT Tx` and VLC as the transcoder.

```
$ docker run --rm -p 9998:9998/udp -v $PWD:/mnt eyevinntechnology/toolbox-loopts IN.mp4 "srt://0.0.0.0:9998?pkt_size=1316&mode=listener" --withtc
```

```
$ docker run --rm -p 9999:9999/udp eyevinntechnology/toolbox-srtrx 10.0.110.178:9998 host.docker.internal:9999
```

where 10.0.110.178 is the IP of your computer running the loopts container.
