from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date

class AccountTypeLevel(models.Model):
    _name = 'account.type.level'
    _description = 'Account Type Level'

    number_audit = fields.Char(string="Note" ,readonly=True, default=lambda self: _('New'), copy=False)
    name = fields.Char(
        string='Name',
        required=False)
    
    account_level_type_ids = fields.One2many(
        comodel_name='account.type.audit',
        inverse_name='account_type_name',
        string='Account Type',
        required=False)
    account_type_ids = fields.One2many(
        comodel_name='addition.period.assets',
        inverse_name='account_ids',
        string='Account Type',
        required=False)
    audit_financial_id = fields.Many2one(
        comodel_name='audit.financial.program',
        string='Audit Financial Program')


    type = fields.Selection(
        selection=[
            ("asset_receivable", "Receivable"),
            ("asset_cash", "Bank and Cash"),
            ("asset_current", "Current Assets"),
            ("asset_non_current", "Non-current Assets"),
            ("asset_prepayments", "Prepayments"),
            ("asset_fixed", "Fixed Assets"),
            ("liability_payable", "Payable"),
            ("liability_credit_card", "Credit Card"),
            ("liability_current", "Current Liabilities"),
            ("liability_non_current", "Non-current Liabilities"),
            ("equity", "Equity"),
            ("equity_unaffected", "Current Year Earnings"),
            ("income", "Income"),
            ("income_other", "Other Income"),
            ("expense", "Expenses"),
            ("expense_depreciation", "Depreciation"),
            ("expense_direct_cost", "Cost of Revenue"),
            ("off_balance", "Off-Balance Sheet"),
        ],
        string="Type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )
    balance_this = fields.Float(
        string='This Year',
        required=False,
        compute='_compute_current_balance',
    )
    total_balance_this = fields.Float(
        string='This Year',
        required=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    balance_last = fields.Monetary(
        string='Last Year',
        required=False,
        currency_field='currency_id',
        compute='_compute_open_balance',
    )
    total_balance_last = fields.Monetary(
            string='Last Year',
            required=False,
            currency_field='currency_id',
        )

    def _inverse_balance_last(self):
        """
        This method is triggered when 'balance_last' is updated directly.
        It syncs the balance_last field with the total_balance_last field when appropriate.
        """
        for record in self:
            if record.total_balance_last != 0.0 and record.balance_last == 0.0:
                # If total_balance_last is set and balance_last is zero, set balance_last to total_balance_last
                record.balance_last = record.total_balance_last
            elif record.total_balance_last == 0.0 and record.balance_last != 0.0:
                # You could add additional logic to reset or manage other fields if needed
                pass


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number_audit', _('New')) == _('New'):
                vals['number_audit'] = self.env['ir.sequence'].next_by_code('account.type.level') or _('New')
        records = super(AccountTypeLevel, self).create(vals_list)
        return records  # Ensure created records are returned

    @api.depends('balance_this' , 'account_level_type_ids' ,'account_level_type_ids.balance_this',)
    def _compute_current_balance(self):
        for record in self:
            balance = 0.0
            if record.type:
                for line in record.account_level_type_ids:
                    balance += line.balance_this
                record.balance_this = balance
            else:
                record.balance_this = record.total_balance_this

    @api.depends('account_level_type_ids.balance_last', 'type')
    def _compute_open_balance(self):
        for record in self:
            if record.type:
                balance = sum(line.balance_last for line in record.account_level_type_ids)
                record.balance_last = balance
            else:
                record.balance_last = record.total_balance_last

class AccountAccountTypeAudit(models.Model):
    _name = "account.type.audit"
    _description = "Audit Account Type"

    balance_this = fields.Float(
        string='This Year',
        required=False,
        compute='_compute_balance',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    # Define the monetary field with the currency_field parameter

    balance_last = fields.Monetary(
        string='Last Year',
        required=False ,
        currency_field='currency_id',
        compute='_compute_balance',
    )
    account_ids = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        domain=lambda self: self._get_account_domain()
    )

    @api.depends('account_ids')
    def _compute_current_balance(self):
        for record in self:
            total_balance = 0.0
            for account in record.account_ids:
                print(f"Account ID: {account.id}, Current Balance: {account.current_balance}")
                total_balance += account.current_balance
            record.balance_this = total_balance

    @api.depends('account_ids')
    def _compute_balance(self):
        for record in self:
            total_balance_this = 0.0
            total_balance_last = 0.0

            # Define the date ranges for the current and previous years
            current_year_start = date(date.today().year, 1, 1)
            current_year_end = date(date.today().year, 12, 31)
            last_year_start = date(date.today().year - 1, 1, 1)
            last_year_end = date(date.today().year - 1, 12, 31)

            # Calculate balances for each account
            for account in record.account_ids:
                lines = self.env['account.move.line'].search([
                    ('account_id', '=', account.id)
                ])
                for line in lines:
                    # Calculate balance for the current year
                    if current_year_start <= line.date <= current_year_end:
                        total_balance_this += line.debit - line.credit
                    # Calculate balance for the previous year
                    elif last_year_start <= line.date <= last_year_end:
                        total_balance_last += line.debit - line.credit

            # Assign computed balances
            record.balance_this = total_balance_this
            record.balance_last = total_balance_last

    def _get_account_domain(self):
        if not self.account_type_name:
            print("Account type is not set")
            return []

        type_key = self.account_type_name.type
        type_selection = dict(self.account_type_name._fields['type'].selection).get(type_key)

        print("Account Type Key:", type_key)  # Should print the key (e.g., 'asset_current')
        print("Account Type Label:", type_selection)  # Should print the label (e.g., 'Asset Current')

        return [('account_type', '=', type_key)]

    # Account Type Level selection (this will filter accounts)
    account_type_name = fields.Many2one(
        comodel_name='account.type.level',
        string='Account Type',
        required=False,

          # Default handler
    )

class AdditionPeriodAssets(models.Model):
    _name = 'addition.period.assets'
    _description = 'AdditionPeriodAssets'

    account_ids = fields.Many2one(
        comodel_name='account.type.level',
        string='Account',
    )
    account = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        domain=lambda self: self._get_account_domain()
    )

    account_move_line= fields.Many2one(
        comodel_name='account.move.line',
        string='Account',
        domain=lambda self: self._get_account_domain()
    )
    
    def _get_account_domain(self):
        if not self.account_ids:
            print("Account type is not set")
            return []
        return [('account_id', '=', self.account)]