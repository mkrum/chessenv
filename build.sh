
git clone https://github.com/fogleman/MisterQueen.git ./MisterQueen
cd ./MisterQueen && make COMPILE_FLAGS="-std=c99 -Wall -O3 -fPIC" && cd ..
gcc -shared -o /usr/local/lib/libmisterqueen.so ./MisterQueen/build/release/*.o -lpthread
gcc -shared -o /usr/local/lib/libtinycthread.so ./MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread

pip install -e .
