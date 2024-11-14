import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date ,timedelta
from odoo.http import content_disposition, request
import base64
import io
import xlsxwriter
from io import BytesIO
from xlsxwriter import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.tools import date_utils


class VatDeclarationLine(models.Model):
    _name = 'vat.declaration.line'
    _description = 'VAT Declaration Line'

    declaration_id = fields.Many2one('vat.declaration', string='VAT Declaration', required=True)
    line_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('none','None')
    ], string='Line Type', related="tax_id.type_tax_use")

    tax_id = fields.Many2one('account.tax', string='Tax', required=True)
    description = fields.Char(string='Description', related='tax_id.description', readonly=True)
    amount = fields.Float(string='Amount' ,compute='_compute_tax_amount',store=True, readonly=False)
    taxamount = fields.Float(string='Tax Amount', compute='_compute_tax_amount', store=True, readonly=False)
    adjustment = fields.Float(string='Adjustment',default="0.0")

    def _sql_from_amls_one(self, start_date, end_date):
        sql = """SELECT "account_move_line".tax_line_id, 
                 COALESCE(SUM("account_move_line".debit - "account_move_line".credit), 0)
                 FROM %s 
                 WHERE %s AND "account_move_line".date >= %s AND"account_move_line".date <= %s
                 GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_from_amls_two(self, start_date, end_date):
        sql = """SELECT r.account_tax_id,
                 COALESCE(SUM("account_move_line".debit - "account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s AND "account_move_line".date >= %s AND "account_move_line".date <= %s
                 GROUP BY r.account_tax_id"""
        return sql

    @api.depends('declaration_id.vat_sales_outputs.amount', 'declaration_id.vat_expenses_inputs.amount',
                 'declaration_id.vat_sales_outputs.taxamount', 'declaration_id.vat_expenses_inputs.taxamount')
    def _compute_tax_amount(self):
        # Get start_date and end_date

        start_date =self.declaration_id.date_from
        end_date = self.declaration_id.date_to

        taxes = {}
        for line in self:
            taxes[line.tax_id.id] = {'taxamount': 0.0, 'amount': 0.0}

        # Generate SQL with date filters
        tables, where_clause, where_params = self.env['account.move.line']._query_get()

        # Add start_date and end_date to where_params
        where_params += [start_date, end_date]

        # Tax amount calculation
        sql = self._sql_from_amls_one(start_date, end_date)
        query = sql % (tables, where_clause, '%s', '%s')
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            tax_line_id, tax_amount = result
            if tax_line_id in taxes:
                taxes[tax_line_id]['taxamount'] = abs(tax_amount)

        sql2 = self._sql_from_amls_two(start_date, end_date)
        query = sql2 % (tables, where_clause ,'%s', '%s')
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            account_tax_id, net_amount = result
            if account_tax_id in taxes:
                taxes[account_tax_id]['amount'] = abs(net_amount)

        # Update the amount and taxamount fields
        for line in self:
            if line.tax_id.id in taxes:
                line.amount = taxes[line.tax_id.id]['amount']
                line.taxamount = taxes[line.tax_id.id]['taxamount']


    @api.onchange('amount')
    def _onchange_amount(self):
        pass

class VatDeclaration(models.Model):
    _name = 'vat.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VAT Declaration 201'

    name = fields.Char(string='Reference', readonly=True, copy=False, default=lambda self: _('New'), unique=True)
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    vat_registration_id = fields.Many2one('vat.registration', string='VAT Registration', required=True,domain="[('tax_type', '=', 'vat')]")
    trn = fields.Char(string='TRN', related='vat_registration_id.trn', readonly=True, store=True)
    due_date = fields.Date(string='Due Date')
    legal_name = fields.Char(string='Legal Name of Entity', related='vat_registration_id.legal_name_english', readonly=True, store=True)
    signatore_id = fields.Many2one('authorised.signatory', string="Authorised Signatory")

    basic_rate_supplies_emirate = fields.Many2one(
        related='vat_registration_id.basic_rate_supplies_emirate',
        string='The supplies subject to the basic rate in',
        readonly=True
    )

    vat_sales_outputs = fields.One2many('vat.declaration.line', 'declaration_id', string='VAT Sales and Expenses')
    vat_expenses_inputs = fields.One2many('vat.declaration.line', 'declaration_id', string='VAT Expenses and Inputs')
    total_sales = fields.Float(string='Total Sales', compute='_compute_totals', store=True)
    total_sales_vat = fields.Float(string='Total Sales VAT', compute='_compute_totals', store=True)
    total_purchase = fields.Float(compute="_compute_totals", string="Total Purchase", store=True)
    total_purchase_vat = fields.Float(compute="_compute_totals", string="Total Purchase VAT", store=True)
    total_expenses = fields.Float(string='Total Expenses', compute='_compute_totals', store=True)
    total_expenses_vat = fields.Float(string='Total Expenses VAT', compute='_compute_totals', store=True)
    net_vat = fields.Float(string='Net VAT Due', compute='_compute_totals', store=True)
    effective_reg_date = fields.Date(string='Effective Regesrtation Date', related='vat_registration_id.effective_reg_date', store=True, readonly=True)

    tax_id = fields.Many2one('account.tax',string="Tax")

    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status',default='draft')

    q_dates = fields.Selection([
        ('q1', 'Q1 Date'),
        ('q2', 'Q2 Date'),
        ('q3', 'Q3 Date'),
        ('q4', 'Q4 Date')
    ], string='Quarter Dates')
    line_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('none','All')
    ], string='Line Type')

    current_datetime = fields.Char(string="Current Date and Time", compute="_compute_current_datetime")
    
    @api.depends('vat_sales_outputs')
    def _compute_totals(self):
        for record in self:

            sales_lines = record.vat_sales_outputs.filtered(lambda line: line.line_type == 'sale')
            record.total_sales = sum(sales_lines.mapped('amount'))
            record.total_sales_vat = sum(sales_lines.mapped('taxamount'))
            
            purchase_lines = record.vat_sales_outputs.filtered(lambda line: line.line_type == 'purchase')
            record.total_purchase = sum(purchase_lines.mapped('amount'))
            record.total_purchase_vat = sum(purchase_lines.mapped('taxamount'))


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'


    def _compute_current_datetime(self):
        for record in self:
            record.current_datetime = fields.Datetime.now().strftime("%A, %d %B %Y")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            sequence_code = 'vat.declaration'
            trn_sequence = self.env['ir.sequence'].next_by_code(sequence_code) or _('New')
            vals['name'] = f"{trn_sequence}/{fields.Date.today().strftime('%Y/%m/%d')}"

        record = super(VatDeclaration, self).create(vals)
        if not record.vat_sales_outputs:
            record.with_context(skip_generate_lines=True)._generate_lines()
        return record

    def write(self, vals):
        if not self.env.context.get('skip_generate_lines') and not self.vat_sales_outputs:
            self.with_context(skip_generate_lines=True)._generate_lines()
        return super(VatDeclaration, self).write(vals)


    def _generate_lines(self):
        existing_tax_ids = self.vat_sales_outputs.mapped('tax_id').ids
        vat_sales_lines = []

        for tax in self.env['account.tax'].search([]):
            if tax.id not in existing_tax_ids:
                vat_sales_lines.append((0, 0, {
                    'declaration_id': self.id,
                    'tax_id': tax.id,
                    'description': tax.description,
                    'amount': 0.0,
                    'taxamount': 0.0,
                }))

        if vat_sales_lines:
            self.with_context(skip_generate_lines=True).write({
                'vat_sales_outputs': vat_sales_lines,
            })

    @api.onchange('vat_registration_id', 'q_dates')
    def _onchange_dates(self):
        if self.vat_registration_id and self.q_dates:
            q1_date = self.vat_registration_id.vat_due_date_q1
            q2_date = self.vat_registration_id.vat_due_date_q2
            q3_date = self.vat_registration_id.vat_due_date_q3
            q4_date = self.vat_registration_id.vat_due_date_q4
            

            if self.q_dates == 'q1':
                self.date_from = q1_date 
                self.date_to = q1_date + relativedelta(months=3) 
            elif self.q_dates == 'q2':
                self.date_from = q2_date   
                self.date_to = q2_date  + relativedelta(months=3)
            elif self.q_dates == 'q3':
                self.date_from = q3_date   
                self.date_to = q3_date + relativedelta(months=3)
            elif self.q_dates == 'q4':
                self.date_from = q4_date  
                self.date_to = q4_date + relativedelta(months=3,)
            self.due_date = self.date_to - timedelta(days=2)
        else:
            self.date_from = False 
            self.date_to = False

    def action_generate_vat_excel_report(self):
        print("Name:", self.name)
        print("Date From:", self.date_from)
        print("TRN:", self.trn)
        print("Legal Name:", self.legal_name)
        buffer = io.BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet("VAT 201 Return Report")

        # Define formats for headers and currency
        bold = workbook.add_format({'bold': True})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})

        # Header section
        worksheet.write("A1", "VAT 201 Return", bold)
        worksheet.write("A2", "Ref:", bold)
        worksheet.write("B2", self.name if self.name else "N/A")  # Check for empty reference
        worksheet.write("A3", "Date:", bold)
        worksheet.write("B3", self.date_from.strftime('%Y-%m-%d') if self.date_from else "N/A")  # Format date if available
        worksheet.write("A4", "Tax Registration Number (TRN):", bold)
        worksheet.write("B4", self.trn if self.trn else "N/A")  # Check TRN
        worksheet.write("A5", "Legal Name in English:", bold)
        worksheet.write("B5", self.legal_name if self.legal_name else "N/A")  # Check legal name

        # Column headers for Supplies Section
        worksheet.write("A7", "Description", bold)
        worksheet.write("B7", "Amount (AED)", bold)
        worksheet.write("C7", "VAT Amount (AED)", bold)
        worksheet.write("D7", "Adjustment (AED)", bold)

        # Add data rows from `vat_sales_outputs`
        vat_sales_outputs = self.vat_sales_outputs
        start_row = 8
        row = start_row
        for line in vat_sales_outputs:
            worksheet.write(row, 0, line.description or "N/A")  # Provide fallback for empty description
            worksheet.write(row, 1, line.amount, currency_format)
            worksheet.write(row, 2, line.taxamount, currency_format)
            worksheet.write(row, 3, line.adjustment, currency_format)
            row += 1

        # Totals Row
        worksheet.write(row, 0, "Total", bold)
        worksheet.write_formula(row, 1, f"SUM(B{start_row}:B{row})", currency_format)
        worksheet.write_formula(row, 2, f"SUM(C{start_row}:C{row})", currency_format)
        worksheet.write_formula(row, 3, f"SUM(D{start_row}:D{row})", currency_format)

        # Footer for Net Tax Summary
        row += 2
        worksheet.write(row, 0, "Total Value of Due Tax for the Period", bold)
        worksheet.write_formula(row, 1, f"C{row-2}", currency_format)  # Use VAT Amount Total
        row += 1
        worksheet.write(row, 0, "Total Value of Recoverable Tax for the Period", bold)
        worksheet.write_formula(row, 1, f"C{start_row}:C{row-3}", currency_format)  # Sum all VAT amounts
        row += 1
        worksheet.write(row, 0, "Payable Tax for the Period", bold)
        worksheet.write_formula(row, 1, f"B{row-2}-B{row-1}", currency_format)

        # Finalize workbook and create attachment
        workbook.close()
        buffer.seek(0)
        file_data = buffer.read()

        # Attach the report
        attachment = self.env['ir.attachment'].sudo().create({
            'name': "VAT Report.xlsx",
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        # Provide a download link
        download_url = "/web/content/{}/?download=true".format(attachment.id)
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'new',
        }


    # def action_generate_vat_excel_report(self):
    #     buffer = io.BytesIO()  # Create a buffer to hold the data
    #     workbook = Workbook(buffer)  # Create a workbook with the buffer

    #     worksheet = workbook.add_worksheet("VAT 201 Return Report")

    #     # Define formats for headers and currency
    #     bold = workbook.add_format({'bold': True})
    #     currency_format = workbook.add_format({'num_format': '#,##0.00'})

    #     # Add header information to the worksheet (example)
    #     worksheet.write("A1", "VAT 201 Return", bold)
    #     worksheet.write("A2", "Ref:", bold)
    #     worksheet.write("B2", self.name if self.name else "N/A")

    #     # Add other data and calculations as needed (same as your original code)
    #     # Don't forget to loop through `vat_sales_outputs` and write the data into the worksheet

    #     workbook.close()  # Finalize the workbook
    #     buffer.seek(0)  # Go back to the start of the buffer
    #     file_data = buffer.read()  # Read the file content

    #     # Return the content as a base64 encoded file for the controller
    #     return {
    #         'file_content': base64.b64encode(file_data),
    #     }

    # def action_generate_vat_excel_report(self):
    #     # Create an in-memory buffer to store the Excel file
    #     buffer = io.BytesIO()
    #     workbook = Workbook(buffer)  # Create a new Excel workbook using xlsxwriter

    #     worksheet = workbook.add_worksheet("VAT 201 Return Report")

    #     # Define formats for headers and currency
    #     bold = workbook.add_format({'bold': True})
    #     currency_format = workbook.add_format({'num_format': '#,##0.00'})

    #     # Add header information to the worksheet
    #     worksheet.write("A1", "VAT 201 Return", bold)
    #     worksheet.write("A2", "Ref:", bold)
    #     worksheet.write("B2", self.name if self.name else "N/A")

    #     worksheet.write("A3", "Date:", bold)
    #     worksheet.write("B3", self.date_from.strftime('%Y-%m-%d') if self.date_from else "N/A")

    #     worksheet.write("A4", "Tax Registration Number (TRN):", bold)
    #     worksheet.write("B4", self.trn if self.trn else "N/A")

    #     worksheet.write("A5", "Legal Name in English:", bold)
    #     worksheet.write("B5", self.legal_name if self.legal_name else "N/A")

    #     # Column headers for Supplies Section
    #     worksheet.write("A7", "Description", bold)
    #     worksheet.write("B7", "Amount (AED)", bold)
    #     worksheet.write("C7", "VAT Amount (AED)", bold)
    #     worksheet.write("D7", "Adjustment (AED)", bold)

    #     # Add data rows from `vat_sales_outputs`
    #     vat_sales_outputs = self.vat_sales_outputs
    #     start_row = 8
    #     row = start_row
    #     for line in vat_sales_outputs:
    #         worksheet.write(row, 0, line.description or "N/A")  # Provide fallback for empty description
    #         worksheet.write(row, 1, line.amount, currency_format)
    #         worksheet.write(row, 2, line.taxamount, currency_format)
    #         worksheet.write(row, 3, line.adjustment, currency_format)
    #         row += 1

    #     # Totals Row
    #     worksheet.write(row, 0, "Total", bold)
    #     worksheet.write_formula(row, 1, f"SUM(B{start_row}:B{row})", currency_format)
    #     worksheet.write_formula(row, 2, f"SUM(C{start_row}:C{row})", currency_format)
    #     worksheet.write_formula(row, 3, f"SUM(D{start_row}:D{row})", currency_format)

    #     workbook.close()  # Finalize the workbook
    #     buffer.seek(0)  # Move the cursor to the start of the buffer
    #     file_data = buffer.read()  # Read the content of the Excel file

    #     # Return the file content as a base64 encoded string
    #     return {
    #         'file_content': base64.b64encode(file_data),  # Encode the content in base64
    #     }
