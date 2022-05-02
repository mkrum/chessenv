FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3.8 python3-pip build-essential git cmake

ENV LD_LIBRARY_PATH /usr/local/lib

RUN git clone https://github.com/fogleman/MisterQueen.git /root/MisterQueen
RUN cd /root/MisterQueen && make COMPILE_FLAGS="-std=c99 -Wall -O3 -fPIC" && cd ..
RUN gcc -shared -o /usr/local/lib/libmisterqueen.so /root/MisterQueen/build/release/*.o -lpthread
RUN gcc -shared -o /usr/local/lib/libtinycthread.so /root/MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread

RUN apt-get install -y python3.8-dev libffi-dev
RUN python3.8 -m pip install cython 
RUN python3.8 -m pip install cffi numpy

WORKDIR /root/
ADD build.py build.py
ADD setup.py setup.py
ADD src /root/src
ADD chessenv /root/chessenv

RUN python3.8 -m pip install -e .
RUN apt-get install 

RUN apt-get install -y clang-9 clang-tools-9
RUN export CMAKE_CXX_COMPILER=/usr/bin/clang++-9
RUN python3.8 -m pip install open_spiel || python3.8 -m pip install open_spiel
RUN python3.8 -m pip install chess
ADD benchmark.py /root/benchmark.py

