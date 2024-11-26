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
        required=True)
    
    account_level_type_ids = fields.One2many(
        comodel_name='account.type.audit',
        inverse_name='account_type_name',
        string='Account',
        required=False)
    account_type_ids = fields.One2many(
        comodel_name='addition.period.assets',
        inverse_name='account_ids',
        string='Cost',
        required=False)
    account_share_capital = fields.One2many(
        comodel_name='share.capital.assets',
        inverse_name='share_capital',
        string='Equity',
        required=False)

    account_type_accumulated = fields.One2many(
        comodel_name='addition.acccumulated.assets',
        inverse_name='accumulated_account',
        string='Accumulated',
        required=False)
    audit_financial_id = fields.Many2one(
        comodel_name='audit.financial.program',
        string='Audit Financial Program')
    comprehensive_income_id = fields.Many2one(
        comodel_name='comprehensive.income',
        string='Comprehensive Income')


    accumulated = fields.Boolean(
        string='Accumulated',
        required=False)
    work_In_Progress = fields.Boolean(
            string='Work',
            required=False)

    capital_share = fields.Boolean(
            string='Capital Share',
            required=False)


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
        string='Total This Year',
        required=False,
        compute='_compute_current_balance',
    )
    total_balance_this = fields.Float(
        string='This Year',
        required=False,
    )
    accum = fields.Char(
        string='Accumulated',
        required=False ,readonly=True )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    account_account_line = fields.Many2one(
        comodel_name='audit.account.account.line',
        string='Account Account line', domain=[ ('account_type','=',type)],
        required=False)
    customer_req_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Rege', related="audit_financial_id.partner_id",
        required=False)

    balance_last = fields.Monetary(
        string='Total Last Year',
        required=False,
        currency_field='currency_id',
        compute='_compute_open_balance',
    )
    total_balance_last = fields.Monetary(
            string='Total Last Year',
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

    @api.depends('account_type_accumulated.balance_this','account_type_ids.balance_this' ,'account_level_type_ids.balance_this', 'type')
    def _compute_current_balance(self):
        for record in self:
            balance = 0.0
            if record.type and record.account_level_type_ids :
                balance = sum(line.balance_this for line in record.account_level_type_ids)
                record.balance_this = balance
            elif record.type and record.account_type_ids :
                balance = sum(line.balance_this for line in record.account_type_ids)
                record.balance_this = balance
            elif record.type and record.account_type_accumulated :
                balance = sum(line.balance_this for line in record.account_type_accumulated)
                record.balance_this = balance
            else:
                record.balance_this = record.total_balance_this

    @api.depends('account_type_accumulated.balance_last','account_type_ids.balance_last' ,'account_level_type_ids.balance_last', 'type')
    def _compute_open_balance(self):
        for record in self:
            if record.type and record.account_level_type_ids :
                balance = sum(line.balance_last for line in record.account_level_type_ids)
                record.balance_last = balance
            elif record.type and record.account_type_ids :
                balance = sum(line.balance_last for line in record.account_type_ids)
                record.balance_last = balance
            elif record.type and record.account_type_accumulated:
                balance = sum(line.balance_last for line in record.account_type_accumulated)
                record.balance_last = balance
            else:
                record.balance_last = record.total_balance_last


class AccountAccountTypeAudit(models.Model):
    _name = "account.type.audit"
    _description = "Audit Account Type"


    account_type_name = fields.Many2one(
        comodel_name='account.type.level',
        string='Account Type',
        required=False,
    )
    account_name_type = fields.Many2one(
        comodel_name='account.level.type',
        string='Account Type',
        required=False,
    )

    account_ids = fields.Many2one(
        comodel_name='audit.account.account.line',
        string='Account',
        required=False)

    customer_req_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Rege', related="account_type_name.customer_req_id",
        required=False)

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
        string="Type",related='account_type_name.type',
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )

    balance_this = fields.Float(
        string='This Year',
        required=False,
        related='account_ids.current_balance',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    # Define the monetary field with the currency_field parameter

    balance_last = fields.Float(
        string='Last Year',
        required=False ,
        related='account_ids.opening_balance',
    )

    balance_credit = fields.Float(
        string='credit',
        required=False,
        related='account_ids.opening_credit',
    )
    balance_debit = fields.Float(
        string='credit',
        required=False,
        related='account_ids.opening_debit',
    )


class AdditionPeriodAssets(models.Model):
    _name = 'addition.period.assets'
    _description = 'AdditionPeriodAssets'


    account_ids = fields.Many2one(
        comodel_name='account.type.level',
        string='Account',
    )
    accounts_account = fields.Many2many("account.account")
    balance_last_last = fields.Float(string="2022")
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
        string="Type", related='account_ids.type',
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )

    account = fields.Many2one(
        comodel_name='audit.account.account.line',
        string='Cost',
    )
    customer_req_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Rege', related="account_ids.customer_req_id",
        required=False)


    balance_this = fields.Float(
        string='This Year',
        required=False,
        related='account.current_balance',
    )
    balance_2years = fields.Float(
        string='Last 2 Year',
        required=False,
        related='account.balance_2years',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    # Define the monetary field with the currency_field parameter

    balance_last = fields.Float(
        string='Last Year',
        required=False,
        related='account.opening_balance',
    )

    balance_credit = fields.Float(
        string='credit',
        required=False,
        related='account.opening_credit',
    )
    balance_debit = fields.Float(
        string='Debit',
        required=False,
        related='account.opening_debit',
    )




class AdditionAcccumulatedAssets(models.Model):
    _name = 'addition.acccumulated.assets' #model_addition_acccumulated_assets
    _description = 'AdditionAccumulated'

    accumulated_account = fields.Many2one(
        comodel_name='account.type.level',
        string='Account',
    )
    balance_last_last = fields.Float(string="2022")
    account = fields.Many2one(
        comodel_name='audit.account.account.line',
        string='Account'
    )
    accounts_account = fields.Many2many("account.account")
    customer_req_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Rege', related="accumulated_account.customer_req_id",
        required=False)

    balance_this = fields.Float(
        string='This Year',
        required=False,
        related='account.current_balance',
    )
    balance_2years = fields.Float(
        string='Last 2 Year',
        required=False,
        related='account.balance_2years',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    balance_last = fields.Float(
        string='Last Year',
        required=False,
        related='account.opening_balance',
    )

    balance_credit = fields.Float(
        string='credit',
        required=False,
        related='account.opening_credit',
    )
    balance_debit = fields.Float(
        string='credit',
        required=False,
        related='account.opening_debit',
    )
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
        string="Type", related='accumulated_account.type',
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )

class ShareCapitalAssets(models.Model):
    _name = 'share.capital.assets' #model_addition_acccumulated_assets
    _description = 'Share Capital Assets'

    share_capital = fields.Many2one(
        comodel_name='account.type.level',
        string='Account',
    )
    account = fields.Many2one(
        comodel_name='audit.account.account.line',
        string='Account'
    )
    customer_req_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Rege', related="share_capital.customer_req_id",
        required=False)

    balance_this = fields.Float(
        string='This Year',
        required=False,
        related='account.current_balance',
    )
    share_perc= fields.Float(
        string='Share %',
        required=False , readonly=False)
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
        string="Type", related='share_capital.type',
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )
