FROM ubuntu:20.04
COPY . /app
ENV TZ Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install git cmake python3 build-essential
RUN apt-get update && apt-get -y install libsuitesparse-dev libmetis-dev libgmp-dev libgl1-mesa-dev xorg-dev libglu1-mesa-dev libboost-all-dev
RUN mkdir /app/build
RUN cd /app/build && cmake -DCMAKE_BUILD_TYPE=Release ..
RUN cd /app/build && make -j4
