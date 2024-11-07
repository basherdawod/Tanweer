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
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('none','None')
    ], string='Line Type', related="tax_id.type_tax_use")

    tax_id = fields.Many2one('account.tax', string='Tax', required=True)
    description = fields.Char(string='Description', related='tax_id.description', readonly=True)
    amount = fields.Float(string='Amount' ,compute='_compute_tax_amount',store=True)
    taxamount = fields.Float(string='Tax Amount', compute='_compute_tax_amount', store=True)
    # adjustment = fields.Float(string='Adjustment')

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


class VatDeclaration(models.Model):
    _name = 'vat.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VAT Declaration 201'

    name = fields.Char(string='Reference', readonly=True, default='New')
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

    vat_sales_outputs = fields.One2many('vat.declaration.line', 'declaration_id', string='VAT Sales and Outputs')
    vat_expenses_inputs = fields.One2many('vat.declaration.line', 'declaration_id', string='VAT Expenses and Inputs')

    total_sales = fields.Float(string='Total Sales', compute='_compute_totals', store=True)
    total_sales_vat = fields.Float(string='Total Sales VAT', compute='_compute_totals', store=True)
    total_purchase = fields.Float(compute="_compute_totals", string="Total Purchase", store=True)
    total_purchase_vat = fields.Float(compute="_compute_totals", string="Total Purchase VAT", store=True)
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
    line_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('none','All')
    ], string='Line Type',required=True)


    # @api.depends('vat_sales_outputs')
    # def _compute_totals(self):
    #     for record in self:
    #         record.total_sales = sum(record.vat_sales_outputs.mapped('amount'))
    #         record.total_sales_vat = sum(record.vat_sales_outputs.mapped('taxamount'))
    
    @api.depends('vat_sales_outputs')
    def _compute_totals(self):
        for record in self:
            # اجمالي المبيعات
            sales_lines = record.vat_sales_outputs.filtered(lambda line: line.line_type == 'sale')
            record.total_sales = sum(sales_lines.mapped('amount'))
            record.total_sales_vat = sum(sales_lines.mapped('taxamount'))
            
            # اجمالي المشتريات
            purchase_lines = record.vat_sales_outputs.filtered(lambda line: line.line_type == 'purchase')
            record.total_purchase = sum(purchase_lines.mapped('amount'))
            record.total_purchase_vat = sum(purchase_lines.mapped('taxamount'))


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

        for tax in self.env['account.tax'].search([]):
            if tax.type_tax_use == self.line_type :
                vat_sales_lines.append((0, 0, {
                'declaration_id': self.id,
                'tax_id': tax.id,
                'description': tax.description,
                'amount': 0.0,
                'taxamount': 0.0,
            }))
            else:
                vat_sales_lines.append((0, 0, {
                'declaration_id': self.id,
                'tax_id': tax.id,
                'description': tax.description,
                'amount': 0.0,
                'taxamount': 0.0,
            }))


        self.with_context(skip_generate_lines=True).write({
        'vat_sales_outputs': vat_sales_lines,
        # 'vat_expenses_inputs': vat_expense_lines,
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
