
from chessenv_c.lib import reset_env, print_board, get_boards, step_env, reset_env
from cffi import FFI
import chessenv_c
import numpy as np

ffi = FFI()


def boards(env):
    arr = np.zeros(shape=(env.N * 69), dtype=np.int32)
    get_boards(env, ffi.cast("int *", arr.ctypes.data))
    arr = arr.reshape(env.N, 69)
    return arr

def step(env, moves):
    rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    cols= ['1', '2', '3', '4', '5', '6', '7', '8']
    promos = [' ', 'n', 'b', 'r', 'q']

    move_arr = np.zeros(shape=(env.N * 5), dtype=np.int32)
    idx = 0
    for move in moves:
        move_arr[idx] = rows.index(move[0])
        move_arr[idx + 1] = cols.index(move[1])

        move_arr[idx + 2] = rows.index(move[2])
        move_arr[idx + 3] = cols.index(move[3])

        if len(moves) == 4:
            move_arr[idx + 4] = promos.index(move[4])
        else:
            move_arr[idx + 4] = 0

        idx += 5

    print(move_arr)
    step_env(env, ffi.cast("int *", move_arr.ctypes.data))

env = chessenv_c.ffi.new("T *")
reset_env(env, 5)

moves = ['e2e4' for _ in range(env.N)]
print_board(env)
print()
step(env, moves)
print("AFTER STEP")
print_board(env)
