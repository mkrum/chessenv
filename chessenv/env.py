import time
from dataclasses import dataclass

import chess
from cffi import FFI
import chessenv_c
import numpy as np

from typing import List

from chessenv_c.lib import (
    reset_env,
    get_mask,
    get_boards,
    step_env,
    reset_env,
    generate_random_move,
    generate_stockfish_move,
    reset_and_randomize_boards,
    create_sfarray,
    clean_sfarray,
    get_possible_moves,
)

from chessenv.rep import CMoves, CBoards


class CChessEnv:
    """
    Base RL Environment

    RL environment, implents the standard "OpenAI" like API. Includes
    pre-computing a move mask, adding a move limit cap, and randomizing the
    starting position.

    Example
    -------
    >>> env = CChessEnv(10)
    >>> state, mask = env.reset()
    >>> state.shape
    (10, 69)
    >>> mask.shape
    (10, 5632)
    >>> action = ...
    >>> state, mask, reward, done = env.step(action)

    Parameters
    ----------
    max_steps: int
        Total number of moves before restart
    draw_reward: float
        Reward to return on draw/time limit 
    min_random: int
        minimum number of random moves to apply to the starting board
    max_random: int
        maximum number of random moves to apply to the starting board
    """
    def __init__(self, n, max_step=100, draw_reward=0, min_random=0, max_random=0):
        self.ffi = FFI()
        self.n = n
        self.max_step = max_step
        self.draw_reward = draw_reward
        self._env = chessenv_c.ffi.new("Env *")
        self.min_random = min_random
        self.max_random = max_random

        self.t = np.zeros(self.n)

    def reset(self):
        """
        Resets the environment, returns the new intial states.

        Returns
        -------
        state: np.array
            (N, 69) vector representing the board state
        mask: np.array
            (N, 5632) vector represeting the move mask 
        """
        self.t = np.zeros(self.n)
        reset_env(self._env, self.n)
        mask = self.get_mask()
        return self.get_state(), mask


    def step(self, move_arr):
        """
        Steps the environment foward one timestep.

        Returns
        -------
        state: np.array
            (N, 69) vector representing the board state
        mask: np.array
            (N, 5632) vector represeting the move mask 
        reward: np.array
            (N, 1) vector represeting the reward
        done: np.array
            (N, 1) vector represeting wether or not it was a "done" transition
        """
        done_one, my_reward = self.push_moves(move_arr)
        response = self.sample_opponent()
        done_two, their_reward = self.push_moves(response)

        reward = my_reward - (1 - done_one) * (their_reward)

        reward[(self.t > self.max_step)] = self.draw_reward

        total_done = ((done_one + done_two) > 0) | (self.t > self.max_step)
        self.t[(total_done == 1)] = 0

        self.reset_boards(total_done)

        mask = self.get_mask()
        state = self.get_state()

        return state, mask, reward, total_done

    def push_moves(self, move_arr):
        """
        Applies a move_arr to the environment, and resets. Implements a lower
        level version of step to be used for mutliagent training.

        Parameters
        ----------
        move_arr: np.array
            (N, 1) array of move integers

        Returns
        -------
        done : np.array
            (N, 1) array of done bools
        reward : np.array
            (N, 1) array of done bools
        """
        done = self._make_vec_arr()
        reward = self._make_vec_arr()

        self.t += 1

        step_env(
            self._env,
            self.ffi.cast("int *", move_arr.ctypes.data),
            self.ffi.cast("int *", done.ctypes.data),
            self.ffi.cast("int *", reward.ctypes.data),
        )

        reset_and_randomize_boards(self._env, self.ffi.cast("int *", done.ctypes.data), self.min_random, self.max_random)
        return done, reward

    def get_state(self):
        board_arr = self._make_board_arr()
        get_boards(self._env, self.ffi.cast("int *", board_arr.ctypes.data))
        return board_arr.reshape(self.n, 69)

    def get_mask(self):
        mask_arr = self._make_mask_arr()
        get_mask(self._env, self.ffi.cast("int *", mask_arr.ctypes.data))
        return mask_arr.reshape(self.n, 88 * 64)

    def random(self):
        move_arr = self._make_move_arr()
        generate_random_move(self._env, self.ffi.cast("int *", move_arr.ctypes.data))
        return move_arr

    def sample_opponent(self):
        return self.random()

    def reset_boards(self, done):
        done = np.int32(done)
        reset_and_randomize_boards(self._env, self.ffi.cast("int *", done.ctypes.data), self.min_random, self.max_random)
        self.t[(done == 1)] = 0

    def step_moves(self, moves):
        move_arr = CMoves.from_str(moves).to_int()
        return self.step_arr(move_arr)

    def _make_board_arr(self):
        return np.zeros(shape=(self.n * 69), dtype=np.int32)

    def _make_move_arr(self):
        return np.zeros(shape=(self.n,), dtype=np.int32)

    def _make_vec_arr(self):
        return np.zeros(shape=(self.n), dtype=np.int32)

    def _make_mask_arr(self):
        return np.zeros(shape=(self.n * 64 * 88), dtype=np.int32)


class SFCChessEnv(CChessEnv):
    """
    RL Environment that interfaces with Stockfish
    """
    def __init__(self, n, depth):
        super().__init__(n)
        self._sfa = chessenv_c.ffi.new("SFArray *")
        create_sfarray(self._sfa, depth, n)

    def sample_opponent(self):
        generate_stockfish_move(
            self._env, self._sfa, self.ffi.cast("int *", self.move_arr.ctypes.data)
        )
        return np.copy(self.move_arr)

    def __del__(self):
        clean_sfarray(self._sfa)
