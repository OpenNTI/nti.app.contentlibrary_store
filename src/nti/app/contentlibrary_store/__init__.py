#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.app.store import MessageFactory

#: Purchasable content NTIID type
PURCHASABLE_CONTENT = u'purchasable_content'

#: Purchasable content package bundle NTIID type
PURCHASABLE_CONTENT_PACKAGE_BUNDLE = u'purchasable_content_package_bundle'
