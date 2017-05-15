#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.store.interfaces import IPurchasable
from nti.store.interfaces import IPurchasableChoiceBundle


class IPurchasableContent(IPurchasable):
    pass


class IPurchasableContentChoiceBundle(IPurchasableChoiceBundle,
                                      IPurchasableContent):
    pass
