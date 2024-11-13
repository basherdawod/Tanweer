from odoo import api, models, fields , _

class AccountTypeLevel(models.Model):
    _name = 'account.type.level'
    _description = 'Account Type Level'

    number_audit = fields.Char(strring="Number" ,readonly=True, default=lambda self: _('New'), copy=False)
    name = fields.Char(
        string='Name',
        required=False)
    account_level_type_ids = fields.One2many(
        comodel_name='account.type.audit',
        inverse_name='account_type_name',
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
        required=False,
        currency_field='currency_id',
        # compute='_compute_open_balance',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number_audit', _('New')) == _('New'):
                vals['number_audit'] = self.env['ir.sequence'].next_by_code('account.type.level') or _('New')
        records = super(AccountTypeLevel, self).create(vals_list)
        return records  # Ensure created records are returned


class AccountAccountTypeAudit(models.Model):
    _name = "account.type.audit"
    _description = "Audit Account Type"

    balance_this = fields.Float(
        string='This Year',
        required=False,
        compute='_compute_current_balance',
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
        compute='_compute_open_balance',
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
    def _compute_open_balance(self):
        for record in self:
            total_balance = 0.0
            for account in record.account_ids:
                print(f"Account ID: {account.id}, Current Balance: {account.opening_balance}")
                total_balance += account.opening_balance
            record.balance_last = total_balance



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

 # default=lambda self: self._default_account_type()