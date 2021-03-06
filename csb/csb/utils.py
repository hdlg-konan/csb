import frappe
import csb
import json,datetime
from urllib.parse import parse_qs
from frappe.utils import get_request_session
from frappe import _


def make_payment_entry(docname):
	try:
		doc = frappe.get_doc("Payment Request", docname)
		if doc.status == 'Initiated':
			return doc.create_payment_entry(submit=True)
	except frappe.DoesNotExistError:
		pass


def update_paid_requests():
	paystack_profiles = frappe.get_list('CSB Settings', fields=['name'])

	for profile in csb_profiles:
		doc = frappe.get_doc('CSB Settings', profile['name'])
		secret_key = doc.get_password(fieldname='secret_key', raise_exception=False)
		api = csb.Invoice(secret_key=secret_key, public_key=doc.public_key)
		api.list_invoices(status='success')

		if api.ctx.status:
			gen = (item for item in api.ctx.data)
			for item in gen:
				if item['metadata']:
					docname = item['metadata']['payment_request']
					make_payment_entry(docname=docname)

def make_request(method, url, auth=None, headers=None, data=None):
	auth = auth or ''
	data = data or {}
	headers = headers or {}

	try:
		s = get_request_session()
		frappe.flags.integration_request = s.request(method, url, data=data, auth=auth, headers=headers)
		frappe.flags.integration_request.raise_for_status()

		if frappe.flags.integration_request.headers.get("content-type") == "text/plain; charset=utf-8":
			return parse_qs(frappe.flags.integration_request.text)

		return frappe.flags.integration_request.json()
	except Exception as exc:
		frappe.log_error()
		raise exc

def make_get_request(url, **kwargs):
	return make_request('GET', url, **kwargs)

def make_post_request(url, **kwargs):
	return make_request('POST', url, **kwargs)

def make_put_request(url, **kwargs):
	return make_request('PUT', url, **kwargs)

@frappe.whitelist(allow_guest=True, xss_safe=True)
def get_checkout_url(**kwargs):
	try:
		if kwargs.get('payment_gateway'):
			doc = frappe.get_doc("{0} Settings".format(kwargs.get('payment_gateway')))
			return doc.get_payment_url(**kwargs)
		else:
			raise Exception
	except Exception:
		frappe.respond_as_web_page(_("Something went wrong"),
			_("Looks like something is wrong with this site's payment gateway configuration. No payment has been made."),
			indicator_color='red',
			http_status_code=frappe.ValidationError.http_status_code)

def create_payment_gateway(gateway, settings=None, controller=None):
	# NOTE: we don't translate Payment Gateway name because it is an internal doctype
	if not frappe.db.exists("Payment Gateway", gateway):
		payment_gateway = frappe.get_doc({
			"doctype": "Payment Gateway",
			"gateway": gateway,
			"gateway_settings": settings,
			"gateway_controller": controller
		})
		payment_gateway.insert(ignore_permissions=True)

def json_handler(obj):
	if isinstance(obj, (datetime.date, datetime.timedelta, datetime.datetime)):
		return str(obj)
