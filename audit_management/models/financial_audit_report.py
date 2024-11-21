import base64
from odoo import api, fields, models, _, tools, Command
from odoo.exceptions import AccessError, ValidationError, UserError
from datetime import datetime, date
import xlrd

class FinancialAuditReporting(models.Model):
    _name = "financial.audit.customer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Customer Registration"

    lable1 = fields.Char(
        string="Text", readonly=True,
        default="MODULAR CONCEPTS L.L.C.\n DUBAI - UNITED ARAB EMIRATES \n FINANCIAL STATEMENTS & REPORTS")
    name = fields.Char(
        string="Registration No", readonly=True,
        default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', string="Customer Name")
    integration_type = fields.Selection(
        string='Integration Type',
        selection=[('current_system', 'Current Systems'),
                   ('customers_system', 'Customers Systems')],
        required=False, default='current_system')
    data_last_years_end = fields.Date(
        string='Registration Date',
        required=True,
    )


    upload_xlsx = fields.Binary(string="Upload XLSX File")
    upload_xlsx_filename = fields.Char(string="Filename")



    data_fis_years_end = fields.Date(
        string='Fiscal Year End',
        required=False,
        default=lambda self: datetime(date.today().year, 12, 31).strftime("%Y-%m-%d")
    )
    data_last_years = fields.Date(
        string='Last Fiscal Year End',
        required=False,
        default=lambda self: datetime(date.today().year - 1, 12, 31).strftime("%Y-%m-%d")
    )
    active = fields.Boolean(
        string='Active Account',
        required=False)

    audit_financial_program_ids = fields.One2many(
        comodel_name='audit.financial.program',
        inverse_name='partner_id',
        string='Customers Audit Report',
        required=False)

    audit_char_account_id = fields.Many2one(
        comodel_name='audit.account.account',
        string='Chart Of Account',
        required=False)
    account_lines_ss = fields.One2many(
        comodel_name='audit.account.account.line',
        inverse_name='account_ids_audit1',
        string='Account lines',
        required=False)
    account_type_level = fields.Many2one('account.type.level', string="Account Type")

    
    #
    # def action_import_account_lines(self):
    #     if not self.upload_xlsx:
    #         raise ValidationError(_("Please upload an XLSX file first."))
    #
    #     try:
    #         file_content = base64.b64decode(self.upload_xlsx)
    #         workbook = xlrd.open_workbook(file_contents=file_content)
    #         sheet = workbook.sheet_by_index(0)
    #
    #         lines = []
    #         for row_idx in range(1, sheet.nrows):
    #             code = sheet.cell_value(row_idx, 0)
    #             account_type = sheet.cell_value(row_idx, 1)
    #             opening_balance = sheet.cell_value(row_idx, 2)
    #
    #             lines.append((0, 0, {
    #                 'code': code,
    #                 'account_name': account_name,
    #                 'account_balance': opening_balance,
    #
    #             }))
    #
    #         self.account_lines_ss = lines
    #
    #     except Exception as e:
    #         raise ValidationError(_("Error processing the XLSX file: %s") % str(e))


    def create_account_lines_customers(self):
        if self.integration_type == 'current_system':
            list_account = []
            for record in self :
                lines = self.env['account.account'].search([])
                for account in lines :
                    total_credit = 0.0
                    total_debit = 0.0
                    total_balance = 0.0
                    open_balance = 0.0

                    move_lines = self.env['account.move.line'].search([
                        ('account_id', '=', account.id)
                        ])
                    for mov in move_lines:
                        if record.data_last_years >= mov.date >= record.data_fis_years_end:
                            total_credit += mov.credit
                            total_debit += mov.debit
                            total_balance += mov.debit - mov.credit
                        if mov.date >= record.data_last_years :
                            open_balance += mov.debit - mov.credit
                    if record.active :
                        if total_credit or total_debit != 0.0:
                            list_account.append({
                            'code': account.code,
                            'name': account.name,
                            'account_type': account.account_type,
                            'current_balance': total_balance,
                            'opening_balance': open_balance,
                            'opening_credit': total_credit,
                            'opening_debit': total_debit,
                        })
                    else:
                        list_account.append({
                            'code': account.code,
                            'name': account.name,
                            'account_type': account.account_type,
                            'current_balance': total_balance,
                            'opening_balance': open_balance,
                            'opening_credit': total_credit,
                            'opening_debit': total_debit,
                        })
                record.write({
                    'account_lines_ss': [Command.create(vals) for vals in list_account]
                })

    def write(self, vals):
        # Check if the field to be updated is already in the vals dictionary
        if 'account_lines_ss' not in vals:  # Only modify if not already in vals
            for record in self:
                if record.integration_type != 'customers_system':  # Example condition
                    vals['account_lines_ss'] = None  # Setting the field to None
        # Call the parent method to actually update the record
        return super(FinancialAuditReporting, self).write(vals)

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
            self.env['audit.financial.program'].create({
                'partner_id': record.id,
                'name': audit_report_name,
            })



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

    opening_debit = fields.Float(string="Debit" )
    opening_credit = fields.Float(string="Credit"  )
    opening_balance = fields.Float(string="Opening Balance")

    current_balance = fields.Float(string="Current balance")

    # @api.model
    # def import_xlsx(self, file_data):
    #     try:
    #         # Read the XLSX file data
    #         wb = xlrd.open_workbook(file_contents=file_data)
    #         sheet = wb.sheet_by_index(0)

    #         for row_num in range(1, sheet.nrows):  # Skip the header
    #             parent_name = sheet.cell(row_num, 0).value
    #             field_1 = sheet.cell(row_num, 1).value
    #             field_2 = sheet.cell(row_num, 2).value

    #             # Create or get the parent record
    #             parent = self.search([('name', '=', parent_name)], limit=1)
    #             if not parent:
    #                 parent = self.create({'name': parent_name})

    #             # Create the line record
    #             self.env['your.line.model'].create({
    #                 'parent_id': parent.id,
    #                 'field_1': field_1,
    #                 'field_2': field_2,
    #             })
    #     except Exception as e:
    #         raise ValidationError(f"Error importing XLSX: {str(e)}")