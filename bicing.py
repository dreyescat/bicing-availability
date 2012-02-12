from StringIO import StringIO
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, FileBodyProducer
from twisted.web.http_headers import Headers


class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print 'Some data received:'
            print display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)


class BicingAgent(Agent):
    requests = 0
    def __init__(self, reactor):
        super(BicingAgent, self).__init__(reactor)

    def request(self, station_id):
        BicingAgent.requests += 1
        r = super(BicingAgent, self).request('POST',
            'https://www.bicing.cat/CallWebService/StationBussinesStatus_Cache.php',
            Headers({'Content-Type': ['application/x-www-form-urlencoded']}),
            FileBodyProducer(StringIO("idStation={0}".format(station_id))))
        def cbRequest(response):
            finished = Deferred()
            response.deliverBody(BeginningPrinter(finished))
            return finished

        def cbShutdown(ignored):
            BicingAgent.requests -= 1
            if BicingAgent.requests == 0:
                reactor.stop()
        r.addCallback(cbRequest)
        r.addBoth(cbShutdown)

BicingAgent(reactor).request(82)
BicingAgent(reactor).request(84)
BicingAgent(reactor).request(85)
reactor.run()
