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
        inverse_name='account_name_type',
        string='Account',
        required=False)
    audit_financial_id = fields.Many2one(
        comodel_name='comprehensive.income',
        string='Comprehensive Income')

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
        # compute='_compute_current_balance',
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
    balance_last = fields.Monetary(
        string='Total Last Year',
        required=False,
        currency_field='currency_id',
    )
    total_balance_last = fields.Monetary(
            string='Total Last Year',
            required=False,
            currency_field='currency_id',
        )




class AccountTypeLevel(models.Model):
    _name = 'account.audit.line.level'  #model_account_audit_line_level
    _description = 'Account line level '
    _order = 'audit_financial_id, sequence, id'

    audit_financial_id = fields.Many2one(
        comodel_name='comprehensive.income',
        string='Comprehensive Income',
        required=False , readonly=True )
    sequence = fields.Integer(string="Sequence", default=10)

    name = fields.Char(string="Name")

    seq = fields.Integer(string="seq")
    seq2 = fields.Integer(string="seq")
    seq3 = fields.Integer(string="seq")

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_sub', "Sub Section "),
        ],
        default=False)

    level_line_id = fields.Many2one(
        comodel_name='account.level.type',
        string='Account Type',
        readonly=True,
        required=False)

    balance_this = fields.Float(
        string='This Year',
        required=False,
        related="level_line_id.balance_this",
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",

        required=True,
        default=lambda self: self.env.company.currency_id
    )

    balance_last = fields.Monetary(
        string='Last Year',
        related="level_line_id.balance_last",
        required=False,
        currency_field='currency_id',
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
        string="Type",
        related="level_line_id.type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )

    @api.depends('level_line_id')
    def _compute_name(self):
        for line in self:
            # If there's no 'level_line_id', assign a name based on audit_financial_id levels
            print("Line Fields:", dir(line))
            if not line.level_line_id:
                # Handle the case where audit_financial_id is not set
                if line.name !='' and line.seq == 1:
                    line.name = line.audit_financial_id.level1.name
                elif line.name !='' and line.seq2 == 2:
                    line.name = line.audit_financial_id.level2.name
                elif line.name !='' and line.seq3 == 3:
                    line.name = line.audit_financial_id.level3.name
                else:
                    print("Name",line.name )
                    line.name = "No line"
                continue  # Skip the next logic if no level_line_id


            # If 'level_line_id' is set, directly use its 'name' or 'type' (depending on the field you want)
            else:
                line.name =''  # or use line.level_line_id.type if that's more appropriate

