#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from zope.component.hooks import setHooks

import zope.testing.cleanup

from nti.dataserver.tests.mock_dataserver import DSInjectorMixin

from nti.testing.layers import GCLayerMixin
from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin


class SharedConfiguringTestLayer(ZopeComponentLayer,
                                 GCLayerMixin,
                                 ConfiguringLayerMixin,
                                 DSInjectorMixin):

    set_up_packages = ('nti.store',
                       'nti.dataserver',
                       'nti.contentlibrary',
                       'nti.externalization',
                       'nti.app.contentlibrary_store')

    @classmethod
    def setUp(cls):
        setHooks()  # in case something already tore this down
        cls.setUpPackages()

    @classmethod
    def tearDown(cls):
        cls.tearDownPackages()
        zope.testing.cleanup.cleanUp()

    @classmethod
    def testSetUp(cls, test=None):
        cls.setUpTestDS(test)

    @classmethod
    def testTearDown(cls):
        pass


import unittest

from nti.testing.base import AbstractTestBase


class ContentlibraryStoreLayerTest(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    get_configuration_package = AbstractTestBase.get_configuration_package.__func__


from nti.store.interfaces import PA_STATE_SUCCESS

from nti.store.gift_registry import register_gift_purchase_attempt

from nti.store.payments.stripe import STRIPE

from nti.store.purchase_history import register_purchase_attempt

from nti.store.purchase_order import PurchaseItem
from nti.store.purchase_order import create_purchase_order

from nti.store.purchase_attempt import create_purchase_attempt as purchase_attempt_creator

from nti.store.purchase_attempt import create_gift_purchase_attempt


def create_purchase_attempt(item, quantity=None, description=None):
    item = PurchaseItem(NTIID=item, Quantity=1)
    order = create_purchase_order(item, quantity=quantity)
    result = purchase_attempt_creator(order,
                                      processor=STRIPE,
                                      description=description or u'my charge')
    return result


def create_and_register_purchase_attempt(user, item, quantity=None, description=None):
    attempt = create_purchase_attempt(item, 
                                      quantity=quantity, 
                                      description=description)
    register_purchase_attempt(attempt, user)
    return attempt


def create_and_register_gift_attempt(creator, receiver, item, quantity=None, description=None):
    item = PurchaseItem(NTIID=item, Quantity=1)
    order = create_purchase_order(item, quantity=quantity)
    attempt = create_gift_purchase_attempt(creator=creator, 
                                           order=order, 
                                           processor=STRIPE, 
                                           state=PA_STATE_SUCCESS, 
                                           description=description or u'my gift',
                                           receiver=receiver)
    register_gift_purchase_attempt(creator, attempt)
    return attempt
