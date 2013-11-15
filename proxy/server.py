from twisted.python import log, failure
from twisted.internet.protocol import ServerFactory
from twisted.conch.telnet import TelnetProtocol

''' Setting up the protocol class for the server'''
class proxy_protocol(TelnetProtocol):
    
    ''' To check if connection is established'''
    def connectionMade(self):
        log.msg( 'proxy connection made: ipad?' )
        self.factory.myTarget.listeners.append(self)

    ''' To check if the connection is lost'''
    def connectionLost(self, reason):
        log.msg( 'proxy connection lost: ipad?' )
        self.factory.myTarget.listeners.remove(self)

    '''To receive the data or the error from client'''    
    def dataReceived(self, data):
        client = self.factory.myTarget
        d = client.get_cached(data)
        if not d == None:            
            if isinstance(d.result, failure.Failure):
                msg = d.result.getErrorMessage
                d.addErrback( lambda r: log.msg(msg) )
                d.addCallback( lambda r: self.transport.write('ERROR\r\n') )
            else:
                d.addCallback( self.transport.write )

'''Setting up the Server Factory''' 
class factory(ServerFactory):
    protocol = proxy_protocol

    '''Over riding the init function in the factory class'''
    def __init__(self, TargetFactory):
        self.myTarget = TargetFactory
        self.noisy = False
        self.t_name = self.myTarget.name

    ''' Starting the proxy service'''
    def startFactory(self):
        log.msg('Starting proxy service for aspen: %s.' % (self.t_name))

    '''Shutting down the proxy service'''
    def stopFactory(self):
        log.msg('Shutting down proxy service for aspen: %s.' % (self.t_name))
