# -*- coding: utf-8 -*-
# Copyright (c) 2018, XLevel Retail Systems Nigeria Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import csb
import requests
import base64
import json
from frappe import _
from frappe.integrations.utils import  (make_get_request, make_post_request, create_request_log,
	create_payment_gateway)
from frappe.model.document import Document
from frappe.utils import call_hook_method, nowdate,get_url, cint, get_timestamp
from requests import RequestException, ConnectionError
from requests.auth import HTTPBasicAuth

SUPPORTED_CURRENCIES = ['XPF']


class CSBSettings(Document):
	supported_currencies = SUPPORTED_CURRENCIES

	def validate(self):
		create_payment_gateway('CSB')
		call_hook_method('payment_gateway_enabled', gateway='CSB')

	def on_update(self):
		name = 'CSB-{0}'.format(self.gateway_name)
		create_payment_gateway(
			name,
			settings='CSB Settings',
			controller=self.gateway_name
		)
		call_hook_method('payment_gateway_enabled', gateway=name)

	def validate_credentials(self):
		try:
			secret = self.get_password(fieldname='secret_key', raise_exception=False)
			base64string = base64.encodebytes(('%s:%s' % (self.public_key, secret)).encode('utf8')).replace(b'\n', b'')
			api_url = "https://epaync.nc/api-payment/V4/Charge/CreatePayment"
			headers = {'Authorization': 'Basic MTU1NzgwNTM6dGVzdHBhc3N3b3JkX3JCU3lrWXBxNkRMYW1GQVNXS1dGdUZtdlR6MU5lUkRiZ2ROT2ZkTnEwN2UxaA==', 'Content-Type': "application/json"}  
			response = requests.request("GET",api_url, headers=headers)

		except ConnectionError:
			frappe.throw('There was a connection problem. Please ensure that'
						 ' you have a working internet connection.')

		if not api.ctx.status:
			frappe.throw(api.ctx.message, title=_("Failed Credentials Validation"))

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(
				_('{currency} is not supported by CSB at the moment.').format(currency))

	def get_payment_url(self, currency, **kwargs):
		amount = kwargs.get('amount')
		description = kwargs.get('description')
		slug = kwargs.get('reference_docname')
		email = kwargs.get('payer_email')
		order_id = kwargs.get('order_id')
		customer_name = kwargs.get('payer_name')
						
		
		secret = self.get_password(fieldname='secret_key', raise_exception=False)
		base64string = base64.encodebytes(('%s:%s' % (self.public_key, secret)).encode('utf8')).replace(b'\n', b'')
		api_url = "https://epaync.nc/api-payment/V4/Charge/CreatePayment"
		headers = {'Authorization': 'Basic MTU1NzgwNTM6dGVzdHBhc3N3b3JkX3JCU3lrWXBxNkRMYW1GQVNXS1dGdUZtdlR6MU5lUkRiZ2ROT2ZkTnEwN2UxaA==', 'Content-Type': "application/json"}  

		payment_options = {
			"amount": amount,
			"currency": currency,
			"orderId": order_id,
			"customer": {
				"email": email
			}
		}
		order = requests.post(api_url,headers=headers,json=payment_options)
		frappe.throw(_("JSON: {0}".format(order.json()))

