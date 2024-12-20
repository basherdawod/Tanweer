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
        'views/product_product.xml',
        'report/report_quotiation.xml',
        'report/inhiret_external_layout.xml',
        'views/middel_contract.xml',
        'views/visit_card.xml',
        'views/res_partner_views.xml',
        'report/maintenans_report_action.xml',
        'report/maintenans_report.xml',
        'report/report_estmatin.xml',
        'report/report_visiteor_form.xml',

        # Report
        'report/maintenans_report_action.xml',
        'report/visit_card_report_action.xml',
        'report/maintenans_report.xml',
        'report/visit_card_report.xml',
        # 'report/invoice_report_action.xml',
        'report/invoice_report.xml',



        'views/middel_Form.xml',
        # Menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'middel_system_manegment/static/description/icon.png',
            'middel_system_manegment/static/src/js/binary_attachment_preview.js'
            'middel_system_manegment/static/src/js/templates.xml'

        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
