from odoo import models, fields, Command, api , _
from odoo.exceptions import UserError, ValidationError


class PettyCashPayment(models.Model):
    _name = 'petty.cash.payment'
    _description = 'Petty Cash Payment'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    petty_code = fields.Char(string='Pettych', required=True, copy=False, readonly=True)
    user_approval = fields.Many2one('res.users', string="User Approval ", required=True)
    employee_petty = fields.Many2one('hr.employee', string="Employee", required=True)
    employee_request = fields.Many2one('petty.cash.request', string="Employee Request")
    employee_submission = fields.Many2one('petty.cash.submission', string="Employee submission")
    account_id = fields.Many2one(string=" Account " , comodel_name='account.account',
        store=True, readonly=False,
        domain="[('account_type', 'in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card')), ('company_id', '=', company_id)]",
    )
    account_receive = fields.Many2one(
        comodel_name='account.account',
        string="Account Receive",
        store=True, readonly=False,
        domain="[('account_type', 'in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card')), ('company_id', '=', company_id)]",
        help="An petty cash account is receive",
    )
    account_code = fields.Char(string="Account Code", compute="_compute_account_code", store=True)
    payment_type = fields.Selection([('send', 'Send'), ('receive', 'Receive')], string="Payment Type", required=True)
    amount = fields.Monetary(string="Amount", required=True)
    payment_date = fields.Date(string="Payment Date", default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Status', readonly=True, default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True , default=lambda self: self.env.ref('base.AED'))

    @api.depends('account_id')
    def _compute_account_code(self):
        for rec in self:
            rec.account_code = rec.account_id.code if rec.account_id else ''

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('petty.cash.payment') or _('New')
        result = super(PettyCashPayment, self).create(vals)
        return result

    def confirm_payment(self):
        if self.payment_type == 'receive':
            self.validate_request_payment()
        else:
            self.action_approve_submission()
        self.state = 'confirm'

    def validate_payment(self):
        self.state = 'done'


    def validate_request_payment(self):
        self.ensure_one()
        self.state = 'done'
        cash_account = self.env['account.account'].search([('id', '=', self.account_receive.id)], limit=1)
        expense_account = self.env['account.account'].search([('id', '=', self.account_id.id)], limit=1)
        if self.payment_type == 'receive':
            debit_account = expense_account.id
            credit_account = cash_account.id
        else:
            debit_account = cash_account.id
            credit_account = expense_account.id

        move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('name', '=', 'petty cash')], limit=1).id,
            'date': self.payment_date,
            'line_ids': [
                (0, 0, {
                    'account_id': debit_account,
                    # 'partner_id': self.partner_id,  # Add the partner only if available
                    'name': self.name,
                    'debit': self.amount,
                    'currency_id': self.currency_id.id,
                }),
                (0, 0, {
                    'account_id': credit_account,
                    'name': self.name,
                    'credit': self.amount,
                    'currency_id': self.currency_id.id,
                }),
            ]
        })
        # Post the move
        move.action_post()
        for rec in self :
            rec.employee_request.action_pay()


    def action_approve_submission(self):
        self.ensure_one()
        self.state = 'done'

        cash_account = self.env['account.account'].search([('id', '=', self.account_id.id)], limit=1)

        if self.payment_type == 'send':
            account = cash_account.id

        move_line = []

        for record in self.employee_submission.expense_details:
            # Append Debit Line
            move_line.append(Command.create({
                'account_id': account,
                'name': record.description,
                'credit': record.amount,
                'ref': record.reference,
                'currency_id': self.currency_id.id,
            }))

            # Append Credit Line
            move_line.append(Command.create({
                'account_id':record.account.id ,
                'name': record.description,
                'ref': record.reference,
                'debit': record.amount,
                'currency_id': self.currency_id.id,
            }))

        # Create the accounting move
        move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('name', '=', 'petty cash')], limit=1).id,
            'date': self.payment_date,
            'line_ids': move_line
        })
        # Post the move
        move.action_post()

