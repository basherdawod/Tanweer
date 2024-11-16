/** @odoo-module **/
import { Component, useState } from 'owl';
import { useStore } from 'owl.store';

export class CreateVisitComponent extends Component {
    setup() {
        this.selectedUserIds = new Set();  // Store selected user IDs
    }

    async createVisit() {
        const visitIds = await this._rpc({
            model: 'middel.east',
            method: 'action_create_visit',
            args: [Array.from(this.selectedUserIds)],  // Convert Set to Array
        });
        this.displayNotification(visitIds.length);
    }

    displayNotification(count) {
        this.trigger('display_notification', {
            title: 'Success!',
            message: `${count} visit(s) created successfully!`,
            type: 'success',
            sticky: false,
        });
    }

    toggleUserSelection(userId) {
        if (this.selectedUserIds.has(userId)) {
            this.selectedUserIds.delete(userId);
        } else {
            this.selectedUserIds.add(userId);
        }
    }
}

CreateVisitComponent.template = 'middel_system_manegment.create_visit_template';
