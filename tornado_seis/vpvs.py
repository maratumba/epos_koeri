# -*- coding: utf-8 -*-
import handler
import tornado.ioloop
import tornado.web
import tornado.escape
from request_manager_vpvs import RequestManagerVPVS
import _mysql
import json
from ConfigParser import ConfigParser

class MainHandler(handler.APIBaseHandler):

    def initialize(self, config):
        self.config = config

    def do_get(self):
        manager = RequestManagerVPVS()
        user_request = manager.bind(self).validate()
        if user_request.is_valid:
            args = user_request.getArgs()

            # Uncomment lines 17, 18 in order to just show the user request args and stop
            # self.send_success_response(args)
            # return

            db = _mysql.connect(self.config.get('db','host'),
                                self.config.get('db','user'),
                                self.config.get('db','pass'),
                                self.config.get('db','db'))

            query = '''
                    select distinct 
                    ( 1 + 
                     (
                      (
                       TIMESTAMPDIFF(microsecond,c.origintime,g.pick)/{DIV}
                      ) 
                      - 
                      (
                       TIMESTAMPDIFF(microsecond,c.origintime,f.pick)/{DIV}
                      )
                     ) 
                     / 
                     (
                      TIMESTAMPDIFF(microsecond,c.origintime,f.pick)/{DIV}
                     )
                    ) as vpvs_value,
                    g.pick as S_arrival_time,
                    f.pick as P_arrival_time,
                    c.origintime as event_origintime,
                    c.lat as event_lattitude,
                    c.lon as event_longitude,
                    c.elev as event_elevation,
                    h.network as network_code,
                    h.stacode as station_code,
                    h.loco as station_location,
                    h.lat as station_lattitude,
                    h.lon as station_longitude,
                    h.elev as station_elevation,
                    h.place as station_info
                    from
                    eqlocations c,
                    phases g,
                    phases f,
                    stations h
                    where 
                    g.type='P' and
                    f.type='S' and
                    g.eqkID=f.eqkID and
                    g.eqkID=c.eqkID and
                    f.stacode = g.stacode and
                    f.loco = g.loco and
                    f.net = g.net and
                    f.net = h.network and
                    f.stacode = h.stacode and
                    f.loco = h.loco and
                    (c.lat between {minlat} and {maxlat}) and
                    (c.lon between {minlon} and {maxlon}) and
                    (c.elev between {mineqdep} and {maxeqdep}) and
                    (c.origintime between '{mintime}' and '{maxtime}') 
                    having (vpvs_value > {vpvsmin})
                    order by c.origintime asc
                    limit 1000000;
                    '''.format(**args)

            # uncomment lines 75, 76 in order to echo the query to the screen and stop
            # self.send_success_response(query)
            # return
            
            db.query(query)
            rs = db.store_result()
            # self.send_success_response(json.dumps(dict(result=rs.fetch_row(maxrows=0, how=1))))
            # db.close()

            resp = self.render_string('response.json', result=json.dumps(rs.fetch_row(maxrows=0, how=1)))
            self.write(resp)
            self.set_header('Content-Type', 'application/json')
            return
        else:
            errors = [e.message for e in user_request.global_errors]
            return self.send_error_response(errors)


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        queries = []

        # add some example queries
        queries.append(dict(
            mintime='1980-01-01T00:00:00.000',
            maxtime='2017-01-01T00:00:00.000',
            minlat=30,          # -90, 90 and smaller than maxlat
            maxlat=50,          # -90, 90
            minlon=40,          # -180, 180 and smaller than maxlon
            maxlon=60,          # -180, 180
            mineqdep=-70,       # -6378, -9 and smaller than maxeqdep
            maxeqdep=-30,       # -6378, -9
            minnp=2,            # number of p waves, int, min: 0
            minns=3,            # number of s waves, int, min: 0
            maxpw=3,            # int, 0, 4
            maxsw=3,            # int, 0, 4
            minps=4,            # 0, +
            maxvpvspw=3,
            maxvpvssw=3,
            maxgap=150,         # azim gap 0, 360
            midi=70,            # horiz dist of closest sta
            maxherr=300,        # 0, 4000
            maxverr=200,         # 0, 6378
            maxvpvserr=1000000,
            DIV=1000000,
            vpvsmin = 1.41,
            modtype = 1,
            codetype = 2,
            mettype = 2
        ))


        queries.append(dict(
            mintime='1980-01-01T00:00:00.000',
            maxtime='2017-01-01T00:00:00.000',
            minlat=0.0,          # -90, 90 and smaller than maxlat
            maxlat=80.0,          # -90, 90
            minlon=0.10,          # -180, 180 and smaller than maxlon
            maxlon=90.0,          # -180, 180
            mineqdep=1.,       # -9, 6378 and smaller than maxeqdep
            maxeqdep=1000.0,       # -9, 6378
            minnp=0,            # number of p waves, int, min: 0
            minns=0,            # number of s waves, int, min: 0
            maxpw=0,            # int, 0, 4
            maxsw=0,            # int, 0, 4
            minps=0,            # 0, +
            maxvpvspw=4,
            maxvpvssw=4,
            maxgap=360,         # azim gap 0, 360
            midi=0,            # horiz dist of closest sta
            maxherr=500,        # 0, 4000
            maxverr=500,         # 0, 6378
            maxvpvserr=100000,
            DIV=1000000, #why is this adjustable?
            vpvsmin = 0,
            modtype = 1,
            codetype = 2,
            mettype = 2
        ))
        
        for idx, q in enumerate(queries):
            queries[idx] = '&'.join([ '{}={}'.format(k, v) for k, v in q.iteritems() ])
        # transform the queries into http query strings
        queries = ['/nfo_marsite/vpvs/query?%s' % q for q in queries]

        manager = RequestManagerVPVS()

        self.render('index.html', queries=queries, manager=manager)

if __name__ == "__main__":

    cfg = ConfigParser()
    cfg.read('config.ini')

    settings = dict(
        debug=True,
        template_path='templates/'
    )

    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/query", MainHandler, dict(config=cfg))
    ], **settings)
    application.listen(cfg.get('service', 'port'))
    tornado.ioloop.IOLoop.current().start()
