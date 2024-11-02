import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date ,timedelta

class VatDeclarationLine(models.Model):
    _name = 'vat.declaration.line'
    _description = 'VAT Declaration Line'

    declaration_id = fields.Many2one('vat.declaration', string='VAT Declaration')
    description = fields.Text(string='Description')
    amount = fields.Float(string='Amount')
    vat_amount = fields.Float(string='VAT Amount')
    line_type = fields.Selection([('sales', 'Sales'), ('expenses', 'Expenses')], string='Line Type')
    

class VatDeclaration(models.Model):
    _name = 'vat.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VAT Declaration 201'

    name = fields.Char(string='Reference', readonly=True, default='New')
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    vat_registration_id = fields.Many2one('vat.registration', string='VAT Registration', required=True)
    trn = fields.Char(string='TRN', related='vat_registration_id.company_vat', readonly=True, store=True)
    due_date = fields.Date(string='Due Date',related='vat_registration_id.corporate_tax_due_date', readonly=True, store=True)
    legal_name = fields.Char(string='Legal Name of Entity', related='vat_registration_id.legal_name_english', readonly=True, store=True)

    basic_rate_supplies_emirate = fields.Selection(
        related='vat_registration_id.basic_rate_supplies_emirate',
        string='The supplies subject to the basic rate in',
        readonly=True
    )

    vat_sales_outputs = fields.One2many('vat.declaration.line', 'declaration_id', string='VAT Sales and Outputs', domain=[('line_type', '=', 'sales')])
    vat_expenses_inputs = fields.One2many('vat.declaration.line', 'declaration_id', string='VAT Expenses and Inputs', domain=[('line_type', '=', 'expenses')])

    total_sales = fields.Float(string='Total Sales', compute='_compute_totals', store=True)
    total_sales_vat = fields.Float(string='Total Sales VAT', compute='_compute_totals', store=True)
    total_expenses = fields.Float(string='Total Expenses', compute='_compute_totals', store=True)
    total_expenses_vat = fields.Float(string='Total Expenses VAT', compute='_compute_totals', store=True)
    net_vat = fields.Float(string='Net VAT Due', compute='_compute_totals', store=True)
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status',default='draft')
    signatore_id = fields.Many2one('authorised.signatory', string="Authorised Signatory")

    tax_id = fields.Many2one('account.tax',string="Tax")
    account_id = fields.Many2one('account.account',string="Account")

    recoverable_tax = fields.Boolean(string="Do you Wish to Request a Refund for the Above Amount of Exesst Recoverable Tax")
    during_tax = fields.Boolean(string="Did you Apply the Profit Margin Scheme in Respect of Any Supplies Made During The Tax Period")

    q_dates = fields.Selection([
        ('q1', 'Q1 Date'),
        ('q2', 'Q2 Date'),
        ('q3', 'Q3 Date'),
        ('q4', 'Q4 Date')
    ], string='Quarter Dates')

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


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'

    @api.depends('vat_sales_outputs', 'vat_expenses_inputs')
    def _compute_totals(self):
        for record in self:
            record.total_sales = sum(record.vat_sales_outputs.mapped('amount'))
            record.total_sales_vat = sum(record.vat_sales_outputs.mapped('vat_amount'))
            record.total_expenses = sum(record.vat_expenses_inputs.mapped('amount'))
            record.total_expenses_vat = sum(record.vat_expenses_inputs.mapped('vat_amount'))
            record.net_vat = record.total_sales_vat - record.total_expenses_vat

    @api.onchange('vat_registration_id', 'basic_rate_supplies_emirate', 'date_from', 'date_to')
    def _onchange_vat_registration_emirate(self):
        self.ensure_one()
        if self.vat_registration_id and self.basic_rate_supplies_emirate:
            # Get the selection from the original field in VatRegistration model
            emirate_selection = self.env['vat.registration']._fields['basic_rate_supplies_emirate'].selection
            emirate_dict = dict(emirate_selection)
            emirate_name = emirate_dict.get(self.basic_rate_supplies_emirate, '')
            
            # Create or update the sales output line
            sales_line = self.vat_sales_outputs.filtered(lambda l: l.line_type == 'sales')
            if not sales_line:
                sales_line = self.env['vat.declaration.line'].create({
                    'declaration_id': self.id,
                    'line_type': 'sales',
                })
                self.vat_sales_outputs = [(4, sales_line.id)]
            
            sales_line.write({
                'description': f"""
                 Emirate: {emirate_name}
                 Country ID: {self.tax_id.country_id.id}
                """
            })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vat.declaration') or 'New'
        record = super(VatDeclaration, self).create(vals)
        record._onchange_vat_registration_emirate()
        return record

    def write(self, vals):
        result = super(VatDeclaration, self).write(vals)
        self._onchange_vat_registration_emirate()
        return result