"""
File to do performance benchmarking for the parallelized C version vs the
python versions.
"""

import time
import pyspiel
import random
import numpy as np
from open_spiel.python.rl_environment import Environment, StepType
from chessenv.env import CChessEnv
import multiprocessing as mp

from chessenv.rep import CMove


def random_action(masks):
    probs = masks / np.sum(masks, axis=1).reshape(-1, 1)
    actions = np.int32(np.zeros(len(masks)))
    for (i, p) in enumerate(probs):
        actions[i] = np.random.choice(len(p), p=p)
    return actions


class PySpielChessEnvSequential:
    def __init__(self, n):
        self.n = n
        self._envs = [Environment(pyspiel.load_game("chess")) for _ in range(n)]
        self.action_width = self._envs[0].action_spec()["num_actions"]

    def reset(self):
        out = [e.reset() for e in self._envs]
        states = [o.observations["info_state"][0] for o in out]

        legal_mask = np.zeros((self.n, self.action_width))
        for (i, la) in enumerate([o.observations["legal_actions"] for o in out]):
            for a in la:
                legal_mask[i, a] = 1.0

        return np.stack(states), legal_mask

    def step(self, action):
        states = []
        legal_mask = np.zeros((self.n, self.action_width))
        rewards = np.zeros((self.n,))
        dones = np.zeros((self.n,))

        for (i, a) in enumerate(action):
            a = np.array([a])

            out = self._envs[i].step(a)

            if out.step_type == StepType.LAST:
                dones[i] = 1.0
                rewards[i] = out.rewards[0]
                out = self._envs[i].reset()
            else:
                current_player = self._envs[i]
                response = random.sample(
                    out.observations["legal_actions"][out.current_player()], 1
                )

                out = self._envs[i].step(np.array(response))

                if out.step_type == StepType.LAST:
                    dones[i] = 1.0
                    rewards[i] = out.rewards[0]
                    out = self._envs[i].reset()

            states.append(out.observations["info_state"][0])

            for a in out.observations["legal_actions"]:
                legal_mask[i, a] = 1.0

        return (
            np.stack(states),
            legal_mask,
            rewards,
            dones,
        )


def _worker(state_q, action_q):
    env = PySpielChessEnvSequential(1)
    state_and_mask = env.reset()
    state_q.put(state_and_mask)

    while True:
        action = action_q.get()
        out = env.step(action)
        state_q.put(out)


class PySpielChessEnvParallel:
    def __init__(self, n):
        self.n = n
        self._reset()

    def _reset(self):
        self.action_qs = [mp.Queue() for _ in range(self.n)]
        self.state_qs = [mp.Queue() for _ in range(self.n)]

        self.procs = [
            mp.Process(target=_worker, args=(self.state_qs[i], self.action_qs[i]))
            for i in range(self.n)
        ]

        for p in self.procs:
            p.daemon = True
            p.start()

    def reset(self):
        states, masks = zip(*[s.get() for s in self.state_qs])
        return np.concatenate(states), np.concatenate(masks)

    def step(self, actions):

        for i, aq in enumerate(self.action_qs):
            aq.put(np.array([actions[i]]))

        out = [s.get() for s in self.state_qs]
        states, masks, rewards, dones = zip(*out)
        return (
            np.concatenate(states),
            np.concatenate(masks),
            np.concatenate(rewards),
            np.concatenate(dones),
        )

    def __del__(self):
        for p in self.procs:
            p.kill()


def benchmark(env, n, n_steps=100):
    env = env(n)
    state, mask = env.reset()
    times = []

    for _ in range(n_steps):
        action = random_action(mask)
        start = time.time()
        _, mask, _, _ = env.step(action)
        times.append(time.time() - start)

    del env

    return times


if __name__ == "__main__":

    for n in [1, 2, 4, 8, 16, 32, 128, 256, 512, 1024]:
        try:
            times = benchmark(PySpielChessEnvParallel, n)
            times = list(map(str, times))
            print(f'pyspiel_parallel,{n},{",".join(times)}')
        except:
            pass

        times = benchmark(PySpielChessEnvSequential, n)
        times = list(map(str, times))
        print(f'pyspiel_sequential,{n},{",".join(times)}')

        times = benchmark(CChessEnv, n)
        times = list(map(str, times))
        print(f'cchessenv,{n},{",".join(times)}')
