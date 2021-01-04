import tornado.ioloop
import tornado.web

from myown.omnisci import Omnisci 



class MainHandler(tornado.web.RequestHandler):


    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):

        zoom = int(self.get_argument('zoom'))
        extent = self.get_argument('extent')
        scale = int(self.get_argument('scale'))

        t = Omnisci()
        data = t.request(zoom, extent, scale)

        self.write(data)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()