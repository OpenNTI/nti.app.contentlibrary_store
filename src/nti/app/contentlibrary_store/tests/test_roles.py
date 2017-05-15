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
import unittest

from zope import component

from nti.app.contentlibrary_store.roles import get_descendants
from nti.app.contentlibrary_store.roles import get_collection_root
from nti.app.contentlibrary_store.roles import add_users_content_roles
from nti.app.contentlibrary_store.roles import get_users_content_roles
from nti.app.contentlibrary_store.roles import remove_users_content_roles

from nti.contentlibrary.interfaces import IFilesystemContentPackageLibrary

from nti.contentlibrary.filesystem import DynamicFilesystemLibrary as FileLibrary

from nti.dataserver.users import User

from nti.app.contentlibrary_store.tests import SharedConfiguringTestLayer

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans


class TestRoles(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    learning = u"tag:nextthought.com,2011-10:MN-HTML-MiladyCosmetology.learning_objectives"

    no_learning = u"tag:nextthought.com,2011-10:MN-HTML-NoCosmetology.learning_objectives"

    def setUp(self):
        dirname = os.path.dirname(__file__)
        library = FileLibrary(os.path.join(dirname, 'library'))
        library.syncContentPackages()
        component.provideUtility(library, IFilesystemContentPackageLibrary)

    def _create_user(self, username=u'nt@nti.com', password=u'temp001'):
        usr = User.create_user(self.ds, username=username, password=password)
        return usr

    @WithMockDSTrans
    def test_add_users_content_roles(self):
        user = self._create_user()
        roles_added = add_users_content_roles(user, (self.learning,))
        assert_that(roles_added, is_(1))

        roles_added = add_users_content_roles(user, (self.no_learning,))
        assert_that(roles_added, is_(0))

        roles = get_users_content_roles(user)
        assert_that(roles, is_([(u'mn', u'miladycosmetology.cosmetology')]))

    @WithMockDSTrans
    def test_remove_users_content_roles(self):
        user = self._create_user()
        roles_added = add_users_content_roles(user, (self.learning,))
        assert_that(roles_added, is_(1))

        roles_removed = remove_users_content_roles(user, (self.learning,))
        assert_that(roles_removed, is_(1))

    def test_get_descendants(self):
        unit = get_collection_root(self.learning)
        d = list(get_descendants(unit))
        assert_that(d, has_length(3))
