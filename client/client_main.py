import sys

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.five_in_a_row import GameView

if __name__ == '__main__':
    g = GameView()
    g.run_game()
