import pickle
# import below is implicitly required
from snake_game_AI_agent import SnakeAgent, td_qlearning

# Here we test a pretrained snake agent
def main():

    num_games = 2000
    file = open("./agent_data/set_2/agent_" + str(num_games) + "_games.pickle", "rb")
    agent = pickle.load(file)
    # We no longer want the agent to explore - it is now just performing
    agent.q_function.visits_threshold = 0

    while True:
        agent.play_game(learn=False, speed=20)


if __name__ == '__main__':
    main()
