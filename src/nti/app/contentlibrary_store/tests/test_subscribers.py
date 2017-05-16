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

import os
import unittest

from zope import component

from zope.event import notify

from nti.app.contentlibrary_store.roles import add_users_content_roles
from nti.app.contentlibrary_store.roles import get_users_content_roles

from nti.contentlibrary.interfaces import IFilesystemContentPackageLibrary

from nti.contentlibrary.filesystem import DynamicFilesystemLibrary as FileLibrary

from nti.dataserver.users import User

from nti.invitations.interfaces import IInvitationsContainer

from nti.invitations.utils import accept_invitation

from nti.store.interfaces import PA_STATE_SUCCESS
from nti.store.interfaces import PurchaseAttemptRefunded
from nti.store.interfaces import PurchaseAttemptSuccessful
from nti.store.interfaces import GiftPurchaseAttemptRedeemed

from nti.store.invitations import create_store_purchase_invitation

from nti.store.purchase_history import get_purchase_attempt

from nti.store.store import get_gift_code

from nti.app.contentlibrary_store.tests import create_and_register_gift_attempt
from nti.app.contentlibrary_store.tests import create_and_register_purchase_attempt

from nti.app.contentlibrary_store.tests import SharedConfiguringTestLayer

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans


class TestSubscribers(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    ntiid = u"tag:nextthought.com,2011-10:MN-purchasable_content-MiladyCosmetology.cosmetology"

    def setUp(self):
        dirname = os.path.dirname(__file__)
        library = FileLibrary(os.path.join(dirname, 'library'))
        library.syncContentPackages()
        component.provideUtility(library, IFilesystemContentPackageLibrary)

    def create_user(self, username=u'ichigo@bleach.org', password=u'temp001'):
        usr = User.create_user(self.ds, username=username, password=password)
        return usr

    @WithMockDSTrans
    def test_success(self):
        user = self.create_user()
        purchase = create_and_register_purchase_attempt(user, self.ntiid)
        notify(PurchaseAttemptSuccessful(purchase))
        roles = get_users_content_roles(user)
        assert_that(roles, is_([(u'mn', u'miladycosmetology.cosmetology')]))

    @WithMockDSTrans
    def test_refund_simple_purchase(self):
        user = self.create_user()
        add_users_content_roles(user, (self.ntiid,))
        purchase = create_and_register_purchase_attempt(user, self.ntiid)
        purchase.State = PA_STATE_SUCCESS
        notify(PurchaseAttemptRefunded(purchase))
        roles = get_users_content_roles(user)
        assert_that(roles, is_([]))

    @WithMockDSTrans
    def test_refund_invitation_purchase(self):
        user = self.create_user()
        add_users_content_roles(user, (self.ntiid,))
        # create invitation purchase attempt
        purchase = create_and_register_purchase_attempt(user, self.ntiid, 5)
        # accept invitation
        invite = create_store_purchase_invitation(purchase, receiver=user)
        invitations = component.getUtility(IInvitationsContainer)
        invitations.add(invite)
        accept_invitation(user, invite)
        # refund
        notify(PurchaseAttemptRefunded(purchase))
        roles = get_users_content_roles(user)
        assert_that(roles, is_([]))

    @WithMockDSTrans
    def test_refund_gift_purchase(self):
        ichigo = self.create_user()
        aizen = self.create_user(u'aizen@bleach.org',)
        # create gift purchase attempt
        purchase = create_and_register_gift_attempt(ichigo.username,
                                                    aizen.username, 
                                                    self.ntiid)
        code = get_gift_code(purchase)
        # accept gift
        notify(GiftPurchaseAttemptRedeemed(purchase, aizen, code=code))
        # refund
        target = purchase.TargetPurchaseID
        attempt = get_purchase_attempt(target)
        assert_that(attempt, is_not(none()))
        notify(PurchaseAttemptRefunded(attempt))
        roles = get_users_content_roles(aizen)
        assert_that(roles, is_([]))
