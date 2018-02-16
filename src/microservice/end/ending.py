# -*- encoding: utf-8 -*-
"""
Ending Module

ReST endpoints

"""
from __future__ import generator_stop

import sys
import os
from collections import OrderedDict as ODict, deque
import enum
try:
    import simplejson as json
except ImportError:
    import json

import datetime
import mimetypes

import arrow
import falcon
import libnacl

from ioflo.aid.sixing import *
from ioflo.aid import lodict
from ioflo.aid import timing
from ioflo.aid import classing
from ioflo.aio.http import httping

from ioflo.aid import getConsole

from .. import microserviceconstnclass
from ..microserviceconstnclass import SEPARATOR, ANON_EXPIRATION_DELAY, ValidationError

from ..db import dbing
from ..help import helping

#from ..keep import keeping


console = getConsole()

DEFAULT_STATIC_BASE_PATH = "/"
THING_BASE_PATH = "/reputee"

import json
from wsgiref import simple_server
import falcon
import requests
from pprint import pprint as pp
import numpy as np

class StorageEngine(object):
    def __init__(self):
        self.store = {} 

    def add_thing(self, thing):
        if len(self.store.keys()) == 0: current =0
        else: current = max(self.store.keys()) 
        self.store[current+1] = thing

def reputes_type(db, rtype, nr):
    '''
    for a given name_of_reputee(nr), return reputes of particular type(rtype) = reach or clarity
    ''' 
    return [i for i in db.store.values() if i['reputee'] == nr and i["repute"]['feature'] ==rtype]

def values_for_rid(reputes):
    '''
    return values for reputes and amount of unique values(rid's)
    it is assumed that reputes already belong to particular type(reach/clarity)
    '''
    rids=[];values=[]
    for i in reputes:
        if i['repute']['rid'] not in rids:
            rids.append(i['repute']['rid']); values.append(i['repute']['value'])    
    return values , len(rids)        

def S(a,b,x):
    '''
    S function as described in the notes
    perhaps, bounds have to be verified
    ''' 
    if a>=x: return 0
    if x>=a and ((a+b)/2.0) >= x : return 2*((x-a)/float(b-a))**2
    if x >= ((a+b)/2.0) and b>=x : return  1 - 2*((x-a)/float(b-a))**2
    if x >= b : return 1 

class ThingsResource(object):

    def on_get(self, req, resp, reputee):
    
        '''        
	try:
            doc = json.loads(req.stream.read())

        except KeyError:
            raise falcon.HTTPBadRequest('Missing thing','A thing must be submitted in the request body.')
        '''         
        print (reputee);
        name_of_reputee = reputee # get reputee name
        '''
        reputes_r= reputes_type(self.db, 'reach', name_of_reputee)
        reputes_c= reputes_type(self.db,'clarity', name_of_reputee)
        values_r , x_r = values_for_rid(reputes_r); values_c, x_c = values_for_rid( reputes_c)
        
        
        reach_score = np.mean(values_r); reach_conf = S(a = 2, b = 6, x = x_r) 
        clarity_score = np.mean(values_c) ;  clarity_conf = S(a = 4, b = 8, x = x_c)
        clout_score = 0.1*(reach_score*reach_conf + clarity_score*clarity_conf)/float(reach_conf + clarity_conf)
        clout_conf = min(reach_conf,clarity_conf)
        pp(reputes_r);pp(reputes_c);pp(values_r); pp(values_c)
                
        
        result = {"reputee":  name_of_reputee,
                  "clout": {       
                    "score": clout_score, 
                    "confidence": clout_conf  },
                  "reach": {       
                    "score": reach_score,
                    "confidence": reach_conf    },
                  "clarity":      {       
                    "score": clarity_score,
                    "confidence": clarity_conf    }}
        '''
        
        result = dbing.getReputation(reputee)

        if result is not None:
            resp.media = json.loads(result) #resp.context['result'] = result
            resp.status = falcon.HTTP_200
        else:
            resp.media = ""
            resp.status = falcon.HTTP_404

    def on_post(self, req, resp): 
        body = req.stream.read()
        try:
            doc = json.loads(body)#json.loads(req.stream.read().decode('utf-8'));
        except KeyError:
            raise falcon.HTTPBadRequest('Missing thing','A thing must be submitted in the request body.')
        except:
            raise falcon.HTTPBadRequest('Malformed request')
        
        signature = None
        try:
            signature = req.get_header('Signature')
        except KeyError:
            raise falcon.HTTPBadRequest('Missing signature')

        try:
            sig = signature.split('signer=')[1].split('"')[1]
        except AttributeError:
            raise falcon.HTTPBadRequest('Missing signature')

        dbing.putUnprocessed(body, sig)
#        proper_thing = self.db.add_thing(doc)
        resp.status = falcon.HTTP_201

class UserRegistration:
    def on_post(self, req, resp):
        body = req.stream.read()
        signature = None

        try:
            signature = req.get_header('Signature', default='no-signature')
            print(signature)

        except KeyError:
            raise falcon.HTTPBadRequest('Missing signature')

        if signature == 'no-signature':
            raise falcon.HTTPBadRequest('Missing signature')

        sig = None

        try:
            sig = signature.split('signer=')[1].split('"')[1]

        except IndexError:
            raise falcon.HTTPBadRequest('Invalid signature')

        except AttributeError:
            raise falcon.HTTPBadRequest('Missing signature')

        key = None
        try:
            doc = json.loads(body)
            key = doc['key']
            username = doc['username']

        except KeyError:
            raise falcon.HTTPBadRequest('Invalid registration information')

        try:
            if helping.verify64ub(sig, body, key):
                reg = dbing.RegisterUser(username, key)
                if reg:
                    resp.status = falcon.HTTP_201
                else:
                    resp.status = falcon.HTTP_409
                    resp.body = "Already exist"

            else:
                raise falcon.HTTPBadRequest('Invalid signature')

        except:
            raise falcon.HTTPBadRequest('Invalid signature')
        
        
def loadEnds(app, store):
    """
    Load endpoints for app with store reference
    This function provides the endpoint resource instances
    with a reference to the data store
    """
    thing = ThingsResource()
    userreg = UserRegistration()

    app.add_route('/reputee/', thing)
    app.add_route('/reputee/{reputee}', thing)
    app.add_route('/register/', userreg)

#    thing = ThingResource(store=store)
#    app.add_route('{}'.format(THING_BASE_PATH), thing)
#    app.add_route('{}/{reputee}'.format(THING_BASE_PATH), thing)
