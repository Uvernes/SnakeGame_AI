import math
import pickle

import pygame
from game import SnakeGame, State

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class td_qlearning():

    # Note: To compute reward, both the state and action are required
    @staticmethod
    def reward(state_bitstring, action):
        state = State(state_bitstring)
        # An action of None implies we are at a terminal state. This means a collision occurred. Set reward to -10
        # (Actually, reward of 0 should work also since already punished for collision previously)
        # ** Maybe we don't even need q-value for terminal states? Reflect later -- YUP, REMOVED FOR NOW
        if action is None:
            return -10
        # Check if action resulted in food being obtained
        elif state.food_adjacent and \
                ((state.food_left and action == "left") or (state.food_right and action == "right") or
                 (state.food_up and action == "up") or (state.food_down and action == "down")):
            return 50
        # Check if action resulted in a collision
        elif (state.danger_left and action == "left") or (state.danger_right and action == "right") or \
                (state.danger_up and action == "up") or (state.danger_down and action == "down"):
            return -50
        # REMOVE LATER
        elif state.hungry:
            return -50
        else:
            return -1

    def __init__(self, alpha, gamma, init_q_value, visits_threshold, R_plus):
        # Stores q value for state action pairs that have been visited (if not visited, q value is the default one)
        self.q_values = dict()  # of the form - (state, action) : q_value(state, action)
        self.number_of_visits = dict()  # of the form state : (state, action) : N(state, action)
        self.alpha = alpha
        self.gamma = gamma
        self.init_q_value = init_q_value
        self.visits_threshold = visits_threshold
        self.R_plus = R_plus

    # Update the q-function using the trial passed in. We use the exploitation/exploration method
    # Note: States are required to be passed in as bitstring representations
    def update(self, trial):
        # Note: Ignore terminal state since it has no associated action and reward requires both state and action
        for i in range(len(trial) - 1):
            state, action = trial[i]
            if (state, action) not in self.q_values:
                self.q_values[(state, action)] = self.init_q_value
                self.number_of_visits[(state, action)] = 0
            self.number_of_visits[(state, action)] += 1

            # If next state is the terminal state, q(s,a) is simply reward(s,a)
            if i + 1 >= len(trial) - 1:
                self.q_values[(state, action)] = td_qlearning.reward(state, action)
                continue

            # Otherwise update q_value regularly
            cur_q_value = self.q_values[(state, action)]
            estimate_q_value = td_qlearning.reward(state, action)

            # must find the max q value possible from the next state
            next_state = trial[i + 1][0]
            max_q_value_in_next_state = -math.inf
            for possible_action in ["right", "left", "up", "down"]:
                cur_q_value_in_next_state = self.q_value(next_state, possible_action)
                if cur_q_value_in_next_state > max_q_value_in_next_state:
                    max_q_value_in_next_state = cur_q_value_in_next_state
            # Note: must account for the discount factor here
            estimate_q_value += self.gamma*max_q_value_in_next_state

            # Update q-value for the current state action pair being examined
            self.q_values[(state, action)] += self.alpha*(estimate_q_value - cur_q_value)

    def q_value(self, state, action):
        if (state, action) not in self.q_values:
            return self.init_q_value
        else:
            return self.q_values[(state, action)]

    def num_visits_for_given_pair(self, state, action):
        if (state, action) not in self.number_of_visits:
            return 0
        else:
            return self.number_of_visits[(state,action)]

    def policy(self, state):
        # Policy chooses the action with the value for the exploration/exploitation function
        best_action = None
        highest_value = -math.inf
        for action in ["right", "left", "up", "down"]:
            cur_value = None
            if self.num_visits_for_given_pair(state, action) < self.visits_threshold:
                cur_value = self.R_plus
            else:
                cur_value = self.q_value(state, action)

            if cur_value > highest_value:
                best_action = action
                highest_value = cur_value
        return best_action


class SnakeAgent:

    def __init__(self, alpha=0.1, gamma=0.9, init_q_value=0, visits_threshold=1, R_plus=10000):

        self.q_function = td_qlearning(alpha, gamma, init_q_value, visits_threshold, R_plus)

    def learn(self, num_games):
        for _ in range(num_games):
            self.play_game()

    # When playing through a game using our current policy, we store all state-action pairs. This generates a trial.
    # We then update the q-values AFTER the game, using this trial
    # *** BUT should we be updating q-values as we are generating a trial? ASK. Maybe doesn't matter
    def play_game(self, learn=True, speed=1000):
        trial = []
        pygame.init()
        display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        game = SnakeGame(display, w=SCREEN_WIDTH, h=SCREEN_HEIGHT, speed=speed)
        prev_score = game.score
        turns_passed_since_last_ate = 0
        while not game.game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # Prevent infinite game loops
            if prev_score == game.score:
                turns_passed_since_last_ate += 1
            else:
                prev_score = game.score
                turns_passed_since_last_ate = 0
            if turns_passed_since_last_ate > 100:
                break

            state = game.get_state().bitstring()
            action = self.q_function.policy(state)
            trial.append((state, action))
            game.play_step(action)

        # Add terminal state - has no action
        trial.append((game.get_state().bitstring(), None))
        print(trial)

        if learn:
            self.q_function.update(trial)

        print("Score:", game.score)
        return game.score

    def save(self, filename="./agent_data/agent_data.pickle"):
        file = open(filename, "wb")
        pickle.dump(self, file)
        file.close()


if __name__ == '__main__':
    # Greater than 0 if agent has been trained previously. If so, we start with the pretrained agent
    num_prev_games = 0
    # Specify when to save agent in terms of total games played in its life
    save_checkpoints = list(range(50,2001,50))
    print("Save checkpoints:", save_checkpoints)

    if num_prev_games > 0:
        file = open("./agent_data/set_3/agent_" + str(num_prev_games) + "_games.pickle", "rb")
        agent = pickle.load(file)
        file.close()
    else:
        agent = SnakeAgent()

    num_games_to_play_checkpoints = []
    for save_point in save_checkpoints:
        num_games_to_play_checkpoints.append(save_point - num_prev_games)

    print("Num games to play: ", max(num_games_to_play_checkpoints))

    for game_num in range(1, max(num_games_to_play_checkpoints) + 1):
        print("Current game:", game_num + num_prev_games)
        # Save agent if at a checkpoint
        if game_num in num_games_to_play_checkpoints:
            original_threshold = agent.q_function.visits_threshold
            agent.q_function.visits_threshold = 0
            agent.play_game(speed=20)
            agent.q_function.visits_threshold = original_threshold
            agent.save(filename="./agent_data/set_3/agent_" + str(game_num + num_prev_games) + "_games.pickle")
        else:
            agent.play_game()

    # Games are displayed slower once agent has had enough time to learn
    # while True:
    #     agent.play_game(speed=20)
