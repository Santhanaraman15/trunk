from twisted.application import internet, service
from twisted.python import log
from twisted.internet import reactor
import sys

from aspen.client import factory as AspenFactory
from proxy.server import factory as ProxyServerFactory



#log.startLogging(sys.stdout)  
log.startLogging(open('proxy.log', 'w'))

default_aspen_port = 4081

'''Setting up the web proxy service for the aspen'''
class AspenProxyService(service.Service):
    def __init__(self):
        ''' Assigning ip,port to each of the aspen devices'''
        self.Aspens = [  
                ('172.20.72.201', default_aspen_port, None),
                ('172.20.72.202', default_aspen_port, None),
                ('172.20.72.203', default_aspen_port, None),
                ('172.20.72.204', default_aspen_port, None),
                ('172.20.72.205', default_aspen_port, None),
                ('172.20.72.206', default_aspen_port, None),
                ('172.20.72.207', default_aspen_port, None),
                ('172.20.72.208', default_aspen_port, None),
                ('172.20.72.209', default_aspen_port, None),
                ('172.20.72.210', default_aspen_port, None),
                ('172.20.72.211', default_aspen_port, None),
                ('172.20.72.212', default_aspen_port, None),
                ('172.20.72.213', default_aspen_port, None),
                      ]  


        t = []

        for aspen in self.Aspens:
            host, port, factory = aspen
               
            name = host.split('.').pop()

            listen_port = 40000+int(name)

            factory = AspenFactory(name)

            t.append( (host, port, factory) )

            # reactor.connectTCP( host, port, factory )
            # reactor.listenTCP( listen_port, ProxyServerFactory(factory) )

        self.Aspens = t

    '''To start the web proxy service for the aspen'''
    def startService(self):
        service.Service.startService(self)


application = service.Application("AspenProxy")

top_service = service.MultiService()

proxy_service = AspenProxyService()
proxy_service.setServiceParent(top_service)


for aspen in proxy_service.Aspens:
    tcp_client=internet.TCPClient(aspen[1], aspen[0], aspen[2])
    tcp_server=internet.TCPServer(aspen[1], aspen[0], ProxyServerFactory(aspen[2]))
    tcp_client.setServiceParent(top_service)
    tcp_server.setServiceParent(top_service)
        

top_service.setServiceParent(application)


