from keras.models import Sequential
from keras.layers import Dense
from collections import deque
import numpy as np
import time
from datetime import datetime
import random

import ModifiedTB

DISCOUNT = 0.97
BATCH_SIZE = 32
REPLAY_MEMORY_SIZE = 30_000
MIN_REPLAY_MEMORY_SIZE = 1_000

EPSILON_MIN = 0.001
EPSILON_DECAY = 0.99975


class DQNAgent:
    def __init__(self):
        self.model = self.create_model()
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)
        self.epsilon = 1
        self.tensorboard = ModifiedTB.ModifiedTB(log_dir=f'logs/tetris-mem={REPLAY_MEMORY_SIZE}-bs'
                                                         f'={BATCH_SIZE}-'
                                                         f'{datetime.now().strftime("%Y%m%d-%H%M%S")}')

    def create_model(self):
        model = Sequential()
        model.add(Dense(32, input_dim=5, activation="relu"))
        model.add(Dense(32, "relu"))
        model.add(Dense(1, "linear"))

        model.compile(loss="mse", optimizer="adam")

        return model

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def get_qs(self, state):
        return self.model.predict(np.array(state).reshape(-1, *state.shape))[0]

    def train(self, terminal_state, step):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        batch = random.sample(self.replay_memory, BATCH_SIZE)

        current_states = np.array([transition[0] for transition in batch])
        current_q_values = self.model.predict(current_states)

        new_current_states = np.array([transition[3] for transition in batch])
        future_q_values = self.model.predict(new_current_states)

        x = []
        y = []

        for index, (curr_state, action, reward, new_curr_state, done) in enumerate(batch):
            if not done:
                max_future_q = np.max(future_q_values[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_q_values[index]
            current_qs[action] = new_q

            x.append(curr_state)
            y.append(current_qs)

        self.model.fit(np.array(x), np.array(y), batch_size=BATCH_SIZE, verbose=0,
                       shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

        if self.epsilon > EPSILON_MIN:
            self.epsilon *= EPSILON_DECAY
