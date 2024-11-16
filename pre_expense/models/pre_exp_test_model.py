from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class PreExpTestModel(models.Model):
    _name = 'pre.exp.test.model'
    _description = 'Prepaid Expense Test Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    account_number = fields.Char(string='Account Number', tracking=True)
    category_id = fields.Many2one('pre.exp.test.category', string='Category', tracking=True)
    contract_start_date = fields.Date(string='Contract Start Date', tracking=True)
    contract_end_date = fields.Date(string='Contract End Date', tracking=True)
    method_period = fields.Integer(string='Period (months)', default=1, tracking=True)
    contract_amount = fields.Float(string='Contract Amount', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('close', 'Closed')
    ], string='Status', default='draft', tracking=True)

    line_ids = fields.One2many('pre.exp.test.line', 'expense_id', string='Expense Lines')

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'confirm'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pre.exp.test.model',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }

    def action_close(self):
        self.write({'state': 'close'})

    def action_compute_expenses(self):
        self.ensure_one()
        self.line_ids.unlink()  # Remove existing lines
        
        if not (self.contract_start_date and self.contract_end_date and self.contract_amount and self.method_period):
            return

        current_date = self.contract_start_date
        end_date = self.contract_end_date
        total_days = (end_date - current_date).days + 1
        daily_amount = self.contract_amount / total_days

        while current_date <= end_date:
            next_date = current_date + relativedelta(months=self.method_period)
            if next_date > end_date:
                next_date = end_date

            days_in_period = (next_date - current_date).days + 1
            amount = daily_amount * days_in_period

            self.env['pre.exp.test.line'].create({
                'expense_id': self.id,
                'name': f"Expense from {current_date} to {next_date}",
                'date': next_date,
                'amount': amount,
            })

            current_date = next_date + relativedelta(days=1)

class PreExpTestLine(models.Model):
    _name = 'pre.exp.test.line'
    _description = 'Prepaid Expense Test Line'

    name = fields.Char(string='Description')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')
    move_id = fields.Many2one('account.move', string='Journal Entry')
    expense_id = fields.Many2one('pre.exp.test.model', string='Prepaid Expense', ondelete='cascade')