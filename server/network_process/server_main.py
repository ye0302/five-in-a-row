import sys

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from server.network_process.server_process import GobandServer

if __name__ == '__main__':
    host = "0.0.0.0"
    post = 9876
    c = GobandServer(host, post)
    c.main()