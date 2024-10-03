# -*- coding: utf-8 -*-
{
    'name': 'pre_exp_test',
    'version': '1.2',
    'category': 'Accounting',
    'sequence': 35,
    'summary': 'Prepaid expense management test module',
    'website': 'https://www.odoo.com/app/purchase',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/pre_exp_test_views.xml', 
        'views/pre_exp_test_category_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}