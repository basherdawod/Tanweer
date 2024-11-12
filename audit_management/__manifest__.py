# -*- coding: utf-8 -*-
{
    'name': 'Audit Management',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Manage and ',
    'sequence': 1,
    'website': 'https://www.odoo.com/app/purchase',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_views.xml',
        'data/program_line_demo.xml',
        'views/audit_item_views.xml',
        'views/audit_program_views.xml',
        'views/program_line_views.xml',
        'views/audit_financial_program.xml',
        'views/menu.xml',
        'reports/program_report_template.xml',
        'reports/audit_item.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'audit_management/static/src/js/audit_lines.js',
            'audit_management/static/src/xml/audit.xml',
            'audit_management/static/src/css/style.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}