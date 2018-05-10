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
                       TIMESTAMPDIFF(microsecond,c.origintime,g.pick)/{param_DIV}
                      ) 
                      - 
                      (
                       TIMESTAMPDIFF(microsecond,c.origintime,f.pick)/{param_DIV}
                      )
                     ) 
                     / 
                     (
                      TIMESTAMPDIFF(microsecond,c.origintime,f.pick)/{param_DIV}
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
                    (c.lat between {param_minlat} and {param_maxlat}) and
                    (c.lon between {param_minlon} and {param_maxlon}) and
                    (c.elev between {param_mineqdep} and {param_maxeqdep}) and
                    (c.origintime between '{param_mintime}' and '{param_maxtime}') 
                    having (vpvs_value > {param_vpvsmin})
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
            param_mintime='1980-01-01T00:00:00.000',
            param_maxtime='2017-01-01T00:00:00.000',
            param_minlat=30,          # -90, 90 and smaller than maxlat
            param_maxlat=50,          # -90, 90
            param_minlon=40,          # -180, 180 and smaller than maxlon
            param_maxlon=60,          # -180, 180
            param_mineqdep=-70,       # -6378, -9 and smaller than maxeqdep
            param_maxeqdep=-30,       # -6378, -9
            param_minnp=2,            # number of p waves, int, min: 0
            param_minns=3,            # number of s waves, int, min: 0
            param_maxpw=3,            # int, 0, 4
            param_maxsw=3,            # int, 0, 4
            param_minps=4,            # 0, +
            param_maxvpvspw=3,
            param_maxvpvssw=3,
            param_maxgap=150,         # azim gap 0, 360
            param_midi=70,            # horiz dist of closest sta
            param_maxherr=300,        # 0, 4000
            param_maxverr=200,         # 0, 6378
            param_maxvpvserr=1000000,
            param_DIV=1000000,
            param_vpvsmin = 1.41,
            param_modtype = 1,
            param_codetype = 2,
            param_mettype = 2
        ))


        queries.append(dict(
            param_mintime='1980-01-01T00:00:00.000',
            param_maxtime='2017-01-01T00:00:00.000',
            param_minlat=0.0,          # -90, 90 and smaller than maxlat
            param_maxlat=80.0,          # -90, 90
            param_minlon=0.10,          # -180, 180 and smaller than maxlon
            param_maxlon=90.0,          # -180, 180
            param_mineqdep=1.,       # -9, 6378 and smaller than maxeqdep
            param_maxeqdep=1000.0,       # -9, 6378
            param_minnp=0,            # number of p waves, int, min: 0
            param_minns=0,            # number of s waves, int, min: 0
            param_maxpw=0,            # int, 0, 4
            param_maxsw=0,            # int, 0, 4
            param_minps=0,            # 0, +
            param_maxvpvspw=4,
            param_maxvpvssw=4,
            param_maxgap=360,         # azim gap 0, 360
            param_midi=0,            # horiz dist of closest sta
            param_maxherr=500,        # 0, 4000
            param_maxverr=500,         # 0, 6378
            param_maxvpvserr=100000,
            param_DIV=1000000, #why is this adjustable?
            param_vpvsmin = 0,
            param_modtype = 1,
            param_codetype = 2,
            param_mettype = 2
        ))
        
        for idx, q in enumerate(queries):
            queries[idx] = '&'.join([ '{}={}'.format(k, v) for k, v in q.iteritems() ])
        # transform the queries into http query strings
        queries = ['/query?%s' % q for q in queries]

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
