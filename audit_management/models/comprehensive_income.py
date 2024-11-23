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

    account_type = fields.Selection([
        ('revenue', 'Revenue'),
        ('direct_cost', 'Direct Cost'),
        ('selling_and_distribution_expenses', 'Selling and Distribution Expenses'),
        ('general_and_administrative_expenses', 'General and Administrative Expenses'),
        ('finance_cost', 'Finance Cost'),
        ('other_incomes', 'Other Incomes'),
    ], string='Account Type')


    comprehensive_income_line_ids = fields.One2many('comprehensive.income.line','comprehensive_income_id',string="Comprehensive Income Line")
    financial_id = fields.Many2one('financial.audit.customer', string="Financial Report")
    # account_lines_ids = fields.One2many(
    #     comodel_name='account.type.level',
    #     inverse_name='audit_financial_id',
    #     string='Account Lines',
    #
    #     # domain=lambda self: [('type', '=', self.account_type)]
    # )
    audit_lines_ids = fields.One2many(
        comodel_name='account.audit.level.line',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False

    )



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('comprehensive.income') or _('New')
        res = super(ComprehensiveIncome, self).create(vals_list)
        return res

    def action_create_audit_line(self):
        self.write({
            'comprehensive_income_line_ids': [(5, 0, 0)]
        })
        line_vals = []

        for record in self:
            level = self.env['audit.account.account.line'].search([])
            for line in record.comprehensive_income_line_ids:
                vals = {
                    'code': line.code,
                    'account_name': line.name,
                    'total_last_year': line.opening_balance,
                    'total_this_year': line.current_balance,
                }
                line_vals.append(vals)
            if line_vals:
                self.write({
                    'comprehensive_income_line_ids': [Command.create(vals) for vals in line_vals]
                })


class ComprehensiveIncomeLine(models.Model):
    _name = 'comprehensive.income.line' #model_comprehensive_income_line
    _description = 'Comprehensive Income Line'


    code = fields.Char(string="Code")
    account_name = fields.Char(string="Account Name")
    total_last_year = fields.Float(string="Total Last Year")
    total_this_year = fields.Float(string="Total This Year")
    comprehensive_income_id = fields.Many2one('comprehensive.income','comprehensive_income_line_ids')
    financial_line_id = fields.Many2one('financial.audit.customer', string="Financial Report")

