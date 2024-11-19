from odoo import api, fields, models, _, tools, Command
from odoo.exceptions import ValidationError

class FinancialAuditReporting(models.Model):
    _name = "financial.audit.customer" #model_financial_audit_customer
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Customer Registration"

    lable1 = fields.Char(
        string="Text" ,readonly=True,
        default="MODULAR CONCEPTS L.L.C.\n DUBAI - UNITED ARAB EMIRATES \n FINANCIAL STATEMENTS & REPORTS")
    name = fields.Char(
        strring="Registration No", required=False ,readonly=True,
        default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer Name")
    integration_type = fields.Selection(
        string='Integration Type',
        selection=[('current_system', 'Current Systems'),
                   ('customers_system', 'Customers Systems '), ],
        required=False, default='current_system')

    data_last_years_end = fields.Date(
        string='Registration Date',
        required=True,
    )
    audit_financial_program_ids = fields.One2many(
        comodel_name='audit.financial.program',
        inverse_name='partner_id',
        string='Customers Audit Report',
        required=False)
    api_key = fields.Char(
        strring="APT Key", required=False, copy=False)

    audit_char_account_id = fields.Many2one(
        comodel_name='audit.account.account',
        string='Char Of Account',
        required=False)
    account_lines_ss = fields.One2many(
        comodel_name='audit.account.account.line',
        inverse_name='account_ids_audit1',
        string='Account lines',
        required=False)
    account_type_level = fields.Many2one('account.type.level',string="Account Type")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('financial.audit.customer') or _('New')
        records = super(FinancialAuditReporting, self).create(vals_list)

        return records
    def create_audit_report(self):
        for record in self:
            existing_audit_reports = record.audit_financial_program_ids
            if not existing_audit_reports:
                audit_report_name = record.name
            else:
                next_letter = chr(65 + len(existing_audit_reports))  # ASCII 'A' is 65
                audit_report_name = f"{record.name}/{next_letter}"

            # Create the new audit_report record
            audit_report = self.env['audit.financial.program'].create({
                'partner_id': record.id,
                'name': audit_report_name,
            })

            # Log the creation in chatter
            record.message_post(body=f"audit_report {audit_report.name} has been created.")


class AuditAccountChar(models.Model):
    _name = 'audit.account.account' #model_audit_account_account
    _description = 'AuditAccountChar'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Account Name", required=True, index='trigram', tracking=True, translate=True)
    customer_account_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Account ',
        required=False)
    account_lines_ids = fields.One2many(
        comodel_name='audit.account.account.line',
        inverse_name='account_ids_audit',
        string='Account_lines_ids',
        required=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('audit.account.account') or _('New')
        records = super(AuditAccountChar, self).create(vals_list)
        return records


class AuditAccountCharLine(models.Model):
    _name = 'audit.account.account.line' #model_audit_account_account_line
    _description = 'audit.account.account.line'


    name = fields.Char(string="Account Name", required=True, index='trigram', tracking=True, translate=True)
    account_ids_audit = fields.Many2one(
        comodel_name='audit.account.account',
        string='Account_ids_audit',
        required=False)
    account_ids_audit1 = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Account_ids_audit',
        required=False)
    code = fields.Char(size=64, required=True, tracking=True, index=True, unaccent=False)
    account_type = fields.Selection(
        selection=[
            ("asset_receivable", "Receivable"),
            ("asset_cash", "Bank and Cash"),
            ("asset_current", "Current Assets"),
            ("asset_non_current", "Non-current Assets"),
            ("asset_prepayments", "Prepayments"),
            ("asset_fixed", "Fixed Assets"),
            ("liability_payable", "Payable"),
            ("liability_credit_card", "Credit Card"),
            ("liability_current", "Current Liabilities"),
            ("liability_non_current", "Non-current Liabilities"),
            ("equity", "Equity"),
            ("equity_unaffected", "Current Year Earnings"),
            ("income", "Income"),
            ("income_other", "Other Income"),
            ("expense", "Expenses"),
            ("expense_depreciation", "Depreciation"),
            ("expense_direct_cost", "Cost of Revenue"),
            ("off_balance", "Off-Balance Sheet"),
        ],
        string="Type", tracking=True,
        required=True,
        store=True, readonly=False, precompute=True, index=True,
        help="Account Type is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries."
    )

    opening_debit = fields.Float(string="Opening Debit" )
    opening_credit = fields.Float(string="Opening Credit"  )
    opening_balance = fields.Float(string="Opening Balance")

    current_balance = fields.Float(string="Current balance")