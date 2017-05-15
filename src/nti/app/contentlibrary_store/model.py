#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.app.contentlibrary_store.interfaces import IPurchasableContent
from nti.app.contentlibrary_store.interfaces import IPurchasableContentChoiceBundle

from nti.store.purchasable import Purchasable
from nti.store.purchasable import create_purchasable


@interface.implementer(IPurchasableContent)
class PurchasableContent(Purchasable):
    pass


@interface.implementer(IPurchasableContentChoiceBundle)
class PurchasableContentChoiceBundle(PurchasableContent):
    __external_class_name__ = 'PurchasableContentChoiceBundle'
    IsPurchasable = False


def create_purchasable_content(ntiid, provider, amount, currency=u'USD', items=(), fee=None,
                               title=None, license_=None, author=None, description=None,
                               icon=None, thumbnail=None, discountable=False, giftable=False,
                               redeem_cutoff_date=None, purchase_cutoff_date=None,
                               redeemable=False, bulk_purchase=True, public=True,
                               vendor_info=None, factory=PurchasableContent, **kwargs):

    result = create_purchasable(ntiid=ntiid, provider=provider,  amount=amount, currency=currency,
                                items=items, fee=fee, title=title, license_=license_, author=author,
                                description=description, icon=icon, thumbnail=thumbnail,
                                discountable=discountable, giftable=giftable,
                                redeem_cutoff_date=redeem_cutoff_date,
                                purchase_cutoff_date=purchase_cutoff_date,
                                redeemable=redeemable, bulk_purchase=bulk_purchase, public=public,
                                vendor_info=vendor_info, factory=factory, **kwargs)
    return result
