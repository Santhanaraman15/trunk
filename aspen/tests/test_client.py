from ..client import factory as AspenFactory

from twisted.trial import unittest
from twisted.internet.protocol import Factory
from twisted.internet.defer import Deferred, succeed, fail
from twisted.trial.unittest import TestCase
from twisted.test import proto_helpers
from random import choice

name=str(choice(range( 201, 213 )))

class TestAspenClient(TestCase):

    def setUp(self):
        factory = AspenFactory(name)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_one(self):
        pass
