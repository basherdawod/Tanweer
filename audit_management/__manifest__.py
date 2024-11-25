# -*- coding: utf-8 -*-
{
    'name': 'Audit Management',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Manage and ',
    'sequence': 1,
    'website': 'https://www.odoo.com/app/purchase',
    'depends': ['base', 'account' ,'base_accounting_kit'],
    'data': [
        'security/ir.model.access.csv',
        # 'wizerd/audit_accounts_lines.xml',
        'data/sequence_views.xml',
        'data/program_line_demo.xml',
        'data/report_demo.xml',
        'data/comprehensive_income_seq.xml',
        'data/comprehensive_income_demo_data.xml',
        'views/audit_item_views.xml',
        'views/audit_program_views.xml',
        'views/program_line_views.xml',
        'views/leval_line.xml',
        'views/audit_financial_program.xml',
        'views/account_account_registration.xml',
        'views/audit_financial_registration.xml',
        'views/comprehensive_income.xml',
        'reports/program_report_template.xml',
        'reports/audit_item.xml',
        'reports/audit_financial_program_report.xml',
        'reports/account_type_level_report.xml',
        # 'reports/type_line.xml',
        'views/menu.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            # 'audit_management/static/src/js/One2manyWidget.js',
            # 'audit_management/static/src/xml/audit.xml',
            'audit_management/static/src/css/style.css',
            'audit_management/static/src/css/line.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}