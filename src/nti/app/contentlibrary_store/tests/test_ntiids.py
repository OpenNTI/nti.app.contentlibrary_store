#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that

import unittest

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.app.contentlibrary_store.tests import SharedConfiguringTestLayer

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans


class TestResolvers(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    ntiid = u"tag:nextthought.com,2011-10:MN-purchasable_content-MiladyCosmetology.cosmetology"

    @WithMockDSTrans
    def test_finder(self):
        purchasable = find_object_with_ntiid(self.ntiid)
        assert_that(purchasable, is_not(none()))
