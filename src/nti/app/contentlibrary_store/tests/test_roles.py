#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that

import os

from zope import component

from nti.app.contentlibrary_store.roles import resolve
from nti.app.contentlibrary_store.roles import get_descendants
from nti.app.contentlibrary_store.roles import add_users_content_roles
from nti.app.contentlibrary_store.roles import get_users_content_roles
from nti.app.contentlibrary_store.roles import remove_users_content_roles

from nti.contentlibrary.interfaces import IFilesystemContentPackageLibrary

from nti.contentlibrary.filesystem import DynamicFilesystemLibrary as FileLibrary

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.dataserver.tests import mock_dataserver


class TestRoles(ApplicationLayerTest):

    learning = "tag:nextthought.com,2011-10:MN-HTML-MiladyCosmetology.learning_objectives"

    no_learning = "tag:nextthought.com,2011-10:MN-HTML-NoCosmetology.learning_objectives"

    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.library = FileLibrary(os.path.join(dirname, 'library'))
        self.library.syncContentPackages()
        component.provideUtility(self.library, IFilesystemContentPackageLibrary)

    def tearDown(self):
        gsm = component.getGlobalSiteManager()
        gsm.unregisterUtility(self.library, IFilesystemContentPackageLibrary)
        
    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_add_users_content_roles(self):
        with mock_dataserver.mock_db_trans(self.ds):
            user = self._create_user(u'ichigo@bleach.org', password=u'temp001')
            roles_added = add_users_content_roles(user, (self.learning,))
            assert_that(roles_added, is_(1))
    
            roles_added = add_users_content_roles(user, (self.no_learning,))
            assert_that(roles_added, is_(0))
    
            roles = get_users_content_roles(user)
            assert_that(roles, is_([('mn', 'miladycosmetology.cosmetology')]))

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_remove_users_content_roles(self):
        with mock_dataserver.mock_db_trans(self.ds):
            user = self._create_user(u'ichigo@bleach.org', password=u'temp001')
            roles_added = add_users_content_roles(user, (self.learning,))
            assert_that(roles_added, is_(1))
    
            roles_removed = remove_users_content_roles(user, (self.learning,))
            assert_that(roles_removed, is_(1))

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_get_descendants(self):
        with mock_dataserver.mock_db_trans(self.ds):
            unit = resolve(self.learning)
            d = list(get_descendants(unit))
            assert_that(d, has_length(3))
