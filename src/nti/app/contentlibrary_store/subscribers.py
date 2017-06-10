#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.app.contentlibrary_store.interfaces import IPurchasableContent

from nti.app.contentlibrary_store.roles import add_users_content_roles

from nti.app.contentlibrary_store.roles import remove_users_content_roles

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.store.interfaces import IPurchaseAttempt
from nti.store.interfaces import IGiftPurchaseAttempt
from nti.store.interfaces import IPurchaseAttemptRefunded
from nti.store.interfaces import IRedeemedPurchaseAttempt
from nti.store.interfaces import IInvitationPurchaseAttempt
from nti.store.interfaces import IPurchaseAttemptSuccessful
from nti.store.interfaces import IRedeemedPurchaseAttemptRegistered

from nti.store.purchasable import Purchasable

from nti.store.purchase_history import get_purchase_attempt

from nti.store.store import get_purchase_by_code


def _is_purchasable_content(purchasable):
    return IPurchasableContent.providedBy(purchasable) \
        or type(purchasable) is Purchasable  # legacy


def _activate_items(purchase, user=None):
    for ntiid in purchase.Items or ():
        purchasable = find_object_with_ntiid(ntiid)
        if _is_purchasable_content(purchasable):
            user = user or purchase.creator
            add_users_content_roles(user, purchasable.Items)


@component.adapter(IPurchaseAttempt, IPurchaseAttemptSuccessful)
def _purchase_attempt_successful(purchase, _):
    # CS: We are assuming a non null quantity is for a bulk purchase
    # Therefore we don't modity content roles
    if purchase.Quantity:
        return
    # add roles
    _activate_items(purchase, purchase.creator)


def _return_items(purchase, user=None):
    for ntiid in purchase.Items or ():
        purchasable = find_object_with_ntiid(ntiid)
        if _is_purchasable_content(purchasable):
            user = user or purchase.creator
            remove_users_content_roles(user, purchasable.Items)


@component.adapter(IPurchaseAttempt, IPurchaseAttemptRefunded)
def _purchase_attempt_refunded(purchase, _):
    # CS: We are assuming a non null quantity is for a bulk purchase
    # Therefore we don't modity content roles
    if not purchase.Quantity:
        _return_items(purchase, purchase.creator)


@component.adapter(IInvitationPurchaseAttempt, IPurchaseAttemptRefunded)
def _invitation_purchase_attempt_refunded(purchase, _):
    # return all items from linked purchases (redemptions) and refund them
    for username, ntiid in purchase.consumerMap.items():
        purchase = get_purchase_attempt(ntiid)
        _return_items(purchase, username)


@component.adapter(IRedeemedPurchaseAttempt, IPurchaseAttemptRefunded)
def _redeemed_purchase_attempt_refunded(purchase, _):
    code = purchase.RedemptionCode
    source = get_purchase_by_code(code)
    if IGiftPurchaseAttempt.providedBy(source):
        _return_items(purchase, purchase.creator)


@component.adapter(IRedeemedPurchaseAttempt, IRedeemedPurchaseAttemptRegistered)
def _redeemed_purchase_attempt_registered(purchase, _):
    _activate_items(purchase, purchase.creator)
