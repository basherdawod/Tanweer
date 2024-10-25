# -*- coding: utf-8 -*-
###############################################################################
#
# Aspire Softserv Pvt. Ltd.
# Copyright (C) Aspire Softserv Pvt. Ltd.(<https://aspiresoftserv.com>).
#
###############################################################################
{
    'name': 'Petty Cash Manager',
    'version': '17.0',
    'category': 'Accounting',
    'summary': 'Manage petty cash requests, approvals, and accounting',
    'depends': ['base', 'account', 'hr'],  # Include any required modules
    'data': [
        'data/sequence_views.xml',
        'security/ir.model.access.csv',
        # 'security/rules.xml',
        'views/petty_cash_views.xml',
        'views/petty_card_form.xml',
        'views/payment.xml',
        'views/submited.xml',
        'views/petty_cach_request_form.xml',
        # 'views/pety_cash.xml',
        'report/pety_cash_template.xml',
    ],
    "application": True,
    "installable": True,
}
