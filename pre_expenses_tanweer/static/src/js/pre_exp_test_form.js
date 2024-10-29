/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";

class PreExpTestFormController extends FormController {
    setup() {
        super.setup();

    }

}

export const PreExpTestFormView = {
    ...formView,
    Controller: PreExpTestFormController,
};

registry.category("views").add("pre_exp_test_form", PreExpTestFormView);