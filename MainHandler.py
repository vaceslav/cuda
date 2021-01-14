from logging import debug
import tornado.ioloop
import tornado.web

from myown.omnisci import Omnisci
from myown.portfolios import Portfolios


class MainHandler(tornado.web.RequestHandler):

    def post(self):

        portfolio = self.get_argument('portfolio')
        zoom = int(self.get_argument('zoom'))
        extent = self.get_argument('extent')
        scale = int(self.get_argument('scale'))

        body = tornado.escape.json_decode(self.request.body)
        filter = body['filter']

        t = Omnisci()
        data = t.request(portfolio, zoom, extent, scale, filter)

        self.write(data)


class MainImageHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):

        extent = self.get_argument('bbox')

        t = Omnisci()
        data = t.requestImage(extent)

        self.write(data._render_result.image)
        self.set_header("Content-type",  "image/png")


class MainPortfolioListHandler(tornado.web.RequestHandler):

    def get(self):

        p = Portfolios()
        data = p.list()

        self.finish({'portfolios': data})


class MainAnalyzeHandler(tornado.web.RequestHandler):

    def post(self):

        portfolio = self.get_argument('portfolio')
        body = tornado.escape.json_decode(self.request.body)
        filter = body['filter']

        p = Portfolios()
        data = p.analyze(portfolio, filter)

        self.finish({'analyze': data})


def make_app():
    return tornado.web.Application([
        (r"/api/cluster", MainHandler),
        (r"/image", MainImageHandler),
        (r"/api/portfolios", MainPortfolioListHandler),
        (r"/api/analyze", MainAnalyzeHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
