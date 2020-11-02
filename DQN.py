from DQNAgent import DQNAgent
from Game import Game
from tqdm import tqdm
import time


def run():
    env = Game()
    agent = DQNAgent()

    scores = []

    for episode in tqdm(range(1, DQNAgent.EPISODES + 1), ascii=True, unit='episodes'):
        agent.tensorboard.step = episode

        curr_state = env.reset()

        if not (episode % DQNAgent.REND_EVERY):
            env.set_rend(True)
        else:
            env.set_rend(False)

        done = False
        while not done:
            next_states = env.get_next_states()
            best_state = agent.get_best_state(next_states.values())

            best_action = None
            for action, state in next_states.items():
                if state == best_state:
                    best_action = action
                    break

            reward, done = env.make_move(best_action)

            agent.update_replay_memory(curr_state, next_states[best_action], reward, done)
            curr_state = next_states[best_action]

            agent.train(done)

        scores.append(env.get_score())

        '''if not episode % DQNAgent.LOG_EVERY or episode == 1:
            average_reward = sum(scores[-DQNAgent.LOG_EVERY:]) / len(
                scores[-DQNAgent.LOG_EVERY:])
            min_reward = min(scores[-DQNAgent.LOG_EVERY:])
            max_reward = max(scores[-DQNAgent.LOG_EVERY:])
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward,
                                           reward_max=max_reward, epsilon=agent.epsilon)'''


if __name__ == "__main__":
    run()
