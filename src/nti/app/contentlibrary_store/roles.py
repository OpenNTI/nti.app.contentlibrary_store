#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import component

from nti.app.contentlibrary.utils import role_for_content_bundle
from nti.app.contentlibrary.utils import role_for_content_package

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage
from nti.contentlibrary.interfaces import IContentPackageBundle

from nti.dataserver.authorization import CONTENT_ROLE_PREFIX

from nti.dataserver.interfaces import IMutableGroupMember

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.store import get_user

from nti.traversal.traversal import find_interface


def get_descendants(unit):
    yield unit
    last = unit
    for node in get_descendants(unit):
        for child in node.children:
            yield child
            last = child
        if last == node:
            return


def resolve(ntiid):
    result = find_object_with_ntiid(ntiid)
    if IContentUnit.providedBy(result):
        result = find_interface(result, IContentPackage, strict=False)
    elif not IContentPackageBundle.providedBy(result):
        result = None
    return result


def get_role(context):
    if IContentPackageBundle.providedBy(context):
        return role_for_content_bundle(context)
    return role_for_content_package(context)


def add_users_content_roles(user, items):
    """
    Add the content roles to the given user

    :param user: The user object
    :param items: List of ntiids
    """

    if isinstance(items, six.string_types):
        items = set(items.split())

    user = get_user(user)
    if user is None or not items:
        return 0

    # parse current roles
    roles_to_add = []
    member = component.getAdapter(user,
                                  IMutableGroupMember,
                                  CONTENT_ROLE_PREFIX)
    current_roles = {x.id: x for x in member.groups}
    # resolve new roles
    for item in items:
        source = resolve(item)
        if source is None:
            continue
        role = get_role(source)
        if role.id not in current_roles:
            logger.debug("Role %s added to %s", role.id, user)
            roles_to_add.append(role)
    # add new roles
    if roles_to_add:
        current_roles = list(current_roles.values())
        member.setGroups(current_roles + roles_to_add)
    return len(roles_to_add)


def remove_users_content_roles(user, items):
    """
    Remove the content roles from the given user

    :param user: The user object
    :param items: List of ntiids
    """
    if isinstance(items, six.string_types):
        items = set(items.split())

    user = get_user(user)
    if not user or not items:
        return 0
    member = component.getAdapter(user,
                                  IMutableGroupMember,
                                  CONTENT_ROLE_PREFIX)
    if not member.hasGroups():
        return 0

    # parse current roles
    roles_to_remove = []
    current_roles = {x.id.lower(): x for x in member.groups}
    current_size = len(current_roles)
    for item in items:
        source = resolve(item)
        if source is None:
            continue
        role = get_role(source)
        roles_to_remove.append(role.id)
    # remove from current roles
    for r in roles_to_remove:
        current_roles.pop(r, None)
    # set new roles
    current_roles = list(current_roles.values())
    member.setGroups(current_roles)
    return current_size - len(current_roles)


def get_users_content_roles(user):
    """
    Return a list of tuples with the user content roles

    :param user: The user object
    """
    user = get_user(user)
    member = component.getAdapter(user,
                                  IMutableGroupMember,
                                  CONTENT_ROLE_PREFIX)
    result = []
    for x in member.groups or ():
        if x.id.startswith(CONTENT_ROLE_PREFIX):
            spl = x.id[len(CONTENT_ROLE_PREFIX):].split(':')
            if len(spl) >= 2:
                result.append((spl[0], spl[1]))
    return result
