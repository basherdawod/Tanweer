from odoo import models, fields, api

class CorporateTax(models.Model):
    _name = 'corporate.tax'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _description = 'Corporate Tax'
    
    name = fields.Char(string='Corporate Tax', readonly=True, copy=False, default='New')
    trn = fields.Char(string='TRN', related='vat_registration_id.trn', readonly=True, store=True)
    legal_name = fields.Char(string='Legal Name of Entity', related='vat_registration_id.legal_name_english', readonly=True, store=True)
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft')
    vat_registration_id = fields.Many2one('vat.registration', string='VAT Registration', required=True, domain="[('tax_type', '=', 'corporate_tax')]")

    # revenue = fields.Float(string="Total Revenue", compute="_compute_profit", store=True)
    # costs = fields.Float(string="Total Costs", compute="_compute_profit", store=True)
    # taxes = fields.Float(string="Total Taxes", compute="_compute_profit", store=True)
    # exemptions = fields.Float(string="Exemptions", required=True, default=0.0)
    # net_profit = fields.Float(string="Net Profit", compute="_compute_profit", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    move_id = fields.Many2one("account.move.line", string="Account Move")

    account_id = fields.Many2one('account.account', string='Account')  # علاقة Many2one مع account.account
    # total_balance = fields.Monetary(string='Total Balance', related="move_id.balance", store=True,currency_field='currency_id')
    total_debit = fields.Float(string="Total Debit")
    total_credit = fields.Float(string="Total Credit")

    total_current_balance = fields.Float(string='Total Current Balance')
    amount = fields.Float(string="Amount",compute='_compute_tax_amount',store=True)


    # @api.model
    # def compute_total_current_balance(self):
    #     self.env.cr.execute("""
    #         SELECT SUM("account.account".current_balance) 
    #         FROM account_account 
    #     """)
    #     total_balance = self.env.cr.fetchone()[0] 
    #     self.total_current_balance = total_balance

    def _sql_from_amls_two(self):
        sql = """SELECT r.account_tax_id,
                 COALESCE(SUM("account_move_line".debit - "account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s
                 GROUP BY r.account_tax_id"""
        return sql

    def _compute_tax_amount(self):
        # Dictionary to store the calculated amount for each tax
        taxes = {}
        for line in self:
            taxes[line.tax_id.id] = {'amount': 0.0}

        # Generate SQL without date filters
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        
        # Ensure tables and where_clause are valid
        if not tables or not where_clause:
            return  # Skip calculation if no tables or where_clause are available

        # Amount calculation only
        sql2 = self._sql_from_amls_two()
        query = sql2 % (tables, where_clause)
        
        # Execute SQL query
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        
        # Assign fetched results to taxes dictionary
        for result in results:
            account_tax_id, net_amount = result
            if account_tax_id in taxes:
                taxes[account_tax_id]['amount'] = abs(net_amount)

        # Update the amount field only
        for line in self:
            if line.tax_id.id in taxes:
                line.amount = taxes[line.tax_id.id]['amount']

   



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
