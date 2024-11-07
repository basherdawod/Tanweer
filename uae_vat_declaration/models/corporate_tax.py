from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
# _logger.info("Starting _compute_account_balance")
class CorporateTax(models.Model):
    _name = 'corporate.tax'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Corporate Tax'
    
    name = fields.Char(string='Corporate Tax', readonly=True, copy=False, default='New')
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

    # New fields for net profit and corporate tax
    net_profit = fields.Float(string="Net Profit",compute="_compute_net_profit", store=True)
    corporate_tax = fields.Float(string="Corporate Tax", compute='_compute_corporate_tax', store=True)
    
    # Amount is still computed from account balance
    amount = fields.Float(string="Amount", compute='_compute_account_balance', store=True)

    income_total = fields.Float(string="Total Income Balance", compute='_compute_income_balance')

    @api.depends()
    def _compute_income_balance(self):
        # البحث عن الحسابات التي نوعها 'income', 'income_other', 'expense'
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

        if income_total > 357000:
            self.income_total = (income_total - 357000) * 0.9
        else:
            self.income_total = income_total

            
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
