# -*- coding: utf-8 -*-

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

from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('user', 'imap_server', 'ab_type')


class ComposeToForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ComposeToForm, self).__init__(*args, **kwargs)

        address_list = Address.objects.for_request(request)
        choices = [(address.id, address.id) for address in address_list]
        self.choices = choices
        self.fields['to_addr'].choices = choices
        self.fields['cc_addr'].choices = choices
        self.fields['bcc_addr'].choices = choices

    def clean(self):
        for key in self.cleaned_data.keys():
            self.cleaned_data[key] = ','.join(
                [Address.objects.get(id=int(item)).mail_addr()
                    for item in self.cleaned_data[key]]
                )
        return self.cleaned_data

    to_addr = forms.MultipleChoiceField(required=False)
    cc_addr = forms.MultipleChoiceField(required=False)
    bcc_addr = forms.MultipleChoiceField(required=False,
                                         widget=forms.CheckboxSelectMultiple)
