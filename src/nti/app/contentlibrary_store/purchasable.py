#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import lifecycleevent

from nti.app.contentlibrary_store import MessageFactory as _

from nti.app.contentlibrary_store.utils import get_context_fee
from nti.app.contentlibrary_store.utils import get_context_price
from nti.app.contentlibrary_store.utils import is_context_giftable
from nti.app.contentlibrary_store.utils import is_context_redeemable
from nti.app.contentlibrary_store.utils import get_purchasable_cutoff_date
from nti.app.contentlibrary_store.utils import get_bundle_purchasable_ntiid
from nti.app.contentlibrary_store.utils import get_context_purchasable_name
from nti.app.contentlibrary_store.utils import get_context_purchasable_title
from nti.app.contentlibrary_store.utils import get_package_purchasable_ntiid
from nti.app.contentlibrary_store.utils import is_context_enabled_for_purchase
from nti.app.contentlibrary_store.utils import get_context_purchasable_provider
from nti.app.contentlibrary_store.utils import get_purchasable_redeem_cutoff_date

from nti.app.contentlibrary_store.model import PurchasableContent
from nti.app.contentlibrary_store.model import PurchasableContentPackageBundle

from nti.app.contentlibrary_store.model import create_purchasable_content

from nti.contentlibrary.interfaces import IContentPackageBundle
from nti.contentlibrary.interfaces import IContentUnitHrefMapper

from nti.store.interfaces import IPurchasable

from nti.store.store import register_purchasable


def create_purchasable_from_context(context):
    giftable = is_context_giftable(context)
    redeemable = is_context_redeemable(context)
    public = is_context_enabled_for_purchase(context)
    provider = get_context_purchasable_provider(context)

    # find price
    fee = get_context_fee(context)
    price = get_context_price(context, provider)
    if price is None:
        return None
    amount = price.Amount
    currency = price.Currency
    fee = float(fee) if fee is not None else fee

    if IContentPackageBundle.providedBy(context):
        packages = context.ContentPackages
        factory = PurchasableContentPackageBundle
        ntiid = get_bundle_purchasable_ntiid(context, provider)
    else:
        packages = (context,)
        factory = PurchasableContent
        ntiid = get_package_purchasable_ntiid(context, provider)

    icon = thumbnail = None
    if packages:
        icon = packages[0].icon
        thumbnail = packages[0].thumbnail
        icon = IContentUnitHrefMapper(icon).href if icon else None
        if thumbnail:
            thumbnail = IContentUnitHrefMapper(thumbnail).href
        else:
            thumbnail = None

    purchase_cutoff_date = get_purchasable_cutoff_date(context)
    redeem_cutoff_date = get_purchasable_redeem_cutoff_date(context)

    if      purchase_cutoff_date \
        and redeem_cutoff_date \
        and purchase_cutoff_date > redeem_cutoff_date:
        msg = _(u'RedeemCutOffDate cannot be before PurchaseCutOffDate.')
        raise ValueError(msg)

    items = [context.ntiid]
    name = get_context_purchasable_name(context) or context.title
    title = get_context_purchasable_title(context) or context.title

    result = create_purchasable_content(ntiid=ntiid,
                                        items=items,
                                        name=name,
                                        title=title,
                                        provider=provider,
                                        public=public,
                                        fee=fee,
                                        amount=amount,
                                        currency=currency,
                                        giftable=giftable,
                                        redeemable=redeemable,
                                        description=context.description,
                                        redeem_cutoff_date=redeem_cutoff_date,
                                        purchase_cutoff_date=purchase_cutoff_date,
                                        # deprecated/legacy
                                        icon=icon,
                                        thumbnail=thumbnail,
                                        # initializer
                                        factory=factory)
    return result


def update_purchasable_context(purchasable, context):
    fee = get_context_fee(context)
    provider = get_context_purchasable_provider(context)
    price = get_context_price(context, provider)
    if price is None:  # price removed
        purchasable.Public = False
        logger.warn('Could not find price for %s', purchasable.NTIID)
    else:
        name = get_context_purchasable_name(context) or context.title
        title = get_context_purchasable_title(context) or context.title
        purchasable.Name = name
        purchasable.Title = title
        # Update price properties
        purchasable.Amount = price.Amount
        purchasable.Currency = price.Currency
        purchasable.Giftable = is_context_giftable(context)
        purchasable.Redeemable = is_context_redeemable(context)
        purchasable.Fee = float(fee) if fee is not None else fee
        purchasable.Public = is_context_enabled_for_purchase(context)
    return purchasable


def sync_purchasable_context(context):
    purchasable = IPurchasable(context, None)
    if purchasable is not None:
        update_purchasable_context(purchasable, context)
        lifecycleevent.modified(purchasable)
    else:
        purchasable = create_purchasable_from_context(context)
        if purchasable is not None:
            lifecycleevent.created(purchasable)
            register_purchasable(purchasable)
            purchasable.__parent__ = context
    return purchasable
