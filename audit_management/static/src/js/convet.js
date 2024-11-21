/** @odoo-module **/

import { One2manyWidgetComponent } from './one2many_widget_component';  // Import the OWL component

import { patch } from 'web.utils';  // Import patching functionality to modify the Odoo FormView

patch('web.FormView', 'audit_management/one2many_widget', {
    start() {
        this._super(...arguments);

        // Find the One2many field by its class
        const one2manyField = this.el.querySelector('.o_one2many');

        if (one2manyField) {
            // Create a new instance of the OWL component
            const widget = new One2manyWidgetComponent();

            // Pass the One2many data (lines) to the OWL component
            widget.setLines(this.record.data.account_type_ids);  // Adjust field name as necessary

            // Attach the OWL widget to the DOM of the One2many field
            one2manyField.innerHTML = widget.el.outerHTML;  // Insert the OWL component's HTML
        }
    }
});
