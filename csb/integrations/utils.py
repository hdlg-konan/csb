import frappe
import connecthe


def make_payment_entry(docname):
	try:
		doc = frappe.get_doc("Payment Request", docname)
		if doc.status == 'Initiated':
			return doc.create_payment_entry(submit=True)
	except frappe.DoesNotExistError:
		pass


def update_paid_requests():
	CSB_profiles = frappe.get_list('CSB Settings', fields=['name'])

	for profile in CSB_profiles:
		doc = frappe.get_doc('CSB Settings', profile['name'])
		secret_key = doc.get_password(fieldname='secret_key', raise_exception=False)
		api = paystakk.Invoice(secret_key=secret_key, public_key=doc.public_key)
		api.list_invoices(status='success')

		if api.ctx.status:
			gen = (item for item in api.ctx.data)
			for item in gen:
				if item['metadata']:
					docname = item['metadata']['payment_request']
					make_payment_entry(docname=docname)
