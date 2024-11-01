{
    'name': 'UAE VAT Declaration',
    'version': '1.2',
    'sequence': -10000,
    'category': 'Accounting',
    'summary': 'Manage VAT Declarations for UAE',
    'description': """
This module allows you to manage and file VAT Declarations for the UAE.
It includes:
- VAT Declaration form
- Calculation of VAT on sales and expenses
- Summary of VAT due
    """,
    'depends': ['base', 'account'],
    'data': [
        'data/vat_declaration_sequence.xml',
        'data/vat_registration_sequence.xml',
        'data/cron_job.xml',
        # 'data/demo_data.xml',
        'views/vat_declaration_views.xml',
        'views/vat_registration_views.xml',
        'views/authorised_signatory.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/vat_report_action.xml',
        'report/vat_report.xml',
        
    ],
    'demo': [
        'demo/vat_declaration_demo.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}