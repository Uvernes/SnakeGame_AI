import math
import pickle
import matplotlib.pyplot as plt
# import below is implicitly required
from snake_game_AI_agent import SnakeAgent, td_qlearning

SAMPLE_SIZE = 20

def main():

    num_games_checkpoints = list(range(50, 501,50))
    average_scores = []

    for num_games in num_games_checkpoints:

        file = open("./agent_data/set_2/agent_" + str(num_games) + "_games.pickle", "rb")
        agent = pickle.load(file)
        file.close()
        # We no longer want the agent to explore - it is now just performing
        agent.q_function.visits_threshold = 0

        cur_average_score = 0

        for _ in range(SAMPLE_SIZE):
            cur_average_score += agent.play_game(learn=False, speed=math.inf)
        average_scores.append(cur_average_score/SAMPLE_SIZE)

    for i in range(len(num_games_checkpoints)):
        print("Games played:", num_games_checkpoints[i], "| Score: ", average_scores[i])

    plt.plot(num_games_checkpoints, average_scores)
    plt.xlabel("Number of Games Played")
    plt.ylabel("Average Score Across " + str(SAMPLE_SIZE) + " Games")
    plt.title("Number of Games Played vs. Average Game Scores")
    plt.savefig("temp_results_graph_average_" + str(SAMPLE_SIZE) + "_games.png")
    plt.show()


if __name__ == '__main__':
    main()
