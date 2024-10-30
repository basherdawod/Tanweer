/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { rpc } from "@web/core/rpc";

class PettyCashDashboard extends Component {
    static template = "petty_cash_manager.PettyCashDashboardTemplate";

    setup() {
        this.transactions = useState({ data: [] });

        onMounted(async () => {
            this.transactions.data = await this._fetchTransactions();
        });
    }

    async _fetchTransactions() {
        try {
            const result = await rpc({
                model: "petty.cash.request",
                method: "search_read",
                args: [[], ["name", "date", "request_amount", "state"]],
            });
            return result;
        } catch (error) {
            console.error("Failed to fetch transactions:", error);
            return [];
        }
    }
}

registry.category("actions").add("petty_cash_dashboard", PettyCashDashboard);
