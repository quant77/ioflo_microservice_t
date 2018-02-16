# -*- coding: utf-8 -*-
"""
Behaviors
"""
from __future__ import generator_stop

import sys
import os


# Import Python libs
from collections import deque

try:
    import simplejson as json
except ImportError:
    import json

import datetime

# Import ioflo libs
from ioflo.aid.sixing import *
from ioflo.aid.odicting import odict
from ioflo.base import doify
from ioflo.aid import  timing
from ioflo.aid import getConsole

from ..db import dbing
from ..help import helping
from ..prime import priming

console = getConsole()

@doify('ReputationWorker', ioinits=odict(test=""))
def reputationWorker(self, **kwa):
    dbing.processRecord()

