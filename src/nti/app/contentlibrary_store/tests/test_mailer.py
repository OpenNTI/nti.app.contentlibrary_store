#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import contains_string

import os
from quopri import decodestring

import transaction

from zope import component

from zope.event import notify

from pyramid.testing import DummyRequest

from nti.contentlibrary.interfaces import IFilesystemContentPackageLibrary

from nti.contentlibrary.filesystem import DynamicFilesystemLibrary as FileLibrary

from nti.dataserver.users import User

from nti.dataserver.users.interfaces import IUserProfile

from nti.store.charge import UserAddress
from nti.store.charge import PaymentCharge

from nti.store.interfaces import PA_STATE_SUCCESS
from nti.store.interfaces import PurchaseAttemptSuccessful

from nti.store.pricing import create_priced_item
from nti.store.pricing import create_pricing_results

from nti.app.contentlibrary_store.tests import create_and_register_purchase_attempt

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.app.testing.testing import ITestMailDelivery

from nti.dataserver.tests import mock_dataserver


class TestMailer(ApplicationLayerTest):

    processor = u'stripe'

    ntiid = u"tag:nextthought.com,2011-10:MN-purchasable_content-MiladyCosmetology.cosmetology"

    def setUp(self):
        dirname = os.path.dirname(__file__)
        library = FileLibrary(os.path.join(dirname, 'library'))
        library.syncContentPackages()
        component.provideUtility(library, IFilesystemContentPackageLibrary)

    def create_user(self, username=u'ichigo@bleach.org', password=u'temp001'):
        user = User.create_user(self.ds, username=username, password=password)
        IUserProfile(user).email = username
        return user

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_mailer(self):
        with mock_dataserver.mock_db_trans(self.ds):
            user = self.create_user()
            purchase = create_and_register_purchase_attempt(user, self.ntiid)
            purchase.State = PA_STATE_SUCCESS
            # price
            item = create_priced_item(self.ntiid, 100)
            pricing = create_pricing_results((item,), 100)
            pricing.TotalNonDiscountedPrice = 100
            purchase.Pricing = pricing
            # create charge
            address = UserAddress.create(u"1 Infinite Loop", None, u"Cupertino", u"CA",
                                         u"95014", u"USA")
            charge = PaymentCharge(Name=u'Ichigo',
                                   Amount=100.0,
                                   Currency=u'USD',
                                   CardLast4=1234,
                                   Address=address)
            notify(PurchaseAttemptSuccessful(purchase, charge, request=DummyRequest()))

            mailer = component.getUtility(ITestMailDelivery)
            assert_that(mailer.queue, has_length(1))
            msg = mailer.queue[0]

            assert_that(msg, has_property('body'))
            body = decodestring(msg.body)
            assert_that(body, contains_string(user.username))

            transaction.abort()
