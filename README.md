# Eyevinn Toolbox

The Eyevinn Toolbox is a set of Docker containers with tools that may come in handy. They are all free to use and if you have any suggestions feel free to create a ticket.

| Tool      | Description | Container |
| ----      | ----------- | --------- |
| Loop TS   | Generate MPEG-TS stream over multicast or SRT by looping an MP4 file | eyevinntechnology/toolbox-loopts |
| SRT Tx    | Transport stream over SRT | eyevinntechnology/toolbox-srttx |
| SRT Rx    | Receive stream over SRT | eyevinntechnology/toolbox-srtrx |
| RTMP Rx   | Receive RTMP and stream over multicast | eyevinntechnology/toolbox-rtmprx |
| Mosaic TS | Render a 2x2 or 3x3 mosaic in MPEG-TS from 4 or 9 HLS sources | eyevinntechnology/toolbox-mosaicts |
| HLS 2 TS  | Pull a live HLS stream and output to multicast TS | eyevinntechnology/toolbox-hls2ts |
| HLS 2 RTMP | Pull a live HLS stream and re-stream to multiple RTMP destinations. | eyevinntechnology/toolbox-hls2rtmp |
| HLS 2 SRT | Pull a live HLS stream and transmit over SRT | eyevinntechnology/toolbox-hls2srt |
| SRT 2 RTMP | Receive an SRT stream and re-stream to multiple RTMP destinations. | eyevinntechnology/toolbox-srt2rtmp |
| RTMP 2 SRT | Receive an RTMP stream and transmit over SRT. | eyevinntechnology/toolbox-rtmp2srt |
| VOD Transcode | Quickly transcode video file to a set of different bitrates | eyevinntechnology/toolbox-transcode |

## Loop input file and output MPEG-TS multicast

```
$ docker run --rm -v $PWD:/mnt eyevinntechnology/toolbox-loopts IN.mp4 udp://239.0.0.1.1234?pkt_size=1316
```

where `$PWD` is your working directory where you have your input file.

The following options are available:

```
$ docker run --rm -v $PWD:/mnt eyevinntechnology/toolbox-loopts -h
usage: loopts.py [-h] [--workdir WORKDIR] [--framerate FRAMERATE]
                 [--kfinterval KFINTERVAL] [--bitrate BITRATE] [--hevc]
                 [--withtc] [--withaudio] [--nologo] [--useflv]
                 [--multibitrate]
                 inputfile multicast

Loop an MP4 file and output to MPEG-TS multicast

positional arguments:
  inputfile
  multicast

optional arguments:
  -h, --help              show this help message and exit
  --workdir WORKDIR       specify a working directory, default is /mnt
  --framerate FRAMERATE   output framerate (DEFAULT 25fps)
  --kfinterval KFINTERVAL specify keyframe interval (DEFAULT 2 sec)
  --bitrate BITRATE       specify video bitrate in kbps (e.g. 2500)
  --hevc                  use HEVC encoded output
  --withtc                burn in local timecode in video output
  --withaudio             adds a test tone on the audio track
  --nologo                remove logo
  --useflv                use FLV for RTMP output
  --multibitrate          output multiple video bitrates
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

### Output FLV over RTMP

To use RTMP instead of multicast you can run `loopts` and push with RTMP

```
docker run --rm -it -v $PWD:/mnt eyevinntechnology/toolbox-loopts --useflv IN.mp4 "rtmp://live.twitch.tv/app/live_*****"
```

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

```
$ docker run --rm eyevinntechnology/toolbox-srtrx -h
usage: srtrx.py [-h] [--listener] [--with-debug] inputaddress outputaddress

Receive MPEG-TS over SRT and restream over Multicast

positional arguments:
  inputaddress
  outputaddress

optional arguments:
  -h, --help     show this help message and exit
  --listener     run as SRT listener
  --passthrough  for low latency skip the unmux and mux step.
```

## Receive RTMP and restream over SRT

The `srttx` tool can be used to receive a local RTMP stream and restream to an `SRT Rx` over the Internet.

```
+------------------+                     +-----------------+                       +------------+
|  Wirecast &      |                     |                 |                       |            |
|  toolbox-srttx   | ===> INTERNET ===>  |  toolbox-srtrx  | ====> MULTICAST ====> | TRANSCODER |
|  <IP-TX>         |                     |  <IP-RX>        |                       |            |
+------------------+                     +-----------------+                       +------------+
```

On the transmitter side with for example Wirecast as producing the stream first start the `srttx` tool.

```
$ docker run --rm -p 1935:1935 eyevinntechnology/toolbox-srttx:0.2.4 input_stream <IP-RX>:9998 --passthrough
```

Then point the Wirecast / OBS output to `rtmp://localhost/live/input_stream`

On the receiver side you then run the following:

```
$ docker run --rm -p 9998:9998/udp -p <MULTICAST-PORT>:<MULTICAST-PORT>/udp eyevinntechnology/toolbox-srtrx --listener --passthrough 0.0.0.0:9998 <MULTICAST>:<MULTICAST-PORT>`
```

```
$ docker run --rm eyevinntechnology/toolbox-srttx:0.2.4 -h
usage: srttx.py [-h] [--inputtype INPUTTYPE] [--listener] [--passthrough]
                inputstream outputaddress

Receive RTMP and stream over SRT

positional arguments:
  inputstream
  outputaddress

