from ..dsp import dsp
from twisted.internet.defer import Deferred, succeed, fail
from twisted.python.failure import Failure, DefaultException
from twisted.trial.unittest import TestCase
from random import choice

# set globals
name = str(choice(range(201,213)))
cmd='!inlv(*)?\r'
response_ok=succeed('inlv(0,0,0,0,0,0,0,0)')
response_fail=fail('no cache')
t = float(0.333)

print 'Test Name: %s' % (name)

class test_dsp(TestCase):

    def setUp(self):
        self.a = dsp(name, t)


    def test_attributes_name(self):
        return self.assertEquals( self.a.name, name )

    def test_attributes_ticker(self):
        msg='Ticker not float'
        if not type(self.a.ticker) is float: return self.fail(msg)
        return self.assertEquals( self.a.ticker, t )
    
    def test_cycle_structure(self):
        
        msg='cycle not dictionary'
        if not type(self.a.cycle) is dict: return self.fail(msg)

        try:
            ct = self.a.cycle['cycle_time']
            rqcl_all = self.a.cycle['rqcl_all']
            commands = self.a.cycle['commands']
        except:
            return self.fail()
        
        msg='cycle_time not float'
        if not type(ct) is float: return self.fail(msg)
        msg='rqcl_all not list'
        if not type(rqcl_all) is list: return self.fail(msg)
        msg='rqcl_all empty'
        if len(rqcl_all) == 0: return self.fail(msg)

        for cmd in commands:
            msg='command list does not contain dictionaries'
            if not type(cmd) is dict: return self.fail(msg)
            try:
                delay = cmd['delay']
                command = cmd['command']
            except:
                return self.fail()

        
        return self.assertEquals( len(rqcl_all), len(commands) )

    def test_cycle_time(self):

        l = len(self.a.cycle['commands'])

        c = l * t
        c += t

        i = float(c)

        msg='cycle_time not the correct length'
        if not round(i, 6) == round(self.a.cycle['cycle_time'], 6): return self.fail(msg)

        msg='delay not set correctly'
        x = float(0.0)
        for cmd in self.a.cycle['commands']: 
            if not round(x, 6) == round(cmd['delay'], 6): return self.fail(msg)
            x += t 
            
        x += t

        return self.assertEquals( round(x, 6), round(i, 6) )


    def test_not_in_cache(self):  
        x = self.a.get_from_cache(cmd)        
        return self.assertFailure(x, DefaultException)

    def test_in_cache(self):
        self.a.put_in_cache(response_ok.result)
        x = self.a.get_from_cache(cmd)
        return self.assertEquals( x.result, response_ok.result )
