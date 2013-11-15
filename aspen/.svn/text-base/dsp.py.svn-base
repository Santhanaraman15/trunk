import re
from datetime import datetime
from twisted.internet.defer import Deferred, succeed, fail

class dsp(object):
    """ ASPEN Device Base classf
    A Class to contain all of the specialized ASPEN settings and commands.
    Current implementation is designed to work with the twisted framework
    which is implemented as a proxy service between control systems (iPads)
    and the Aspen devices.

    Initialize with Name and Ticker Increment
        - last octet of device IP (e.g. xxx.xxx.xxx.[201])
          
          name='201' (Str)

        - Ticker increment is the (best effort) time interval (rate)  that
          the system will poll the aspen device at for repeating queries such
          as asking what the student mic volume levels are, and how frequently

          ticker=0.333 (seconds)(float)

    
    This class implements a simple caching system accessible by: 
        put_in_cache()
        get_from_cache()

    """
    def __init__(self, name, ticker):
        self.name = name                # Name is Last Octet of IP
        self.ticker = float(ticker)     # Sets the frequency of repeating queries

        # List of all of the aspen device names (keep current!)
        self._SPN812s = ['201','204','209']
        self._SPN16is = ['203','206','207','208','211','212','213']
        self._SPN16is_sp = ['203','208','213'] #special
        self._SPNCONs = ['202','204','210']
                        
        # List of all of the queries that should be repeated and cached
        # rqcl = repeated query command list
        self._rqcl_each   = [ '!inlv(*)?\r', '!inmt(*)?\r', ]
        self._rqcl_812    = [ '!rpingn(*)?\r', '!rpoutgn(*)?\r', ]
        self._rqcl_16i    = [ ] 
        self._rqcl_16i_sp = [ '!xpgn(1,3)?\r', ]
        rs_ls = self._rqcl_each + self._rqcl_812 + self._rqcl_16i \
                                                          + self._rqcl_16i_sp
        
        # This instance's cache is a dict
        self._cache = {}

        # Set the total time all queries cycle and build command list
        self.cycle = self._set_cycle()


    def _set_cycle(self):
        """ Return the total time all queries cycle, a list of responses to
            the repeating queries (from the aspen), the interval of each query
            (command) and each query command to send to the aspen.

        Each repeating command should execute after one ticker interval.
        Each Aspen unit (instance of this class) has a set of repeating
        query (commands sent to aspen).

        Each command is has an associated interval which is the space between
        the start of the cycle and when the interval should execute. (e.g., an
        interval of 0.999 means that the query should be sent to the aspen
        999 miliseconds after the beginning of the cycle.
        
        Response structure:
        { 'cycle_time': x,
          'rqcl_all': ['inlvl', ...]  
          'commands': [{'delay':0, 'command':'!inlvl(*)?\r'}, ...]
        
        """
        d = {'cycle_time': 0,      # total time of a cycle
             'rqcl_all': [],       # total Repeated Ruery Command List
             'commands': [],       # query commands & intervals (dict)
            }

        i = float(0.0)       # ticker interval multiplier
        
        # for queries that go to each aspen device
        for qry in self._rqcl_each:
            d['commands'].append( self._set_qdict( i, qry ) )
            d['rqcl_all'].append( self._set_rlist( qry ) )
            i += 1

        if self.name in self._SPN812s:
            for qry in self._rqcl_812:
                d['commands'].append( self._set_qdict( i, qry ) )
                d['rqcl_all'].append( self._set_rlist( qry ) )
                i += 1
        else:
            if self.name in self._SPN16is:
                for qry in self._rqcl_16i:
                    d['commands'].append( self._set_qdict( i, qry ) )
                    d['rqcl_all'].append( self._set_rlist( qry ) )
                    i += 1

            if self.name in self._SPN16is_sp:
                for qry in self._rqcl_16i_sp:
                    d['commands'].append( self._set_qdict( i, qry ) )
                    d['rqcl_all'].append( self._set_rlist( qry ) )
                    i += 1

            if self.name in self._SPNCONs:
                pass

        d['cycle_time'] = i * self.ticker + self.ticker

        return d

    def _set_rlist(self, response):
        """ 
        returns a string with the first part of the expected aspen response
        """
        self.re_str='(!)|(\(\*\))|(\\r)|(\(1,3\))|(\?)'
        return re.sub(self.re_str, '', response)

    def _set_qdict(self, d, command):
        """
        returns a dict with the delay and command (repeated query)
        """
        delay = d * self.ticker
        return { 'delay':delay, 'command':command }


    def put_in_cache(self, data):
        """ Places a response from the aspen into the cache. 
        It replaces the previously cached response of the same type.
        """
        ided_responses = [i for i in self.cycle['rqcl_all'] if i in data]
        for response in ided_responses:
            self._cache[response] = (data, datetime.now())
            return succeed(data)
        return succeed(data)
            
    def get_from_cache(self, qry):
        #log.msg(qry)
        response = self._set_rlist(qry)
        try:
            return succeed(self._cache[response][0])
        except KeyError:
            return fail('no cache')
        except:
            return fail()

    def get_query_commands(self):
        return self.qry_commands

    def timeout(self):
        return self.cycle['cycle_time']