optional arguments:
  -h, --help     show this help message and exit
  --inputtype INPUTTYPE type of input [rtmp|mpegts], default is rtmp  
  --listener     run as SRT listener
  --passthrough  passthrough input and skip encoding process
```

### MPEG-TS as a source

The `srttx` tool can also take an MPEG-TS as a source. Instead run the following command on the transmitter side. The receiver side as before.

```
$ docker run --rm eyevinntechnology/toolbox-srttx:0.2.4 <MULTICAST>:<MULTICAST-PORT> <IP-RX>:9998 --passthrough --inputtype=mpegts
```

## Receive RTMP and restream over Multicast

Use the `rtmprx` tool to receive RTMP and restream MPEG-TS over multicast if you want to use RTMP as the transport protocol with a live transcoder that for example only supports MPEG-TS multicast.

On the receiver side run the following command:

```
$ docker run --rm -p 1935:1935 -p <MULTICAST-PORT>:<MULTICAST-PORT>/udp eyevinntechnology/toolbox-rtmprx input_stream <MULTICAST>:<MULTICAST-PORT> --passthrough
```

```
$ docker run --rm eyevinntechnology/toolbox-rtmprx -h
usage: rtmprx.py [-h] [--passthrough] [--with-debug] inputstream outputaddress

Receive RTMP and restream over Multicast

positional arguments:
  inputstream
  outputaddress

optional arguments:
  -h, --help     show this help message and exit
  --passthrough  passthrough input and skip encoding process
```

## Render a Mosaic from HLS sources

Use the `mosaicts` tool to render a 2x2 or 3x3 mosaic of HLS sources.

```
$ docker run --rm eyevinntechnology/toolbox-mosaicts -h
usage: mosaicts.py [-h] [--port PORT] [--multicast MULTICAST] [--with-debug]
                   layout urlfile

Take multiple HLS sources and render a mosaic in MPEG-TS

positional arguments:
  layout                2x2|3x3
  urlfile               A text file containing URLs to HLS sources. One source
                        per line.

optional arguments:
  -h, --help            show this help message and exit
  --port PORT
  --multicast MULTICAST
                        Use multicast address specified here instead of SRT
```

To read the list of URLs from STDIN:

```
$ docker run --rm -i -p 9998:9998/udp eyevinntechnology/toolbox-mosaicts 2x2 - < urls.txt
```

## Pull a live HLS stream and output to multicast TS

Use the `hls2ts` tool to pull an HLS live stream and output to multicast TS.

```
$ docker run --rm eyevinntechnology/toolbox-hls2ts -h
usage: hls2ts.py [-h] [--srt] [--bitrate BITRATE] [--with-debug]
                 hlsurl outputaddress

Pull live HLS and output to multicast TS

positional arguments:
  hlsurl
  outputaddress

optional arguments:
  -h, --help         show this help message and exit
  --srt              use SRT as transport protocol
  --bitrate BITRATE  which bitrate to use
  --with-debug

```

Example:

```
docker run --rm eyevinntechnology/toolbox-hls2ts:0.1.0 HLSURL <MULTICAST>:<MULTICAST-PORT>
```

## Re-stream SRT to multiple RTMP destinations

Use the `srt2rtmp` tool to receive an SRT stream and re-stream to multiple RTMP destinations.

Example:

```
docker run --rm -p 1234:1234/udp eyevinntechnology/toolbox-srt2rtmp:0.1.1 0.0.0.0:1234 <RTMPURL1> <RTMPURL2>
```

## Pull a live HLS stream and output to multiple RTMP destinations

Use the `hls2rtmp` tool to pull a live HLS stream and re-stream to multiple RTMP destinations.

Example:

```
docker run --rm eyevinntechnology/toolbox-hls2rtmp:0.1.3 HLSURL <RTMPURL1> <RTMPURL2>
```

## Pull a live HLS stream and output to SRT

Use the `hls2srt` tool to pull a live HLS stream and make available over SRT.

Example:

```
docker run -d --restart always -p 1234:1234/udp eyevinntechnology/toolbox-hls2srt:0.1.1 HLSURL 0.0.0.0:1234
```

## Listen for an RTMP stream and output to SRT

Use the `rtmp2srt` tool to receive an RTMP stream and transmit over SRT.

Example:

```
docker run --rm -p 1935:1935 -p 1234:1234/udp eyevinntechnology/toolbox-rtmp2srt:0.1.1 <STREAMKEY> <IP>:1234
```

By deafult in SRT listener mode, to use SRT as a client:

```
docker run --rm -p 1935:1935 eyevinntechnology/toolbox-rtmp2srt:0.1.0 --caller <STREAMKEY> <IP>:1234
```

## VOD Transcode

Quickly transcode video file to a set of different bitrates.

```
docker run --rm -v $PWD:/media eyevinntechnology/toolbox-transcode:0.1.0 --framerate 24 videofile-720p.mp4
```

and it will generate three GOP-aligned MP4 files prepared to be chunked into segments.

# About Eyevinn Technology

Eyevinn Technology is an independent consultant firm specialized in video and streaming. Independent in a way that we are not commercially tied to any platform or technology vendor.

At Eyevinn, every software developer consultant has a dedicated budget reserved for open source development and contribution to the open source community. This give us room for innovation, team building and personal competence development. And also gives us as a company a way to contribute back to the open source community. 

Want to know more about Eyevinn and how it is to work here. Contact us at work@eyevinn.se!
