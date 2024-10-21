/** In your custom module's static/src/js/toggle_active_button.js **/

import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";

class ToggleActiveTreeViewController extends ListController {
    // Overriding the setup to handle active state toggle
    setup() {
        super.setup();
    }

    // Method that toggles the button label dynamically
    async toggleActive(recordId) {
        const record = this.model.get(recordId);
        const newActiveStatus = !record.data.active;

        // Call the server-side method to update the active field
        await this.rpc({
            model: 'middel.petrol.charges',
            method: 'toggle_active',
            args: [[recordId]],
        });

        // Refresh the view to reflect the new status
        this.reload();
    }

    // Override the button click handler to call the toggleActive method
    async onButtonClick(event) {
        const recordId = event.currentTarget.closest('tr').dataset.recordId;
        await this.toggleActive(recordId);
    }
}

// Register the controller so it's used for this tree view
registry.category("controllers").add("toggleActiveTreeView", ToggleActiveTreeViewController);
