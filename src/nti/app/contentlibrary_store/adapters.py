#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.app.contentlibrary_store.utils import get_nti_context_price
from nti.app.contentlibrary_store.utils import get_bundle_purchasable_ntiid
from nti.app.contentlibrary_store.utils import get_context_purchasable_provider
from nti.app.contentlibrary_store.utils import get_bundle_ntiid_from_purchasable

from nti.contentlibrary.interfaces import IContentPackageBundle

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.store.interfaces import IPrice
from nti.store.interfaces import IPurchasable

from nti.store.store import get_purchasable


@interface.implementer(IPrice)
def _nti_context_price_finder(context):
    return get_nti_context_price(context)


@interface.implementer(IPurchasable)
@component.adapter(IContentPackageBundle)
def _bundle_to_purchasable(bundle):
    provider = get_context_purchasable_provider(bundle)
    ntiid = get_bundle_purchasable_ntiid(bundle, provider)
    return get_purchasable(ntiid) if ntiid else None


@component.adapter(IPurchasable)
@interface.implementer(IContentPackageBundle)
def _purchasable_to_bundle(purchasable):
    ntiid = get_bundle_ntiid_from_purchasable(purchasable)
    return find_object_with_ntiid(ntiid) if ntiid else None
