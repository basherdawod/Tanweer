from odoo import models, fields, api, _
from num2words import num2words
from odoo.exceptions import AccessError, ValidationError, UserError


class PettyCashRequest(models.Model):
    _name = 'petty.cash.request'
    _description = 'Petty Cash Request'
    _order = 'date desc'  # Optional: To order requests by date

    name = fields.Char("Request Code", readonly=True, default=lambda self: _('New'), copy=False)
    date = fields.Date(string="Request Date", default=fields.Date.today(), required=True)
    account_code = fields.Char(string="Account Code", compute="_compute_account_code", store=True)
    user_approval = fields.Many2one('res.users', string="User Approval", required=True)
    employee_petty = fields.Many2one(string="Employee Approval", related="petty_card.employee_id")
    petty_card = fields.Many2one('petty.cash.card', string="Petty Card", store=True)
    petty_code = fields.Char(string="Petty Code", required=True)
    account_id = fields.Many2one(string="Account", related="petty_card.account_id")
    request_amount = fields.Float(string="Amount", required=True)
    amount_in_words = fields.Char(string="Amount in Words", compute="_compute_amount_in_words")
    petty_cash_account_id = fields.Many2one('petty.cash.account', string="Petty Cash Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.AED'))
    payment_type = fields.Selection([('send', 'Send'), ('receive', 'Receive')], default="receive",
                                    string="Payment Type", required=True)

    note = fields.Html(string="NOTES", store=True, readonly=False)
    follow = fields.Html(string="FOR THE FOLLOWING REASONS", store=True, readonly=False)
    purpose = fields.Text(string="Purpose")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('reimbursed', 'Reimbursed')
    ], default='draft', string="Status", tracking=True)

    @api.onchange('petty_code')
    def _onchange_petty(self):
        self.write({
            'petty_card': self.env['petty.cash.card'].search([('name', '=', self.petty_code)], limit=1),
        })

    @api.depends('request_amount')
    def _compute_amount_in_words(self):
        for record in self:
            record.amount_in_words = num2words(record.request_amount, to='currency', lang='en').capitalize()

    @api.depends('account_id')
    def _compute_account_code(self):
        for rec in self:
            rec.account_code = rec.account_id.code if rec.account_id else ''

    def action_approve(self):
        self.state = 'approved'
        self.env['petty.cash.payment'].create({
            'user_approval': self.user_approval.id,
            'account_id': self.account_id.id,
            'amount': self.request_amount,
            'petty_code': self.petty_code,
            'payment_type': self.payment_type,
            'employee_petty': self.employee_petty.id,
            'employee_request': self.id,
        })

    def action_add_amount_to_model_b(self):
        if self.petty_card and self.request_amount >= 0:
            self.petty_card.add_amount(self.request_amount)
        else:
            raise UserError("Please change your amount.")

    def action_pay(self):
        self.state = 'paid'
        self.action_add_amount_to_model_b()

    def action_reimburse(self):
        self.state = 'reimbursed'

    def action_to_draft(self):
        self.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('petty_code'):
                existing_requests = self.search([('petty_code', '=', vals.get('petty_code'))])
                if existing_requests:
                    raise ValidationError(_("A Petty Cash Request with this Petty Code already exists."))
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('petty.cash.request') or _('New')
        return super(PettyCashRequest, self).create(vals_list)

    def unlink(self):
        for record in self:
            if record.state == 'paid':
                raise UserError(_("You cannot delete a Petty Cash Request that is already paid."))
        return super(PettyCashRequest, self).unlink()
