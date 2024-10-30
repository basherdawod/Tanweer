# -*- coding: utf-8 -*-
{
    'name': 'prepaid expense',
    'version': '1.2',
    'category': 'Accounting',
    'sequence': 1,
    'summary': 'Prepaid expense management module',
    'website': 'https://www.odoo.com/app/purchase',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_job.xml',
        'views/pre_exp_test_views.xml', 
        'views/pre_exp_test_category_views.xml',
        'reports/prepaid_expense_report_template.xml',
        'reports/prepaid_expense_reports.xml',


    ],
    'assets': {
        'web.assets_backend': [
            'pre_exp_testa/static/src/js/pre_exp_test_form.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}