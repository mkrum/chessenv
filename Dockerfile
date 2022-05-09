FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3.8 python3-pip build-essential git cmake clang-9 clang-tools-9

ENV LD_LIBRARY_PATH /usr/local/lib

RUN mkdir /workdir

RUN git clone https://github.com/fogleman/MisterQueen.git /workdir/MisterQueen
RUN cd /workdir/MisterQueen && make COMPILE_FLAGS="-std=c99 -Wall -O3 -fPIC" && cd ..
RUN gcc -shared -o /usr/local/lib/libmisterqueen.so /workdir/MisterQueen/build/release/*.o -lpthread
RUN gcc -shared -o /usr/local/lib/libtinycthread.so /workdir/MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread

RUN apt-get install -y python3.8-dev libffi-dev
RUN python3.8 -m pip install cython 
RUN python3.8 -m pip install cffi numpy

WORKDIR /workdir/
ADD build.py build.py
ADD setup.py setup.py
ADD src /workdir/src
ADD chessenv /workdir/chessenv

RUN python3.8 -m pip install -e .

RUN export CMAKE_CXX_COMPILER=/usr/bin/clang++-9
RUN python3.8 -m pip install open_spiel || python3.8 -m pip install open_spiel
RUN python3.8 -m pip install chess
ADD benchmark.py /workdir/benchmark.py
