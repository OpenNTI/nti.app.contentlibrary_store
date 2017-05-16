#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.app.store.subscribers import safe_send_purchase_confirmation
from nti.app.store.subscribers import store_purchase_attempt_successful

from nti.app.contentlibrary_store.interfaces import IPurchasableContent

from nti.appserver.interfaces import IApplicationSettings

from nti.store.interfaces import IPurchaseAttempt
from nti.store.interfaces import IPurchaseAttemptSuccessful

from nti.store.purchasable import Purchasable
from nti.store.purchasable import get_purchasable


def is_purchasable_content(purchasable):
    return IPurchasableContent.providedBy(purchasable) \
        or type(purchasable) is Purchasable  # legacy


@component.adapter(IPurchaseAttempt, IPurchaseAttemptSuccessful)
def _purchase_attempt_successful(purchase, event):
    items = purchase.Items
    purchasable = get_purchasable(items[0]) if items else None
    if purchasable is None or not is_purchasable_content(purchasable):
        return
    store_purchase_attempt_successful(event)
    settings = component.queryUtility(IApplicationSettings) or {}
    email_line = settings.get('purchase_additional_confirmation_addresses') or ''
    for email in email_line.split():
        safe_send_purchase_confirmation(event, email)
