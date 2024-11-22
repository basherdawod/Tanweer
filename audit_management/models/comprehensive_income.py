import openpyxl
import io
import base64
from odoo import api, fields, models, _, tools, Command
from odoo.exceptions import AccessError, ValidationError, UserError
from datetime import datetime, date



class ComprehensiveIncome(models.Model):
    _name = 'comprehensive.income' #model_comprehensive_income
    _description = 'Comprehensive Income'

    name = fields.Char(
        string="Registration No", readonly=True,
        default=lambda self: _('New'), copy=False)

    registration_date = fields.Date(
        string='Registration Date',
        required=True,
    )
    #
    # data_fis_years_end = fields.Date(
    #     string='Fiscal Year End',
    #     required=False,
    #     default=lambda self: datetime(date.today().year, 12, 31).strftime("%Y-%m-%d")
    # )
    # data_last_years = fields.Date(
    #     string='Last Fiscal Year End',
    #     required=False,
    #     default=lambda self: datetime(date.today().year - 1, 12, 31).strftime("%Y-%m-%d")
    # )
    # partner_id = fields.Many2one('res.partner', string="Customer Name")
    # integration_type = fields.Selection(
    #     string='Integration Type',
    #     selection=[('current_system', 'Current Systems'),
    #                ('customers_system', 'Customers Systems')],
    #     required=False, default='current_system')
    # active_account = fields.Boolean(
    #     string='Active Account',
    #     required=False)
    # audit_char_account_id = fields.Many2one(
    #     comodel_name='audit.account.account',
    #     string='Chart Of Account',
    #     required=False)
    # upload_xlsx = fields.Binary(string="Upload XLSX File")
    # upload_xlsx_filename = fields.Char(string="Filename")

    comprehensive_income_line_ids = fields.One2many('comprehensive.income.line','comprehensive_income_id',string="Comprehensive Income Line")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('comprehensive.income') or _('New')
        res = super(ComprehensiveIncome, self).create(vals_list)
        return res

    def action_import_account_lines(self):
        if not self.upload_xlsx:
            raise ValidationError(_("Please upload an XLSX file first."))

        if not self.upload_xlsx_filename or not self.upload_xlsx_filename.endswith('.xlsx'):
            raise ValidationError(
                _("The uploaded file is not a valid XLSX file. Please upload a file with the '.xlsx' extension."))

        try:
            # Decode the uploaded file
            file_content = base64.b64decode(self.upload_xlsx)
            file = io.BytesIO(file_content)

            # Try to load the workbook
            workbook = openpyxl.load_workbook(filename=file)
            sheet = workbook.active

            # Initialize an empty list for lines
            lines = []

            # Process the rows, assuming row 1 contains headers
            for row_idx in range(2, sheet.max_row + 1):
                code = sheet.cell(row=row_idx, column=1).value
                account_name = sheet.cell(row=row_idx, column=2).value
                total_last_year = sheet.cell(row=row_idx, column=3).value or 0
                total_this_year = sheet.cell(row=row_idx, column=4).value or 0

                # Validate required fields
                if not code or not account_name:
                    raise ValidationError(
                        _("Row %d: 'Code' and 'Account Name' are required.") % row_idx
                    )

                # Add the line data
                lines.append((0, 0, {
                    'code':code,
                    'account_name': account_name,
                    'total_last_year': total_last_year,
                    'total_this_year': total_this_year,
                }))

            # Assign the lines to the One2many field
            self.comprehensive_income_line_ids = lines

        except Exception as e:
            raise ValidationError(_("Error processing the XLSX file: %s") % str(e))

    def create_account_lines_customers(self):
        if self.integration_type == 'current_system':
            list_account = []

            # Get all accounts
            accounts = self.env['account.account'].search([])

            # Loop through all the records (self) -- assuming self represents multiple records
            for record in self:
                total_last_year = 0.0
                total_this_year = 0.0

                fiscal_year_start = record.data_last_years
                fiscal_year_end = record.data_fis_years_end

                # Get the start and end of last year
                last_year_start = datetime(datetime.today().year - 1, 1, 1).date()
                last_year_end = datetime(datetime.today().year - 1, 12, 31).date()

                # Fetch all move lines for the accounts
                move_lines = self.env['account.move.line'].search([
                    ('account_id', 'in', [account.id for account in accounts]),
                ])

                for account in accounts:
                    account_total_last_year = 0.0
                    account_total_this_year = 0.0

                    for move in move_lines.filtered(lambda m: m.account_id == account):
                        if fiscal_year_start <= move.date <= fiscal_year_end:
                            account_total_this_year += move.debit - move.credit

                        if last_year_start <= move.date <= last_year_end:
                            account_total_last_year += move.debit - move.credit

                    list_account.append({
                        'account_name': account.name,
                        'total_last_year': account_total_last_year,
                        'total_this_year': account_total_this_year,
                    })

                record.write({
                    'comprehensive_income_line_ids': [(0, 0, vals) for vals in list_account]
                })

    from datetime import datetime

    def create_account_lines_customers(self):
        if self.integration_type == 'current_system':
            list_account = []

            # Get only active accounts if the field active_account is True
            if self.active_account:
                accounts = self.env['account.account'].search([])
            else:
                # Get all accounts if active_account is False or not set
                accounts = self.env['account.account'].search([])

            # Loop through all the records (self) -- assuming self represents multiple records
            for record in self:
                total_last_year = 0.0
                total_this_year = 0.0

                fiscal_year_start = record.data_last_years
                fiscal_year_end = record.data_fis_years_end

                # Get the start and end of last year
                last_year_start = datetime(datetime.today().year - 1, 1, 1).date()
                last_year_end = datetime(datetime.today().year - 1, 12, 31).date()

                # Fetch all move lines for the selected accounts
                move_lines = self.env['account.move.line'].search([
                    ('account_id', 'in', [account.id for account in accounts]),
                ])

                for account in accounts:
                    account_total_last_year = 0.0
                    account_total_this_year = 0.0

                    # Filter move lines for the current account
                    for move in move_lines.filtered(lambda m: m.account_id == account):
                        # If the move is within the current fiscal year range
                        if fiscal_year_start <= move.date <= fiscal_year_end:
                            account_total_this_year += move.debit - move.credit

                        # If the move is within last year's fiscal range
                        if last_year_start <= move.date <= last_year_end:
                            account_total_last_year += move.debit - move.credit

                    # Add the account totals to the list, based on the active account condition
                    if record.active_account:
                        # Only add to list if there is some credit or debit for active accounts
                        if account_total_this_year or account_total_last_year:
                            list_account.append({
                                'account_name': account.name,
                                'total_last_year': account_total_last_year,
                                'total_this_year': account_total_this_year,
                            })
                    else:
                        # Add to list for all accounts regardless of whether they are active or not
                        list_account.append({
                            'account_name': account.name,
                            'total_last_year': account_total_last_year,
                            'total_this_year': account_total_this_year,
                        })

                # Write the account lines to the comprehensive income model
                record.write({
                    'comprehensive_income_line_ids': [(0, 0, vals) for vals in list_account]
                })


class ComprehensiveIncomeLine(models.Model):
    _name = 'comprehensive.income.line' #model_comprehensive_income_line
    _description = 'Comprehensive Income Line'

    code = fields.Char(string="Code")
    account_name = fields.Char(string="Account Name")
    total_last_year = fields.Float(string="Total Last Year")
    total_this_year = fields.Float(string="Total This Year")
    comprehensive_income_id = fields.Many2one('comprehensive.income','comprehensive_income_line_ids')
