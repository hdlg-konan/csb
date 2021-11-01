# -*- coding: utf-8 -*-
# Copyright (c) 2018, XLevel Retail Systems Nigeria Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import csb
import requests
import base64
from frappe import _
from frappe.integrations.utils import create_payment_gateway
from frappe.model.document import Document
from frappe.utils import call_hook_method, nowdate
from requests import RequestException, ConnectionError

SUPPORTED_CURRENCIES = ['XAF']


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
			base64string = base64.encodebytes(('%s:%s' % (self.public_key, self.secret_key)).encode('utf8')).decode('utf8').replace('\n', '')
			headers = ("Authorization: Basic %s" % base64string)
			api_url = "https://epaync.nc/api-payment/V4/Charge/SDKTest"
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

	def get_payment_url(self, **kwargs):
		amount = kwargs.get('amount')
		currency = kwargs.get ('currency')
		description = kwargs.get('description')
		slug = kwargs.get('reference_docname')
		email = kwargs.get('payer_email')
		metadata = {
			'order_id': kwargs.get('order_id'),
			'customer_name': kwargs.get('payer_name')
		}
		
		

		secret_key = self.get_password(fieldname='secret_key', raise_exception=False)
		base64string = base64.encodebytes(('%s:%s' % (self.public_key, self.secret_key)).encode('utf8')).decode('utf8').replace('\n', '')
		headers = {"Authorization: Basic %s" % base64string}
		api_url = "https://epaync.nc/api-payment/V4/Charge/SDKTest"

		payment_options = {
			"amount": kwargs.get('amount'),
			"currency": kwargs.get('currency'),
			"order_id": kwargs.get('order_id'),
		}
		order = requests.post(api_url,headers=headers)
		if order.post("status") != "SUCCESS":
			frappe.throw(api.ctx.message, title=_("Ca fonctionne"))
		else:
			error = order.post("status")
			frappe.throw(api.ctx.message, title=_(error))
		


