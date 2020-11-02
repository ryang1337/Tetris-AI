
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from collections import deque
import numpy as np
from datetime import datetime
import random

import ModifiedTB


class DQNAgent:
    DISCOUNT = 0.97
    BATCH_SIZE = 32
    REPLAY_MEMORY_SIZE = 20_000
    MIN_REPLAY_MEMORY_SIZE = 1_000
    EPISODES = 2_000
    REND_EVERY = 1
    LOG_EVERY = 50

    EPSILON_MIN = 0.001
    EPSILON_DECAY = 0.99975

    def __init__(self):
        self.model = self.create_model()
        self.replay_memory = deque(maxlen=DQNAgent.REPLAY_MEMORY_SIZE)
        self.epsilon = 1
        self.tensorboard = ModifiedTB.ModifiedTB(log_dir=f'logs/tetris-mem={DQNAgent.REPLAY_MEMORY_SIZE}-bs '
                                                         f'={DQNAgent.BATCH_SIZE}-'
                                                         f'{datetime.now().strftime("%Y%m%d-%H%M%S")}')

    def create_model(self):
        model = Sequential()
        model.add(Dense(32, input_dim=5, activation="relu"))
        model.add(Dense(32, "relu"))
        model.add(Dense(1, "linear"))

        model.compile(loss="mse", optimizer="adam")

        return model

    def update_replay_memory(self, current_state, next_state, reward, done):
        self.replay_memory.append((current_state, next_state, reward, done))

    def get_expected_score(self, state):
        state = np.reshape(state, [1, 4])
        if random.random() <= self.epsilon:
            return random.random()
        else:
            return self.model.predict(state)

    def get_best_state(self, states):
        max_value = None
        best_state = None

        if random.random() <= self.epsilon:
            return random.choice(list(states))
        else:
            for state in states:
                value = self.model.predict(np.reshape(state, [1, 4]))
                if not max_value or value > max_value:
                    max_value = value
                    best_state = state
        return best_state

    def train(self, terminal_state):
        if len(self.replay_memory) < DQNAgent.MIN_REPLAY_MEMORY_SIZE:
            return

        batch = random.sample(self.replay_memory, DQNAgent.BATCH_SIZE)

        new_current_states = np.array([transition[1] for transition in batch])
        future_q_values = [transition[0] for transition in self.model.predict(new_current_states)]

        x = []
        y = []

        for index, (curr_state, _, reward, done) in enumerate(batch):
            if not done:
                new_q = reward + DQNAgent.DISCOUNT * future_q_values[index]
            else:
                new_q = reward

            x.append(curr_state)
            y.append(new_q)

        self.model.fit(np.array(x), np.array(y), batch_size=DQNAgent.BATCH_SIZE, verbose=0,
                       shuffle=False)  # , callbacks=[self.tensorboard] if terminal_state else None)

        if self.epsilon > DQNAgent.EPSILON_MIN:
            self.epsilon *= DQNAgent.EPSILON_DECAY
