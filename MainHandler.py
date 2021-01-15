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

    def post(self):

        portfolio = self.get_argument('portfolio')
        zoom = int(self.get_argument('zoom'))
        extent = self.get_argument('extent')
        scale = int(self.get_argument('scale'))
        width = int(self.get_argument('width'))
        height = int(self.get_argument('height'))

        body = tornado.escape.json_decode(self.request.body)
        filter = body['filter']

        t = Omnisci()
        data = t.requestImage(portfolio, extent, width, height, filter)

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
        (r"/api/image", MainImageHandler),
        (r"/api/portfolios", MainPortfolioListHandler),
        (r"/api/analyze", MainAnalyzeHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
