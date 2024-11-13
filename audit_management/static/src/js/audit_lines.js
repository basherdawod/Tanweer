/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class One2manySectionWidget extends Component {
    setup() {
        this.orm = useService("orm");  // Assuming you need orm service here
        this.state = useState({
            expanded: {},
            recordsWithRelations: {}, // Holds all records with fetched nested data
        });
        this.fetchAllRecordsWithRelations();
    }

    toggleSection(recordId) {
        this.state.expanded[recordId] = !this.state.expanded[recordId];
    }

    async fetchAllRecordsWithRelations() {
        const recordsWithRelations = {};
        for (const record of this.props.records) {
            const accountLevelTypes = await this.fetchRelatedRecords(record.id, "account_level_type_ids");
            recordsWithRelations[record.id] = {
                ...record,
                account_level_type_ids: accountLevelTypes,
            };
            for (const accountType of accountLevelTypes) {
                accountType.type_line_ids = await this.fetchRelatedRecords(accountType.id, "type_line_ids");
            }
        }
        this.state.recordsWithRelations = recordsWithRelations;
    }

    async fetchRelatedRecords(recordId, fieldName) {
        try {
            const record = this.props.records.find((r) => r.id === recordId);
            if (record && record[fieldName]) {
                const relatedRecords = await this.orm.read(record[fieldName], ["id", "name"]);
                return relatedRecords;
            }
            return [];
        } catch (error) {
            console.error("Error fetching related records:", error);
            return [];
        }
    }

    static template = "audit_management.One2manySectionWidgetTemplate";
}

One2manySectionWidget.props = {
    records: Array, // Expected to receive records as a prop
};

registry.category("fields").add("one2many_section_widget", One2manySectionWidget);
export default One2manySectionWidget;
