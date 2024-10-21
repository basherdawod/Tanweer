from lib2to3.fixes.fix_input import context

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class PettyCashSubmission(models.Model):
    _name = 'petty.cash.submission'
    _description = 'Petty Cash Submission'

    name = fields.Char(string="Submission Reference", required=True, readonly=True,
                       default=lambda self: _('New'), copy=False)
    # code_petty_cash = fields.Char(string="Petty Cash Code", related="petty_cash_request_id.request_code")
    petty_cash_request_id = fields.Many2one('petty.cash.request',
                                            string="Petty Cash Request", required=True)
    payment_type = fields.Selection([('send', 'Send'), ('receive', 'Receive')], default="send", string="Payment Type",
                                    required=True)
    user_approval = fields.Many2one('res.users', string="User Approval ", required=True)


    submission_date = fields.Date(string="Submission Date", default=date.today(), required=True)
    total_spent = fields.Float(string="Total Amount Spent", compute="_compute_amount", store=True, readonly=True)
    remaining_amount = fields.Float(string="Remaining Amount", compute="_compute_remaining_amount", store=True)
    expense_details = fields.One2many('petty.cash.expense.line', 'submission_id', string="Expense Details")
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved')],
                             default='draft')
    journal_entry_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.AED'))

    @api.depends('expense_details', 'expense_details.amount')
    def _compute_amount(self):
        for sheet in self:
            sheet.total_spent = sum([line.amount for line in sheet.expense_details])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('petty.cash.submission') or _('New')
        res = super(PettyCashSubmission, self).create(vals_list)
        return res

    def copy_data(self, default=None):
        default = dict(default or {})
        return super().copy_data(default)

    @api.depends('petty_cash_request_id.request_amount', 'total_spent')
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.petty_cash_request_id.request_amount - rec.total_spent

    def action_submit(self):
        self.state = 'submitted'

    def action_submit_payment(self):
        self.state = 'submitted'
        payment = self.env['petty.cash.payment'].create({
            'user_approval': self.user_approval.id,
            'account_id': self.petty_cash_request_id.account_id.id,
            'amount': self.total_spent,
            'payment_type': self.payment_type,
            'currency_id': self.currency_id.id,
            'employee_request': self.petty_cash_request_id.id,
            'employee_petty': self.petty_cash_request_id.employee_petty.id,
            'petty_code': self.petty_cash_request_id.petty_code,
            'employee_submission': self.id,
        })


class PettyCashExpenseLine(models.Model):
    _name = 'petty.cash.expense.line'
    _description = 'Petty Cash Expense Line'

    submission_id = fields.Many2one('petty.cash.submission', string="Submission Reference")
    # code_petty_cash = fields.Char(string="Petty Cash Code", related="petty_cash_request_id.request_code")
    description = fields.Char(string="Description", required=True)
    amount = fields.Float(string="Amount", required=True)
    reference = fields.Char(string="REF", required=True)
    date = fields.Date(string="Date", required=True)
    account = fields.Many2one(
        comodel_name='account.account',
        string="A/C Name",
        store=True, readonly=True,
        compute="_compute_account_name",
        domain="[('account_type', 'in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card')), ('company_id', '=', company_id)]", required=True
    )
    account_code = fields.Char(string="A/C Code", store=True , required=True)


    @api.depends('account_code' , 'account' )
    def _compute_account_name(self):
        for rec in self:
            if rec.account_code :
                rec.account = self.env['account.account'].search([('code', '=', rec.account_code)], limit=1)
