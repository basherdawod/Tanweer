from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date


class AccountLevelType(models.Model):
    _name = 'account.level.type' #model_account_level_type
    _description = 'Account Type Level'

    number_audit = fields.Char(string="Note", readonly=True, default=lambda self: _('New'), copy=False)
    name = fields.Char(
        string='Name',
        required=True)

    account_level_type_ids = fields.One2many(
        comodel_name='account.type.audit',
        inverse_name='account_type_name',
        string='Account',
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
        string='Total This Year',
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
    account_account_line = fields.Many2one(
        comodel_name='audit.account.account.line',
        string='Account Account line', domain=[('account_type', '=', type)],
        required=False)
    customer_req_id = fields.Many2one(
        comodel_name='financial.audit.customer',
        string='Customer Rege', related="audit_financial_id.partner_id",
        required=False)

