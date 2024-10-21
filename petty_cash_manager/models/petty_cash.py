from odoo import models, fields, api, _

class PettyCashAccount(models.Model):
    _name = 'petty.cash.account'
    _description = 'Petty Cash Account'

    name = fields.Char(string="Petty Cash Name", required=True)
    balance = fields.Float(string="Balance", compute='_compute_balance', readonly=True)
    transactions = fields.One2many('petty.cash.request', 'petty_cash_account_id', string="Transactions")

    @api.depends('transactions.request_amount')
    def _compute_balance(self):
        for account in self:
            account.balance = sum(account.transactions.mapped('request_amount'))
