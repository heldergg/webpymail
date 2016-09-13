# sabapp - Simple Address Book Application
# Copyright (C) 2008 Helder Guerreiro

# This file is part of sabapp.
#
# sabapp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sabapp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sabapp.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

import urllib.request
import urllib.parse
import urllib.error

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .forms import AddressForm, ComposeToForm
from .models import Address
from themesapp.shortcuts import render

# Views:


@login_required
def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=int(address_id),
                                      user=request.user, ab_type=1)
    except ObjectDoesNotExist:
        raise Http404

    address.delete()

    return redirect('browse_addresses')


@login_required
def manage_address(request, address_id=None):
    '''Add an address to the user's address book'''
    context = {}
    next = request.GET.get('next', 'browse_addresses')
    context['next'] = next

    if address_id:
        try:
            address = Address.objects.get(id=int(address_id),
                                          user=request.user, ab_type=1)
        except ObjectDoesNotExist:
            raise Http404

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(next)
        if address_id:
            form = AddressForm(request.POST, instance=address)
        else:
            form = AddressForm(request.POST)
        if form.is_valid():
            # Save the new address
            address = form.save(commit=False)
            address.user = request.user
            address.imap_server = request.session['host']
            address.ab_type = 1
            address.save()
            return redirect(next)
        else:
            # Show errors:
            context['form'] = form
    else:
        # Empty form
        if address_id:
            context['form'] = AddressForm(instance=address)
        else:
            # Try to get initialization values
            first_name = request.GET.get('first_name', '')
            last_name = request.GET.get('last_name', '')
            email = request.GET.get('email', '')
            context['form'] = AddressForm(data={'first_name': first_name,
                                                'last_name': last_name,
                                                'email': email})

    return render(request, 'sab/manage_address.html', context)


@login_required
def browse_addresses(request):
    address_list = Address.objects.for_request(request)

    return render(request, 'sab/browse_addresses.html',
                  {'address_list': address_list})


@login_required
@require_POST
def compose_to_addresses(request):
    form = ComposeToForm(request.POST, request=request)
    if form.is_valid():
        to_addr = form.cleaned_data['to_addr'].encode('utf-8')
        cc_addr = form.cleaned_data['cc_addr'].encode('utf-8')
        bcc_addr = form.cleaned_data['bcc_addr'].encode('utf-8')

        if to_addr or cc_addr or bcc_addr:
            query = urllib.parse.urlencode({'to_addr': to_addr,
                                            'cc_addr': cc_addr,
                                            'bcc_addr': bcc_addr, })
            return redirect('%s?%s' % (reverse('mailapp_send_message'), query))
        else:
            return redirect('browse_addresses')
    else:
        return redirect('browse_addresses')
