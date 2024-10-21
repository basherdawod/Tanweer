from odoo import models, fields, api, _

class PettyCashMasterCard(models.Model):
    _name = 'petty.cash.card'
    _description = 'Petty Cash Card'
    _rec_names_search =['name']
    _rec_names = 'name'
    name = fields.Char(string="Petty cash Code"
                       , readonly=True, default=lambda self: _('New'), copy=False  )

    # info = fields.Char("PETTY CASH NAME")
    section = fields.Char(string="Section")
    employee_id = fields.Many2one('hr.employee',
                                  string="Employee", required=True)
    job_title = fields.Many2one(string="Job title"
                                , related = "employee_id.department_id")
    address = fields.Char(string="Employee address "
                          , related = "employee_id.private_street")
    phone = fields.Char(string=" Mobile No ",
                        related = "employee_id.private_phone")
    email = fields.Char(string="Email "
                        , related = "employee_id.private_email" )
    open_balance = fields.Monetary(
        string="Total In Currency",
        currency_field='currency_id',
        store=True, readonly=False,
        tracking=True,
    )

    def add_amount(self, increment_value):
        for record in self:
            record.open_balance += increment_value
        return True

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        string="Report Company Currency",
        readonly=True,
    )
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True ,
                                  default=lambda self: self.env.ref('base.AED'))
    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account",
        store=True, readonly=False,
        domain="[('account_type', 'in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card')), ('company_id', '=', company_id)]",
        help="An petty cash account is petty cash",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('petty.cash.card') or _('New')
        res = super(PettyCashMasterCard, self).create(vals_list)
        return res