#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
from hamcrest import has_key
from hamcrest import assert_that
from hamcrest import has_entries
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from nti.app.contentlibrary_store.model import IPurchasableContent

from nti.app.contentlibrary_store.model import create_purchasable_content

from nti.externalization.externalization import to_external_object

from nti.app.contentlibrary_store.tests import SharedConfiguringTestLayer


class TestModel(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    processor = 'stripe'

    def test_create_content(self):
        default_date_str = u"2025-06-13T04:59:00+00:00"
        purchasable = create_purchasable_content(
                ntiid=u'tag:nextthought.com,2011-10:NTI-purchasable_content-LSTD_1153',
                name=u"A History of the United States",
                provider=u"Janux",
                amount=500,
                items=(u"tag:nextthought.com,2011-10:NTI-HTML-Spring2015_LSTD_1153",),
                title=u"A History of the United States",
                author=u"Janux",
                giftable=True,
                description=u"History is about more than the people",
                redeem_cutoff_date=default_date_str,
                purchase_cutoff_date=default_date_str,
        )

        assert_that(purchasable, validly_provides(IPurchasableContent))
        assert_that(purchasable, verifiably_provides(IPurchasableContent))

        ext = to_external_object(purchasable)
        assert_that(ext,
                    has_entries('Amount', 500.0,
                                'Class', 'PurchasableContent',
                                'Currency', 'USD',
                                'Description', 'History is about more than the people',
                                'Giftable', True,
                                'NTIID', 'tag:nextthought.com,2011-10:NTI-purchasable_content-LSTD_1153',
                                'MimeType', 'application/vnd.nextthought.store.purchasablecontent',
                                'Public', True,
                                'Redeemable', False,
                                'Title', 'A History of the United States',
                                'PurchaseCutOffDate', default_date_str,
                                'RedeemCutOffDate', default_date_str))

        ext = to_external_object(purchasable, name="summary")
        assert_that(ext, does_not(has_key('Icon')))
        assert_that(ext, does_not(has_key('Public')))
        assert_that(ext, does_not(has_key('License')))
        assert_that(ext, does_not(has_key('Thumbnail')))
        assert_that(ext, does_not(has_key('Description')))
        assert_that(ext, does_not(has_key('EndDate')))
        assert_that(ext, does_not(has_key('Preview')))
        assert_that(ext, does_not(has_key('Featured')))
        assert_that(ext, does_not(has_key('Duration')))
        assert_that(ext, does_not(has_key('StartDate')))
        assert_that(ext, does_not(has_key('Signature')))
        assert_that(ext, does_not(has_key('Department')))
        assert_that(ext, does_not(has_key('Communities')))
