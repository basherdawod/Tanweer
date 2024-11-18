from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date


class FinancialAuditReporting(models.Model):
    _name = "financial.audit.reporting"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Audit Report Financial"

    name = fields.Char(strring="Number", readonly=True, default=lambda self: _('New'), copy=False,
                       translate=True)

    level1 = fields.Char('Main', translate=True)
    level2 = fields.Char('Main', translate=True)
    level3 = fields.Char('Main ', translate=True)

    partner_id = fields.Many2one('res.partner', string="Customer Name")
    data_fis_years_end = fields.Date(
        string='Fiscal Year End',
        required=False,
        default=lambda self: datetime(date.today().year, 12, 31).strftime("%Y-%m-%d")
    )
    data_last_years_end = fields.Date(
        string='Last Fiscal Year End',
        required=False,
        default=lambda self: datetime(date.today().year - 1, 12, 31).strftime("%Y-%m-%d")
    )
    audit_lines_ids = fields.One2many(
        comodel_name='account.audit.level.line',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False
    )


class AccountTypeLevel(models.Model):
    _name = 'account.audit.level.line'
    _description = 'Account Level Line'

    audit_financial_id = fields.Many2one(
        comodel_name='audit.financial.program',
        string='Account Type',
        required=False, readonly=True)
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
        comodel_name='account.type.level',
        string='Account Type',
        readonly=True,
        required=False)
    account_type_level = fields.Many2one('account.type.level',string="Account Type")

    balance_this = fields.Float(
        string='This Year',
        required=False,
        related="level_line_id.balance_this",
        # compute='_compute_current_balance',
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
    level1_match = fields.Boolean(string="Level 1 Match", compute="_compute_level1_match")

    @api.depends('audit_financial_id', 'level_line_id')
    def _compute_level1_match(self):
        for record in self:
            # Ensure both fields are set before comparing
            if record.audit_financial_id.level1 == record.level_line_id.name:
                record.level1_match = True
            elif record.audit_financial_id.level2 == record.level_line_id.name:
                record.level1_match = True
            elif record.audit_financial_id.level3 == record.level_line_id.name:
                record.level1_match = True
            else:
                record.level1_match = False

    @api.depends('level_line_id')
    def _compute_name(self):
        for line in self:
            # If there's no 'level_line_id', assign a name based on audit_financial_id levels
            print("Line Fields:", dir(line))
            if not line.level_line_id:
                # Handle the case where audit_financial_id is not set
                if line.name != '' and line.seq == 1:
                    line.name = line.audit_financial_id.level1
                elif line.name != '' and line.seq2 == 2:
                    line.name = line.audit_financial_id.level2
                elif line.name != '' and line.seq3 == 3:
                    line.name = line.audit_financial_id.level3
                else:
                    print("Name", line.name)
                    line.name = "No line"
                continue  # Skip the next logic if no level_line_id


            # If 'level_line_id' is set, directly use its 'name' or 'type' (depending on the field you want)
            else:
                line.name = ''  # or use line.level_line_id.type if that's more appropriate
