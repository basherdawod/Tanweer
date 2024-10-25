# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Middel Management System",
    'sequence':-1000,
    'version': "17.0.1.0.0",
    'description': "Middel East Management System",
    'summary': "Middel East Management System",
    'author': 'Tanweer LTD/Abdalkareim Bashir',
    'website': " ",
    'category': 'Services',
    'depends': ['base','account','contacts', ],
    'data': [
        # Security
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        # data
        'data/sequence_views.xml',
        'data/contract_seq.xml',
        'data/ir_cron_data.xml',
        'views/categorys.xml',
        'views/petrol_charges.xml',
        'views/brand.xml',
        'views/sub_categorys.xml',
        'views/cost_company.xml',
        'views/product.xml',
        'views/middel_quotation.xml',
        'views/middel_team_views.xml',
        'views/account_views.xml',
        'views/middel_contract.xml',
        'views/visit_card.xml',


        'views/middel_Form.xml',
        # Menus
        'views/menus.xml',
        # Report
        'report/maintenans_report_action.xml',
        'report/visit_card_report_action.xml',
        'report/maintenans_report.xml',
        'report/visit_card_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/middel_system_manegment/static/description/icon.png',
            # '/middel_system_manegment/static/src/js/toggle_active_button.js'
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
