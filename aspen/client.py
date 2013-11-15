from twisted.python import log, failure
from twisted.conch.telnet import TelnetProtocol
from twisted.internet.protocol import ReconnectingClientFactory, Factory
from twisted.internet.defer import succeed, fail
from twisted.internet import reactor
from collections import deque


from dsp import dsp

''' Setting up class to establish Telnet connection between client and server'''
class aspen_protocol(TelnetProtocol):
    """

    """

    '''To establish the connection and adding it to the double ended queue'''
    def connectionMade(self):
        log.msg( 'connection made: %s ' % (self.factory.name) )
        self.timeout_increment = 0.333
        self.send_list  = deque()

        self.aspen      = dsp(self.factory.name, self.timeout_increment)
        self.cycle_time = self.aspen.cycle['cycle_time']

        self._send_query_commands()
        self._set_timeout()


    '''Handling and logging the timeout cases'''
    def timeOut(self):
        log.msg( 'Aspen Timed Out %s ' % (self.factory.name) )
        self.transport.loseConnection()   

    '''Checks the deque to fnd the list of client that wants to query the
        server and sends query in the order in deque'''
    def _send_query_commands(self):
        if len(self.send_list) > 0:
            log.msg( 'Send list was not complete before cycle called again' )
            reactor.callLater(self_timeout_increment/2, self._send_query_commands)
        else:
            #log.msg( ' cycle started: %s ' % (self.factory.name) )
            reactor.callLater(self.cycle_time, self._send_query_commands)
            for qry_cmd in self.aspen.cycle['commands']:
                self.send_list.append(qry_cmd['command'])
                reactor.callLater(qry_cmd['delay'], self._call_later)

    '''Send the query and update the deque'''    
    def _call_later(self):
        self.transport.write(self.send_list.popleft())

    '''Setting the aspen time out'''
    def _set_timeout(self):
        t = self.cycle_time*6
        log.msg( 'setting aspen timout out for %s' % (t) )
        self.timeout = reactor.callLater(t, self.timeOut)

    '''Obtaining the data(response) from the server'''
    def dataReceived(self, data):
        #log.msg( 'Aspen timer reset' )
        self.timeout.reset(self.aspen.timeout())

        d = self.aspen.put_in_cache(data)
        for listener in self.factory.listeners:
            d.addCallback( listener.transport.write )
     

    ''' This is called if the connection is lost between client and server'''    
    def connectionLost(self, reason):
        log.msg( 'connection lost: %s ' % (self.factory.name) )

class factory(ReconnectingClientFactory):
    """ 
    A class to manufacture connections to the Aspen units that will 
    reconnect if connection is lost. Note: Although this is a factory
    There should be only one connection to the client at a time.

    """
    initialDelay = 0.1   # reconnect delay (After connection is lost)
    maxDelay=120
    factor=2.71828

    protocol = aspen_protocol

    '''Initialising the instance variables of the class'''
    def __init__(self, name):
        self.listeners = []
        self.name = name
        self.noisy = False

    
    def startedConnecting(self, connector):
        log.msg('Attempting to connect to aspen: %s.' % (self.name))

    ''' Creaate instance of the aspen_protocol'''
    def buildProtocol(self, addr):
        self.resetDelay()   # Reset the delay
        self.p = Factory.buildProtocol(self, addr)
        return self.p
    '''Over riding the get_cached method to obtain the data or error message
        from the server'''
    def get_cached(self, data):
        if not self.p is None:
            d=self.p.aspen.get_from_cache(data)
        else:
            msg='no protocol instance for Aspen: %s. Device off?' % (self.name)
            d=fail(msg)
        if isinstance(d.result, failure.Failure):
            msg = d.result.getErrorMessage()
            if msg == 'no cache':
                d.addErrback( lambda r: self.p.transport.write(data) )
            else:
                d.addErrback( lambda r: log.msg(msg) )
        return d

    '''To reconnect when the connection is lost'''
    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection to aspen %s. Device off?' % (self.name))
        ReconnectingClientFactory.clientConnectionLost(self, 
                                                       connector, 
                                                       reason)
    '''To reconnect when the attempt to connection is failed'''  
    def clientConnectionFailed(self, connector, reason):
        log.msg('Unable to connect to aspen %s. Device off?' % (self.name))
        ReconnectingClientFactory.clientConnectionFailed(self, 
                                                         connector,
                                                         reason)

