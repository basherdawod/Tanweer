# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Middel East Management System",
    'version': "17.0.1.0.0",
    'description': "Middel East Management System",
    'summary': "Middel East Management System",
    'author': 'Abdalkareim Bashir',
    'website': " ",
    'category': 'Services',
    'depends': ['mail','hr_expense', 'account','contacts', 'project', 'sale_management', 'product'],
    'data': [
        # data
        'data/sequence_views.xml',
        'data/contract_seq.xml',
        'data/ir_cron_data.xml',
        # Security
        'security/groups.xml',
        'security/visitor_schedule_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        # Views
        'views/visitor_schedule_view.xml',
        'views/maintenance_view.xml',

        'views/meddil_Form.xml',
        'views/account_views.xml',
        'views/middel_team_views.xml',
        'views/team_task_views.xml',
        'views/contract_views.xml',
        'views/sale_order_views.xml',
        # Menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },

    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
