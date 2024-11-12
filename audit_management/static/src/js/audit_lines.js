/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

class AddAuditLineButton extends Component {
    setup() {
        this.orm = useService("orm");
        this.model = this.props.model;  // Assuming model data is passed as a prop
    }

    async addAuditLine() {
        // Add a new record to the audit_lines_ids one2many field
        await this.orm.create("audit_management.account.type.level", {
            name: "New Level Name", // default value for the new line
            account_level_type_ids: [], // Initialize empty nested field if needed
            type_line_ids: [] // Initialize another empty nested field if needed
        });

        // Refresh the view (if needed)
        await this.model.load();
    }
}

AddAuditLineButton.template = "audit_management.AddAuditLineButton";

registry.category("actions").add("add_audit_line_button", AddAuditLineButton);
