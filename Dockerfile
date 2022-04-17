FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip build-essential git

ENV LD_LIBRARY_PATH /usr/local/lib

RUN git clone https://github.com/fogleman/MisterQueen.git /root/MisterQueen
RUN cd /root/MisterQueen && make COMPILE_FLAGS="-std=c99 -Wall -O3 -fPIC" && cd ..
RUN gcc -shared -o /usr/local/lib/libmisterqueen.so /root/MisterQueen/build/release/*.o -lpthread
RUN gcc -shared -o /usr/local/lib/libtinycthread.so /root/MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread

RUN pip3 install cffi numpy

WORKDIR /root/
ADD build.py build.py
ADD main.py main.py
ADD chessenv.c chessenv.c
ADD chessenv.h chessenv.h

RUN python3 build.py
RUN python3 main.py
