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
from datetime import datetime

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
        # Get the current year
        current_year = datetime.today().year
        start_date = f'{current_year}-01-01'
        end_date = f'{current_year}-12-31' 

        # Search for accounts of different types
        income_and_expense_accounts = self.env['account.account'].search([
            ('account_type', '=', 'income')
        ])

        other_income = self.env['account.account'].search([
            ('account_type', '=', 'income_other')
        ])

        expense_direct_cost_accounts = self.env['account.account'].search([
            ('account_type', '=', 'expense_direct_cost')
        ])
        
        expense = self.env['account.account'].search([
            ('account_type', '=', 'expense')
        ])

        # Initialize totals
        total_income_and_expense = 0.0
        other = 0.0
        total_expense_direct_cost = 0.0
        exp = 0.0
        in_total = 0.0

        # Calculate total income and expense for income accounts
        for account in income_and_expense_accounts:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id),
                ('date', '>=', start_date),  # Filter by start date
                ('date', '<=', end_date)     # Filter by end date
            ])
            for line in lines:
                total_income_and_expense += line.debit - line.credit  

        # Calculate other income
        for account in other_income:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id),
                ('date', '>=', start_date),  # Filter by start date
                ('date', '<=', end_date)     # Filter by end date
            ])
            for line in lines:
                other += line.debit - line.credit  

        # Calculate total expenses
        for account in expense:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id),
                ('date', '>=', start_date),  # Filter by start date
                ('date', '<=', end_date)     # Filter by end date
            ])
            for line in lines:
                exp += line.debit - line.credit  

        # Calculate total direct costs
        for account in expense_direct_cost_accounts:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id),
                ('date', '>=', start_date),  # Filter by start date
                ('date', '<=', end_date)     # Filter by end date
            ])
            for line in lines:
                total_expense_direct_cost += line.debit - line.credit 

        # Calculate income total
        income_total = -(total_income_and_expense + other) - (total_expense_direct_cost + exp)

        # Assign calculated values to fields
        self.income = total_income_and_expense
        self.other_income = other
        self.expense = total_expense_direct_cost
        self.other_expense = exp

        # Income total logic
        if income_total > 357000:
            self.income_total = (income_total - 357000) * 0.9
        else:
            self.income_total = 0.0


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

