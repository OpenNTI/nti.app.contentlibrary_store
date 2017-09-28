#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import contains
from hamcrest import has_length
from hamcrest import assert_that

import fudge

from nti.app.contentlibrary_store.generations.evolve2 import do_evolve

from nti.app.contentlibrary_store.interfaces import IPurchasableContentPackageBundle

from nti.app.contentlibrary_store.model import PurchasableContentPackageBundle

from nti.site import get_all_host_sites

from nti.store.store import register_purchasable

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.dataserver.tests.mock_dataserver import mock_db_trans


class TestEvolve(ApplicationLayerTest):

    @WithSharedApplicationMockDS
    def test_do_evolve(self):
        with mock_db_trans(self.ds):
            sites = list(get_all_host_sites())
            site_name = sites[0].__name__ if sites else None
            if not site_name:
                return
        with mock_db_trans(self.ds, site_name) as conn:
            item = PurchasableContentPackageBundle()
            conn.add(item)
            register_purchasable(item, 'foo', IPurchasableContentPackageBundle)

        with mock_db_trans(self.ds) as conn:
            context = fudge.Fake().has_attr(connection=conn)
            removed = do_evolve(context)
            assert_that(removed, has_length(1))
            assert_that(removed, contains('foo'))
