#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

generation = 2

from zope import component
from zope import interface
from zope import lifecycleevent

from zope.component.hooks import site
from zope.component.hooks import setHooks

from zope.intid.interfaces import IIntIds

from ZODB.POSException import POSError

from nti.app.contentlibrary_store.interfaces import IPurchasableContentPackageBundle

from nti.dataserver.interfaces import IDataserver
from nti.dataserver.interfaces import IOIDResolver

from nti.site.hostpolicy import get_all_host_sites

from nti.site.utils import unregisterUtility

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IDataserver)
class MockDataserver(object):

    root = None

    def get_by_oid(self, oid, ignore_creator=False):
        resolver = component.queryUtility(IOIDResolver)
        if resolver is None:
            logger.warn("Using dataserver without a proper ISiteManager.")
        else:
            return resolver.get_object_by_oid(oid, ignore_creator=ignore_creator)
        return None


def do_evolve(context):
    setHooks()
    conn = context.connection
    root = conn.root()
    ds_folder = root['nti.dataserver']

    mock_ds = MockDataserver()
    mock_ds.root = ds_folder
    component.provideUtility(mock_ds, IDataserver)

    with site(ds_folder):
        assert component.getSiteManager() == ds_folder.getSiteManager(), \
               "Hooks not installed?"

        lsm = ds_folder.getSiteManager()
        intids = lsm.getUtility(IIntIds)

        seen = set()
        for current_site in get_all_host_sites():
            with site(current_site):
                registry = component.getSiteManager()
                for name, bundle in component.getUtilitiesFor(IPurchasableContentPackageBundle):
                    if name in seen:
                        continue
                    seen.add(name)
                    for func in (intids.unregister, lifecycleevent.removed):
                        try:
                            func(bundle)
                        except (POSError, TypeError):
                            pass
                    unregisterUtility(registry, name=name,
                                      provided=IPurchasableContentPackageBundle)

    component.getGlobalSiteManager().unregisterUtility(mock_ds, IDataserver)
    logger.info('Content library store evolution %s done.', generation)
    return seen


def evolve(context):
    """
    Evolve to gen 2 by removing PurchasableContentPackageBundleo objects
    """
    do_evolve(context)
