FROM eyevinntechnology/ffmpeg-base:0.1.3
MAINTAINER Eyevinn Technology <info@eyevinn.se>
RUN apt-get update
RUN apt-get install -y --force-yes libgstreamer1.0-0 gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x \
  gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 \
  gstreamer1.0-pulseaudio

