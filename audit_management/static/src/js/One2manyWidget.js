/** @odoo-module **/

import { Component, useState } from "@odoo/owl";  // Import Component and useState from @odoo/owl
import { patch } from "@odoo/owl";  // Correct import for patching Odoo views

// OWL Component to render One2many data vertically
class One2manyWidget extends Component {
    // Define state for storing the One2many data
    state = useState({
        lines: [],  // Holds the lines (records) of the One2many field
    });

    // Method to set the lines (One2many data) to the widget
    setLines(lines) {
        this.state.lines = lines;  // Assign data to the widget's state
    }

    // Render a single line of the One2many data (vertical layout)
    renderLine(line) {
        return `
            <div class="line-item">
                <div><strong>Account:</strong> ${line.account || ''}</div>
                <div><strong>Balance Last:</strong> ${line.balance_last || ''}</div>
                <div><strong>Balance Credit:</strong> ${line.balance_credit || ''}</div>
                <div><strong>Balance Debit:</strong> ${line.balance_debit || ''}</div>
                <div><strong>Balance This:</strong> ${line.balance_this || ''}</div>
            </div>
        `;
    }

    // Render the entire component
    render() {
        return `
            <div class="vertical-table">
                ${this.state.lines.map(this.renderLine.bind(this)).join('')}
            </div>
        `;
    }
}

// Register the OWL component as a custom widget
export const One2manyWidgetComponent = One2manyWidget;

// Patch Odoo FormView to use the custom OWL widget for One2many field
patch('web.FormView', 'audit_management/one2many_widget', {
    start() {
        this._super(...arguments);

        // Get the One2many field container by class name
        const one2manyField = this.el.querySelector('.o_one2many');

        // Ensure the One2many field exists before proceeding
        if (one2manyField) {
            // Create an instance of the OWL component
            const widget = new One2manyWidgetComponent();

            // Get the `One2many` data from the record (adjust field name as needed)
            const one2manyData = this.record.data.account_type_ids;  // Replace `account_type_ids` with your field name

            // Set the data to the OWL component
            widget.setLines(one2manyData);

            // Attach the widget's rendered HTML to the DOM element of the One2many field
            one2manyField.innerHTML = widget.el.outerHTML;
        }
    }
});
