#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from itertools import chain

from zope import component

from zope.traversing.api import traverse

from nti.app.contentlibrary_store import PURCHASABLE_CONTENT
from nti.app.contentlibrary_store import PURCHASABLE_CONTENT_BUNDLE

from nti.contentlibrary import HTML
from nti.contentlibrary import BUNDLE

from nti.contentlibrary.utils import get_content_vendor_info

from nti.ntiids.ntiids import get_parts
from nti.ntiids.ntiids import make_ntiid

from nti.store.interfaces import IPrice
from nti.store.interfaces import IPurchasable

from nti.store.model import Price


def get_vendor_info(context):
    info = get_content_vendor_info(context, False)
    return info or {}


def has_vendor_info(context):
    return bool(get_vendor_info(context))


def is_context_enabled_for_purchase(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Enabled', default=False)


def is_context_giftable(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Giftable', default=False)


def is_context_redeemable(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Redeemable', default=False)


def get_context_purchasable_provider(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Provider', default=None)


def get_context_purchasable_name(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Name', default=None)


def get_purchasable_redeem_cutoff_date(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/RedeemCutOffDate', default=None)


def get_purchasable_cutoff_date(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/PurchaseCutOffDate', default=None)


def get_context_purchasable_title(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Title', default=None)


def get_context_purchasable_fee(context):
    vendor_info = get_vendor_info(context)
    return traverse(vendor_info, 'NTI/Purchasable/Fee', default=None)
get_context_fee = get_context_purchasable_fee


def get_context_price(context, *names):
    for name in chain(names, ('',)) if names else ('',):
        result = component.queryAdapter(context,  IPrice, name=name)
        if result is not None:
            return result
    return None


def get_context_purchasable_ntiid(context, nttype, provider=None):
    parts = get_parts(context.ntiid)
    provider = provider or parts.provider
    ntiid = make_ntiid(date=parts.date,
                       nttype=nttype,
                       provider=provider,
                       specific=parts.specific)
    return ntiid


def get_package_purchasable_ntiid(context, provider=None):
    nttype = PURCHASABLE_CONTENT
    return get_context_purchasable_ntiid(context, nttype, provider)


def get_bundle_purchasable_ntiid(context, provider=None):
    nttype = PURCHASABLE_CONTENT_BUNDLE
    return get_context_purchasable_ntiid(context, nttype, provider)


def get_context_ntiid_from_purchasable(context, nttype):
    purchasable = IPurchasable(context)
    parts = get_parts(purchasable.NTIID)
    ntiid = make_ntiid(date=parts.date,
                       nttype=nttype,
                       provider=parts.provider,
                       specific=parts.specific)
    return ntiid


def get_bundle_ntiid_from_purchasable(context):
    return get_context_ntiid_from_purchasable(context, BUNDLE)


def get_package_ntiid_from_purchasable(context):
    return get_context_ntiid_from_purchasable(context, HTML)


def get_nti_context_price(context):
    vendor_info = get_vendor_info(context)
    amount = traverse(vendor_info, 'NTI/Purchasable/Price', default=None)
    currency = traverse(vendor_info,
                        'NTI/Purchasable/Currency',
                        default=u'USD')
    if amount is not None:
        result = Price(Amount=float(amount), Currency=currency)
        return result
    return None
