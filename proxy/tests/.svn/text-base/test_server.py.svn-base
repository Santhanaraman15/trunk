from ..server import factory as ProxyFactory
from twisted.trial import unittest
from twisted.internet.protocol import Factory
from twisted.internet.defer import Deferred, succeed, fail
from twisted.trial.unittest import TestCase
from twisted.test import proto_helpers
from random import choice

def get_cached_succeed(data):
    return succeed(data)

def get_cached_fail(data):
    return fail('no cache')

targetFactory = Factory()
cmd ='!inlv(*)?\r'
error = 'ERROR\r\n'
targetFactory.name=str(choice(range( 201, 213 )))
targetFactory.listeners=[]

#targetFactory.proto = targetFactory.buildProtocol(('127.0.0.1',0))
#targetFactory.tr = proto_helpers.StringTransport()
#targetFactory.proto.makeConnection(self.tr)



class TestFakeProxyServer(TestCase):

    def setUp(self):
        factory = ProxyFactory(targetFactory)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def _test(self, cmd, expected):
        self.proto.dataReceived(cmd)
        return self.assertEqual(self.tr.value(), expected)

    def test_response_toclient(self):
        targetFactory.get_cached = get_cached_succeed        
        return self._test(cmd,cmd)
    
    def test_response_toclient_error(self):
        targetFactory.get_cached = get_cached_fail
        return self._test(cmd, error)
     

