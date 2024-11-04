import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date ,timedelta

class VatDeclarationLine(models.Model):
    _name = 'vat.declaration.line'
    _description = 'VAT Declaration Line'

    declaration_id = fields.Many2one('vat.declaration', string='VAT Declaration', required=True)
    line_type = fields.Selection([
        ('sales', 'Sales'),
        ('expenses', 'Expenses')
    ], string='Line Type', required=True)

    tax_id = fields.Many2one('account.tax', string='Tax', required=True)
    description = fields.Char(string='Description', related='tax_id.description', readonly=True)
    amount = fields.Float(string='Amount' ,compute='_compute_tax_amount',store=True)
    taxamount = fields.Float(string='Tax Amount', compute='_compute_tax_amount', store=True) 

    @api.depends('declaration_id.vat_sales_outputs.amount', 'declaration_id.vat_expenses_inputs.amount',
                 'declaration_id.vat_sales_outputs.taxamount', 'declaration_id.vat_expenses_inputs.taxamount')
    def _compute_tax_amount(self):
        for line in self:
            line.amount = 0.0
            line.taxamount = 0.0

            if line.line_type == 'sales':
                # Search for tax lines related to sales
                tax_lines = self.env['account.move.line'].search([
                    ('tax_ids', 'in', line.tax_id.ids),
                    ('move_type', '=', 'out_invoice'),
                ])
                # Get a list of all 'ref' values from tax_lines
                refs = tax_lines.mapped('ref')

                # Use the refs list to find additional lines
                tax_line = self.env['account.move.line'].search([
                    ('ref', 'in', refs),
                    ('move_type', '=', 'out_invoice'),
                ])
                line.amount = sum(tax_line.mapped('credit')[0] if tax_line else 0.0)

                # line.amount = tax_line.mapped('credit') 
                line.taxamount = sum(tax_lines.mapped('credit'))

            elif line.line_type == 'expenses':
                # Search for tax lines related to expenses
                tax_lines = self.env['account.move.line'].search([
                    ('tax_ids', 'in', line.tax_id.ids),
                    ('move_type', '=', 'in_invoice'),
                ])
                # Aggregate amounts
                line.amount = sum(tax_lines.mapped('debit'))
                # Assuming tax amount can be calculated from the tax percentage
                line.taxamount = sum(tax_lines.mapped('tax_ids.amount'))  # Adjust as needed
     # Adjust as necessary


    # @api.depends('declaration_id.vat_sales_outputs.amount', 'declaration_id.vat_expenses_inputs.amount','declaration_id.vat_sales_outputs.taxamount', 'declaration_id.vat_expenses_inputs.taxamount')
    # def _compute_tax_amount(self):

    #     for line in self:
    #         if line.line_type == 'sales':
    #             jurnal_itiems =[]
    #             tax_lines = self.env['account.move.line'].search([
    #                 ('tax_ids', 'in', line.tax_id.ids),
    #                 ('move_type', '=', 'out_invoice'),
    #                 ])
    #             # for lines in tax_lines:
    #             #     jurnal_itiems= self.env['account.move.line'].search([
    #             #     ('move_name', '=', tax_lines.move_name),
    #             #     ('move_type', '=', 'out_invoice'),
    #             #     ])



    #             line.amount = sum(tax_lines.mapped('balance'))  
    #             line.taxamount = sum(tax_lines.mapped('credit')) 
    #         elif line.line_type == 'expenses':
    #             tax_lines = self.env['account.move.line'].search([
    #                 ('tax_ids', 'in', line.tax_id.ids),
    #                 ('move_type', '=', 'in_invoice'),
    #                 ])
    #             line.amount = sum(tax_lines.mapped('debit'))  
    #             line.taxamount = sum(tax_lines.mapped('debit'))  
    #         else:
    #             line.amount = 0.0
    #             line.taxamount = 0.0



class VatDeclaration(models.Model):
    _name = 'vat.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VAT Declaration 201'

    name = fields.Char(string='Reference', readonly=True, default='New')
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    vat_registration_id = fields.Many2one('vat.registration', string='VAT Registration', required=True)
    trn = fields.Char(string='TRN', related='vat_registration_id.trn', readonly=True, store=True)
    due_date = fields.Date(string='Due Date')
    legal_name = fields.Char(string='Legal Name of Entity', related='vat_registration_id.legal_name_english', readonly=True, store=True)
    signatore_id = fields.Many2one('authorised.signatory', string="Authorised Signatory")

    basic_rate_supplies_emirate = fields.Many2one(
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

    tax_id = fields.Many2one('account.tax',string="Tax")

    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status',default='draft')

    q_dates = fields.Selection([
        ('q1', 'Q1 Date'),
        ('q2', 'Q2 Date'),
        ('q3', 'Q3 Date'),
        ('q4', 'Q4 Date')
    ], string='Quarter Dates')


    @api.depends('vat_sales_outputs', 'vat_expenses_inputs')
    def _compute_totals(self):
        for record in self:
            record.total_sales = sum(record.vat_sales_outputs.mapped('amount'))
            record.total_sales_vat = sum(record.vat_sales_outputs.mapped('taxamount'))
            record.total_expenses = sum(record.vat_expenses_inputs.mapped('amount'))
            record.total_expenses_vat = sum(record.vat_expenses_inputs.mapped('taxamount'))
            record.net_vat = record.total_sales_vat - record.total_expenses_vat


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'

    @api.model
    def create(self, vals):
        record = super(VatDeclaration, self).create(vals)
        record.with_context(skip_generate_lines=True)._generate_lines()
        return record

    def write(self, vals):
        if not self.env.context.get('skip_generate_lines'):
            self.with_context(skip_generate_lines=True)._generate_lines()
        return super(VatDeclaration, self).write(vals)

    def _generate_lines(self):
        vat_sales_lines = []
        vat_expense_lines = []

        for tax in self.env['account.tax'].search([]):
            vat_sales_lines.append((0, 0, {
            'declaration_id': self.id,
            'line_type': 'sales',
            'tax_id': tax.id,
            'description': tax.description,
            'amount': 0.0,
            'taxamount': 0.0,
        }))

        for tax in self.env['account.tax'].search([]):
            vat_expense_lines.append((0, 0, {
            'declaration_id': self.id,
            'line_type': 'expenses',
            'tax_id': tax.id,
            'description': tax.description,
            'amount': 0.0,
            'taxamount': 0.0,
        }))

        self.with_context(skip_generate_lines=True).write({
        'vat_sales_outputs': vat_sales_lines,
        'vat_expenses_inputs': vat_expense_lines,
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
