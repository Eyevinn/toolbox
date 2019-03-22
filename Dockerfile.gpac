FROM ubuntu:14.04
MAINTAINER Eyevinn Technology <info@eyevinn.se>
RUN apt-get update
RUN apt-get install -y --force-yes subversion make pkg-config \
  g++ zlib1g-dev libfreetype6-dev libjpeg62-dev libpng12-dev \
  libopenjpeg-dev libmad0-dev libfaad-dev libogg-dev libvorbis-dev \
  libtheora-dev liba52-0.7.4-dev libavcodec-dev libavformat-dev \
  libavutil-dev libswscale-dev libavresample-dev libxv-dev x11proto-video-dev \
  libgl1-mesa-dev x11proto-gl-dev linux-sound-base libxvidcore-dev libssl-dev \
  libjack-dev libasound2-dev libpulse-dev libsdl1.2-dev dvb-apps libavcodec-extra \
  libavdevice-dev libmozjs185-dev
RUN apt-get install -y --force-yes git
RUN mkdir /root/source
RUN apt-get install -y --force-yes libx264-dev
RUN apt-get install -y --force-yes yasm
RUN apt-get install -y --force-yes wget
RUN mkdir /root/source/ffmpeg
RUN apt-get install -y --force-yes libssl-dev
RUN apt-get install -y --force-yes cmake
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes tclsh
RUN cd /root/source/ffmpeg && \
  git clone https://github.com/Haivision/srt.git && \
  cd srt && \
  ./configure && \
  make && make install && \
  ldconfig
RUN cd /root/source/ffmpeg && \
  wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
  tar xjvf ffmpeg-snapshot.tar.bz2 && \
  cd ffmpeg && \
  ./configure \
    --enable-gpl \
    --enable-shared \
    --enable-libx264 \
    --enable-libsrt \
    --enable-version3 \
    --enable-nonfree && \
  make && \
  make install && \
  make distclean && \
  hash -r
RUN cd /root/source/ && \
  git clone https://github.com/gpac/gpac.git && \
  cd gpac && \
  ./configure && \
  make && \
  make install && \
  hash -r
RUN echo /usr/local/lib/x86_64-linux-gnu >> /etc/ld.so.conf.d/x86_64-linux-gnu.conf
RUN ldconfig
