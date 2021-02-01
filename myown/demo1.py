from pymapd import connect
import time


class Demo1:

    def __init__(self):
        self.con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

    def request(self, portfolio_name, filter):

        start = time.time()

        haz1 = self.
