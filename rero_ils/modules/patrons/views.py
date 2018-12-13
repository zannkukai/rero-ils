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

"""Blueprint used for loading templates."""

from __future__ import absolute_import, print_function

from flask import Blueprint, jsonify, render_template
from flask_babelex import gettext as _
from flask_login import current_user, login_required
from flask_menu import register_menu
from werkzeug.exceptions import NotFound

from ..documents.api import Document
from ..items.api import Item
from ..loans.api import get_loans_by_patron_pid
from ..locations.api import Location
from .api import Patron
from .utils import user_has_patron

blueprint = Blueprint(
    'patrons',
    __name__,
    url_prefix='/patrons',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/profile')
@login_required
@register_menu(
    blueprint,
    'main.profile.profile',
    _('%(icon)s Profile', icon='<i class="fa fa-user fa-fw"></i>'),
    visible_when=user_has_patron
)
def profile():
    """Patron Profile Page."""
    patron = Patron.get_patron_by_user(current_user)
    if patron is None:
        raise NotFound()
    loans = get_loans_by_patron_pid(patron.pid)

    checkouts = []
    requests = []
    if loans:
        for loan in loans:
            document = Document.get_record_by_pid(loan['document_pid'])
            item = Item.get_record_by_pid(loan['item_pid'])
            loan['title'] = document['title']
            loan['call_number'] = item['call_number']
            loan['library_name'] = item.dumps()['library_name']
            if loan['state'] == 'ITEM_ON_LOAN':
                checkouts.append(loan)
            elif loan['state'] in (
                    'PENDING',
                    'ITEM_AT_DESK',
                    'ITEM_IN_TRANSIT_FOR_PICKUP'
            ):
                location = Location.get_record_by_pid(
                    loan['pickup_location_pid'])
                loan['pickup_location_name'] = ''
                if location:
                    loan['pickup_location_name'] = location.get('name', '')
                    requests.append(loan)
    return render_template(
        'rero_ils/patron_profile.html',
        record=patron,
        loans=checkouts,
        pendings=requests
    )


@blueprint.route('/logged_user', methods=['GET'])
@login_required
def logger_user():
    """Current logged user informations in JSON."""
    patron = Patron.get_patron_by_user(current_user)
    if patron is None:
        raise NotFound()
    return jsonify(patron.dumps())


@blueprint.app_template_filter('get_patron_from_barcode')
def get_patron_from_barcode(value):
    """Get patron from barcode."""
    return Patron.get_patron_by_barcode(value)


@blueprint.app_template_filter('get_patron_from_checkout_item_pid')
def get_patron_from_checkout_item_pid(item_pid):
    """Get patron from a checkout item pid."""
    from invenio_circulation.api import get_loan_for_item
    patron_pid = get_loan_for_item(item_pid)['patron_pid']
    return Patron.get_record_by_pid(patron_pid)


@blueprint.app_template_filter('get_checkout_loan_for_item')
def get_checkout_loan_for_item(item_pid):
    """Get patron from a checkout item pid."""
    from invenio_circulation.api import get_loan_for_item
    return get_loan_for_item(item_pid)


@blueprint.app_template_filter('get_patron_from_pid')
def get_patron_from_pid(patron_pid):
    """Get patron from pid."""
    return Patron.get_record_by_pid(patron_pid)


@blueprint.app_template_filter('get_location_name_from_pid')
def get_location_name_from_pid(location_pid):
    """Get location from pid."""
    from ..locations.api import Location
    return Location.get_record_by_pid(location_pid)['name']