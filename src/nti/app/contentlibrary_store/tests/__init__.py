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
