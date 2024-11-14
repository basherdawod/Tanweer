from odoo import models, fields, api , _
import io
import xlsxwriter
from odoo.http import content_disposition, request
from odoo import http
import logging
import base64
from io import BytesIO
from xlsxwriter import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

_logger = logging.getLogger(__name__)
# _logger.info("Starting _compute_account_balance")
class CorporateTax(models.Model):
    _name = 'corporate.tax'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Corporate Tax'
    
    name = fields.Char(string='Corporate Tax', readonly=True, default=lambda self: _('New'), unique=True)
    trn = fields.Char(string='TRN', related='vat_registration_id.trn', readonly=True, store=True)
    legal_name = fields.Char(string='Legal Name of Entity', related='vat_registration_id.legal_name_english', readonly=True, store=True)
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft')
    vat_registration_id = fields.Many2one('vat.registration', string='VAT Registration', required=True, domain="[('tax_type', '=', 'corporate_tax')]")

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    move_id = fields.Many2one("account.move.line", string="Account Move")
    account_id = fields.Many2one('account.account', string='Account')  
    total_debit = fields.Float(string="Total Debit")
    total_credit = fields.Float(string="Total Credit")
    total_current_balance = fields.Float(string='Total Corporate Tax')
    corporate_tax_number = fields.Char(string='Corporate Tax Number', related='vat_registration_id.company_corprate_tax', readonly=True, store=True)

    # New fields for net profit and corporate tax
    net_profit = fields.Float(string="Net Profit",compute="_compute_net_profit", store=True)
    corporate_tax = fields.Float(string="Corporate Tax", compute='_compute_corporate_tax', store=True)
    
    # Amount is still computed from account balance
    amount = fields.Float(string="Amount", compute='_compute_account_balance', store=True)

    income_total = fields.Float(string="Total Income Balance", compute='_compute_income_balance')
    income = fields.Float(string="Income",compute='_compute_income_balance')
    other_income = fields.Float(string="Other Income",compute='_compute_income_balance')
    expense = fields.Float(string="Expense",compute='_compute_income_balance')
    other_expense = fields.Float(string="Other Expense",compute='_compute_income_balance')

    current_datetime = fields.Char(string="Current Date and Time", compute="_compute_current_datetime")
    effective_reg_date = fields.Date(string='Effective Regesrtation Date', related='vat_registration_id.effective_reg_date', store=True, readonly=True)

    def _compute_current_datetime(self):
            for record in self:
                record.current_datetime = fields.Datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

    @api.depends()
    def _compute_income_balance(self):
        income_and_expense_accounts = self.env['account.account'].search([
            ('account_type', '=', 'income')
        ])

        other_income = self.env['account.account'].search([
            ('account_type', '=', 'income_other')
            ])

        expense_direct_cost_accounts = self.env['account.account'].search([
            ('account_type', '=' , 'expense_direct_cost')
            ])
        expense = self.env['account.account'].search([
            ('account_type', '=', 'expense')
            ])


        total_income_and_expense = 0.0
        other = 0.0
        total_expense_direct_cost = 0.0
        exp = 0.0
        in_total = 0.0

        for account in income_and_expense_accounts:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id)
            ])
            for line in lines:
                total_income_and_expense += line.debit - line.credit  

        for account in other_income:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id)
            ])
            for line in lines:
                other += line.debit - line.credit  

        for account in expense:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id)
            ])
            for line in lines:
                exp += line.debit - line.credit  

        for account in expense_direct_cost_accounts:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id)
            ])
            for line in lines:
                total_expense_direct_cost += line.debit - line.credit 

        
        income_total = -( total_income_and_expense + other) -  (total_expense_direct_cost + exp)

        self.income = total_income_and_expense
        self.other_income = other
        self.expense = total_expense_direct_cost
        self.other_expense = exp

        if income_total > 357000:
            self.income_total = (income_total - 357000) * 0.9
        else:
            self.income_total = 0.0


    # def action_generate_pdf_report(self):
    #     report_ref = 'uae_vat_declaration.action_corporate_tax_report_pdf'

    #     # Ensure the report reference is a string, not a list
    #     if isinstance(report_ref, list):
    #         raise ValueError("The report reference should be a string, not a list.")

    #     # Now fetch the report
    #     report = self.env.ref(report_ref)

    #     if not report:
    #         raise UserError("Report not found.")
            
    #     pdf_data = report.sudo()._render_qweb_pdf([self.id])[0]  # Generate the PDF

    #     # Continue with creating the attachment as before

    #     # Correctly reference the report action with a single string xmlid
    #     # report = self.env.ref('uae_vat_declaration.action_corporate_tax_report_pdf')  # Make sure this is correct
        
    #     # if not report:
    #     #     raise UserError("Report not found.")
        
    #     # # Generate PDF using the report action
    #     # pdf_data = report.sudo()._render_qweb_pdf([self.id])[0]  # The report action renders the PDF
        
    #     # Create an attachment for the report
    #     attachment = self.env['ir.attachment'].create({
    #         'name': 'corporate_tax_report.pdf',
    #         'type': 'binary',
    #         'datas': base64.b64encode(pdf_data),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/pdf'
    #     })
        
    #     # Return URL for downloading the report
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/web/content/{attachment.id}?download=true',
    #         'target': 'new',
    #     }

    # def action_generate_pdf_report(self):
    #     return self.env.ref('uae_vat_declaration.report_corporit_template').report_action(self)

    # def action_generate_pdf_report(self):
    #     return self.env['ir.actions.report']._get_report_from_name('uae_vat_declaration.action_corporate_tax_report_pdf').report_action(self)





    # def action_generate_excel_report(self):
    #     # Create a BytesIO buffer to hold the Excel file
    #     buffer = BytesIO()
        
    #     # Create an Excel workbook and worksheet
    #     workbook = Workbook(buffer)
    #     worksheet = workbook.add_worksheet("Report")
        
    #     # Define header row
    #     worksheet.write(0, 0, "Name")
    #     worksheet.write(0, 1, "Total Income")
    #     worksheet.write(0, 2, "TRN")
    #     worksheet.write(0, 3, "Legal Name")
    #     worksheet.write(0, 4, "VAT Registration ID")
    #     worksheet.write(0, 5, "Income")
        
    #     # Ensure the field values are correctly retrieved
        
    #     # Write Name field
    #     worksheet.write(1, 0, self.name if self.name else "N/A")  # If 'name' is None or False, use "N/A"
        
    #     # Write Total Income field
    #     worksheet.write(1, 1, self.income_total if self.income_total is not None else 0.0)  # If 'income_total' is None, use 0.0
        
    #     # Write TRN field
    #     worksheet.write(1, 2, self.trn if self.trn else "N/A")  # If 'trn' is None or False, use "N/A"
        
    #     # Write Legal Name field
    #     worksheet.write(1, 3, self.legal_name if self.legal_name else "N/A")  # If 'legal_name' is None or False, use "N/A"
        
    #     # Write VAT Registration ID
    #     if self.vat_registration_id:
    #         worksheet.write(1, 4, self.vat_registration_id.name if self.vat_registration_id.name else "N/A")  # Access related field 'name' in res.company
    #     else:
    #         worksheet.write(1, 4, "N/A")  # If 'vat_registration_id' is None, use "N/A"
        
    #     # Write Income field
    #     worksheet.write(1, 5, self.income if self.income is not None else 0.0)  # If 'income' is None, use 0.0
        
    #     # Close the workbook
    #     workbook.close()
        
    #     # Get the content of the file
    #     buffer.seek(0)
    #     file_data = buffer.read()
        
    #     # Create the attachment to download the file
    #     attachment = self.env['ir.attachment'].create({
    #         'name': "Corporate_Tax_Report.xlsx",
    #         'type': 'binary',
    #         'datas': base64.b64encode(file_data),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #     })
        
    #     # Return the attachment ID so the user can download the file (optional)
    #     return attachment
        
    #     # Return the URL to download the generated file
    #     # return {
    #     #     'type': 'ir.actions.act_url',
    #     #     'url': f'/web/content/{attachment.id}?download=true',
    #     #     'target': 'new',
    #     # }

    #     # def action_export_excel(self):
    #     #     output = io.BytesIO()
    #     #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     #     worksheet = workbook.add_worksheet('Corporate Tax')

    #     #     worksheet.write(0, 0, 'Example Data')


    #     #     workbook.close()
    #     #     output.seek(0)

    #     #     return http.send_file(output, filename="Corporate_Tax_Report.xlsx",
    #     #                           as_attachment=True, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    #     # def action_export_excel(self):
    #     #     return {
    #     #         'type': 'ir.actions.report',
    #     #         'report_name': 'uae_vat_declaration.report_corporit_template_xlsx',
    #     #         'report_type': 'xlsx',
    #     #         'data': {
                  
    #     #         }
    #     #     }



    def action_generate_excel_report(self):
        # Create a BytesIO buffer to hold the Excel file
        buffer = BytesIO()
        
        # Create an Excel workbook and worksheet
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet("Report")
        
        # Define header row
        worksheet.write(0, 0, "Name")
        worksheet.write(1, 0, "TRN")
        worksheet.write(2, 0, "Legal Name")
        worksheet.write(3, 0, "Income")
        worksheet.write(4, 0, "Other Income")
        worksheet.write(5, 0, "Expense")
        worksheet.write(6, 0, "Other Expense")
        worksheet.write(7, 0, "Total Balance")

        worksheet.write(0, 1, self.name)
        worksheet.write(1, 1, self.trn)
        worksheet.write(2, 1, self.legal_name)
        worksheet.write(3, 1, self.income)
        worksheet.write(4, 1, self.other_income)
        worksheet.write(5, 1, self.expense)
        worksheet.write(6, 1, self.other_expense)
        worksheet.write(7, 1, self.income_total)
        
        # Close the workbook
        workbook.close()
        
        # Get the content of the file
        buffer.seek(0)
        file_data = buffer.read()
        
        # Create the attachment to download the file
        attachment = self.env['ir.attachment'].create({
            'name': "Corporate Tax.xlsx",
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        # Generate the URL to download the file
        download_url = "/web/content/{}/?download=true".format(attachment.id)
        
        # Return the download URL in an action to prompt the file download
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
         
        }



    # def action_export_excel(self):
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet('Corporate Tax Report')

    #     worksheet.write(0, 0, 'name')
    #     worksheet.write(0, 1, 'status')

    #     row = 1
    #     for record in self:
    #         worksheet.write(row, 0, record.name or '')
    #         worksheet.write(row, 1, record.status or '')
    #         row += 1

    #     workbook.close()
    #     output.seek(0)
    #     response = request.make_response(
    #         output.getvalue(),
    #         headers=[
    #             ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    #             ('Content-Disposition', content_disposition('Corporate_Tax_Report.xlsx'))
    #         ]
    #     )
    #     return {
    #         'type': 'ir.actions.act_window_close',
    #     }
            
    # def _compute_net_profit(self):
    #     """
    #     Compute the net profit using raw SQL.
    #     Assumes net profit = total_debit - total_credit.
    #     """
    #     for record in self:
    #         # Use SQL to calculate net profit
    #         query = """
    #             SELECT COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) AS net_profit
    #             FROM account_account
    #         """
    #         self.env.cr.execute(query, (record.account_id.id,))
    #         result = self.env.cr.fetchone()
    #         record.net_profit = result[0] if result else 0.0

    #         _logger.info("Record ID %s, Net Profit: %s", record.id, record.net_profit)

    # def _compute_corporate_tax(self):
    #     """
    #     Compute the corporate tax as 9% of net profit using raw SQL.
    #     """
    #     for record in self:
    #         # Corporate tax = 9% of net profit
    #         record.corporate_tax = record.net_profit * 0.09

    #         _logger.info("Record ID %s, Corporate Tax: %s", record.id, record.corporate_tax)

    # def _compute_account_balance(self):
    #     """
    #     Compute account balance using SQL.
    #     """
    #     mapping = {
    #         'balance': "COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) as balance",
    #     }

    #     res = {record.id: {'balance': 0.0} for record in self}

    #     # Check if the list of account_ids is not empty
    #     account_ids = tuple(self.mapped('account_id.id'))
    #     if account_ids:  # Only run query if there are account IDs
    #         tables, where_clause, where_params = self.env['account.move.line']._query_get()
    #         tables = tables.replace('"', '') if tables else "account_move_line"

    #         filters = f" AND {where_clause.strip()}" if where_clause.strip() else ""
    #         request = (
    #             f"SELECT account_id as id, {mapping['balance']} FROM {tables} "
    #             f"WHERE account_id IN %s {filters} GROUP BY account_id"
    #         )
    #         params = (account_ids,) + tuple(where_params)

    #         _logger.info("SQL Request: %s", request)
    #         _logger.info("Params: %s", params)

    #         self.env.cr.execute(request, params)

    #         for row in self.env.cr.dictfetchall():
    #             res[row['id']] = row

    #     # Update the amount for each record
    #     for record in self:
    #         record.amount = res.get(record.id, {}).get('balance', 0.0)
    #         _logger.info("Record ID %s, Calculated Amount: %s", record.id, record.amount)







    # @api.model
    # def compute_total_current_balance(self):
    #     self.env.cr.execute("""
    #         SELECT SUM("account.account".current_balance) 
    #         FROM account_account 
    #     """)
    #     total_balance = self.env.cr.fetchone()[0] 
    #     self.total_current_balance = total_balance

    # def _sql_from_amls_two(self):
        # sql = """SELECT r.account_tax_id,
        #          COALESCE(SUM("account_move_line".debit - "account_move_line".credit), 0)
        #          FROM %s
        #          INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
        #          INNER JOIN account_tax t ON (r.account_tax_id = t.id)
        #          WHERE %s
        #          GROUP BY r.account_tax_id"""
        # return sql

    # def _compute_tax_amount(self):
    #     # Dictionary to store the calculated amount for each tax
    #     taxes = {}
    #     for line in self:
    #         taxes[line.tax_id.id] = {'amount': 0.0}

    #     # Generate SQL without date filters
    #     tables, where_clause, where_params = self.env['account.move.line']._query_get()
        
    #     # Ensure tables and where_clause are valid
    #     if not tables or not where_clause:
    #         return  # Skip calculation if no tables or where_clause are available

    #     # Amount calculation only
    #     sql = self._sql_from_amls_two()
    #     query = sql % (tables, where_clause)
        
    #     # Execute SQL query
    #     self.env.cr.execute(query, where_params)
    #     results = self.env.cr.fetchall()
        
    #     # Assign fetched results to taxes dictionary
    #     for result in results:
    #         account_tax_id, net_amount = result
    #         if account_tax_id in taxes:
    #             taxes[account_tax_id]['amount'] = abs(net_amount)

    #     # Update the amount field only
    #     for line in self:
    #         if line.tax_id.id in taxes:
    #             line.amount = taxes[line.tax_id.id]['amount']

   



    # @api.depends('revenue', 'costs', 'taxes', 'exemptions')
    # def _compute_profit(self):
    #     for record in self:
    #         # حساب الإيرادات (Revenue)
    #         revenue_lines = self.env['account.move.line'].search([
    #             ('move_id', '=', record.move_id.id),  # استخدام move_id بشكل صحيح
    #             ('account_id.user_type_id.type', '=', 'receivable'),
    #             ('move_id.invoice_payment_state', '=', 'paid'),  # أو استبدالها بالشرط المناسب
    #         ])
    #         record.revenue = sum(revenue_lines.mapped('credit'))

    #         # حساب التكاليف (Costs)
    #         cost_lines = self.env['account.move.line'].search([
    #             ('move_id', '=', record.move_id.id),  # استخدام move_id بشكل صحيح
    #             ('account_id.user_type_id.type', '=', 'payable'),
    #             ('move_id.invoice_payment_state', '=', 'paid'),
    #         ])
    #         record.costs = sum(cost_lines.mapped('debit'))

    #         # حساب الضرائب (Taxes)
    #         tax_lines = self.env['account.move.line'].search([
    #             ('move_id', '=', record.move_id.id),  # استخدام move_id بشكل صحيح
    #             ('tax_line_id', '!=', False)
    #         ])
    #         record.taxes = sum(tax_lines.mapped('tax_line_id.amount'))

    #         # حساب الربح الصافي (Net Profit)
    #         record.net_profit = record.revenue - record.costs - record.taxes + record.exemptions



    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'

    def create(self, vals_list):
        if vals_list.get('name', _('New')) == _('New'):
            sequence_code = 'corporate.tax'
            corporate_tax = self.env['ir.sequence'].next_by_code(sequence_code) or _('New')
            vals_list['name'] = f"{corporate_tax}/{fields.Date.today().strftime('%Y/%m/%d')}"
        res = super(CorporateTax, self).create(vals_list)

        return res


    # @api.depends('account_move_line_id')
    # def _compute_tax_rate(self):
    #     for record in self:
    #         record.tax_rate = record.account_move_line_id.tax_line_id.amount if record.account_move_line_id and record.account_move_line_id.tax_line_id else 0.0

    # @api.depends('account_id')
    # def _compute_taxable_income(self):
    #     for record in self:
    #         record.taxable_income = record.account_id.balance if record.account_id else 0.0

    # @api.depends('tax_rate', 'taxable_income')
    # def _compute_tax(self):
    #     for record in self:
    #         record.tax_amount = record.taxable_income * (record.tax_rate / 100)
