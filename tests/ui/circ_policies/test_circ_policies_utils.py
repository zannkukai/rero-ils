# -*- coding: utf-8 -*-
#
# This file is part of RERO ILS.
# Copyright (C) 2017 RERO.
#
# RERO ILS is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# RERO ILS is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RERO ILS; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, RERO does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""CircPolicy Record tests."""

from __future__ import absolute_import, print_function

import pytest

from rero_ils.modules.circ_policies.api import CircPoliciesSearch, \
    CircPolicy, circ_policy_id_fetcher


def test_circ_policy_search(
    app,
    circ_policy,
    circ_policy_short,
    circ_policy_short_library
):
    """Test Find circ policy"""
    library_pid = 'lib1'
    patron_type_pid = 'ptty1'
    item_type_pid = 'itty1'
    cipo = CircPolicy.provide_circ_policy(
        library_pid,
        patron_type_pid,
        item_type_pid
    )
    assert cipo.pid == 'cipo2'
    # return library cipo when pair exists.
    library_pid = 'lib1'
    patron_type_pid = 'ptty2'
    item_type_pid = 'itty2'
    cipo = CircPolicy.provide_circ_policy(
        library_pid,
        patron_type_pid,
        item_type_pid
    )
    assert cipo.pid == 'cipo3'
    # return default cipo when pair does not exists.
    library_pid = 'lib2'
    patron_type_pid = 'ptty2'
    item_type_pid = 'itty2'
    cipo = CircPolicy.provide_circ_policy(
        library_pid,
        patron_type_pid,
        item_type_pid
    )
    assert cipo.pid == 'cipo1'
    # return default when pair is not set anywhere.
    library_pid = 'lib1'
    patron_type_pid = 'ptty3'
    item_type_pid = 'itty2'
    cipo = CircPolicy.provide_circ_policy(
        library_pid,
        patron_type_pid,
        item_type_pid
    )
    assert cipo.pid == 'cipo1'
    # return default when pair is not set anywhere.
    library_pid = 'lib1'
    patron_type_pid = 'ptty1'
    item_type_pid = 'itty2'
    cipo = CircPolicy.provide_circ_policy(
        library_pid,
        patron_type_pid,
        item_type_pid
    )
    assert cipo.pid == 'cipo1'

    # Capture error when pair is not correctly set.
    library_pid = 'lib1'
    patron_type_pid = 'ptty1'
    item_type_pid = 'itty2'
    result = CircPoliciesSearch().filter(
            'term',
            policy_library_level=True
        ).filter(
            'term',
            settings__patron_type__pid=patron_type_pid
        ).filter(
            'term',
            settings__item_type__pid=item_type_pid
        ).filter(
            'term',
            libraries__pid=library_pid
        ).source().scan()
    with pytest.raises(StopIteration):
        assert not next(result)