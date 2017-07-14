#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property

import os

from zope import component

from nti.contentlibrary.interfaces import IContentPackageBundle
from nti.contentlibrary.interfaces import IContentPackageBundleLibrary
from nti.contentlibrary.interfaces import IFilesystemContentPackageLibrary

from nti.contentlibrary.bundle import ContentPackageBundleLibrary
from nti.contentlibrary.bundle import _ContentPackageBundleLibrarySynchronizer

from nti.contentlibrary.filesystem import FilesystemBucket 
from nti.contentlibrary.filesystem import DynamicFilesystemLibrary as FileLibrary

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.store.interfaces import IPurchasable

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.dataserver.tests import mock_dataserver


class TestPurchasable(ApplicationLayerTest):

    bundle_ntiid = "tag:nextthought.com,2011-10:MN-Bundle-Milady"

    def _library(self):
        dirname = os.path.dirname(__file__)
        self.library = FileLibrary(os.path.join(dirname, 'library'))
        self.library.syncContentPackages()
        component.provideUtility(self.library, IFilesystemContentPackageLibrary)
        return self.library

    def _bundles(self):
        dirname = os.path.dirname(__file__)
        bucket = FilesystemBucket(name='library')
        bucket.absolute_path = os.path.join(dirname, 'library', 'ContentPackageBundles')
        self.bundles = ContentPackageBundleLibrary()
        component.provideUtility(self.bundles, IContentPackageBundleLibrary)
        sync = _ContentPackageBundleLibrarySynchronizer(self.bundles)
        sync.syncFromBucket(bucket)

    def setUp(self):
        self._library()
        self._bundles()

    def tearDown(self):
        gsm = component.getGlobalSiteManager()
        gsm.unregisterUtility(self.bundles, IContentPackageBundleLibrary)
        gsm.unregisterUtility(self.library, IFilesystemContentPackageLibrary)

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_purchasable(self):
        with mock_dataserver.mock_db_trans(self.ds):
            bundle = find_object_with_ntiid(self.bundle_ntiid)
            assert_that(bundle, is_not(none()))
            
            purchasable = IPurchasable(bundle, None)
            assert_that(purchasable, is_not(none()))
            assert_that(purchasable, 
                        has_property('__parent__', is_(bundle)))
            assert_that(purchasable, 
                        has_property('Amount', is_(149.0)))
            
            bundle = IContentPackageBundle(purchasable, None)
            assert_that(bundle, is_not(none()))
