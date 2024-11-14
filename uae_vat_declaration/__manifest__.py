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
    'depends': ['base', 'account','l10n_ae','report_xlsx'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/vat_declaration_sequence.xml',
        'data/vat_registration_sequence.xml',
        'data/corporate_tax_sequance.xml',
        'data/cron_job.xml',   
        'views/vat_declaration_views.xml',
        'views/vat_registration_views.xml',
        'views/authorised_signatory.xml',
        'views/corporate_tax.xml',
        'views/res_company.xml',
        'report/vat_report_action.xml',
        'report/vat_report.xml',
        'report/corporit_tax_action.xml',
        'report/corporit_tax_report.xml',
        'report/vat_report_action.xml',
        'report/vat_report.xml',

        'data/tax_lines.xml',
        
        
    ],
    'demo': [
        'demo/vat_declaration_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    # 'post_init_hook': 'create_demo_data',
}