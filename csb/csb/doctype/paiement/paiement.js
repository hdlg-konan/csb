frappe.provide("erpnext.utils");

frappe.ui.form.on('Paiement', {
	refresh: function(frm) {
		if (!cur_frm.doc.__islocal) {
			$(frm.fields_dict['drivers'].wrapper)
				.html(frappe.render_template("transaction_list", cur_frm.doc.__onload));
		}
	}
});

