from match import Match
from agent.ai_agent import RandomAgent, TestSearchAgent
from agent.evaluation import evaluate


if __name__ == '__main__':
    match = Match(agent_black=TestSearchAgent('BLACK', evaluate), agent_white=RandomAgent('WHITE'), gui=False)
    match.start()
