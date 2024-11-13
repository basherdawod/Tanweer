from odoo import models, fields, Command, api , _
from odoo.exceptions import UserError, ValidationError


class PettyCashPayment(models.Model):
    _name = 'petty.cash.payment'
    _description = 'Petty Cash Payment'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    user_approval = fields.Many2one('res.users', string="User Approval ", required=True)
    employee_petty = fields.Many2one('hr.employee', string="Employee", required=True)
    employee_request = fields.Many2one('petty.cash.request', string="Employee Request")
    employee_card = fields.Many2one('petty.cash.card', string="Employee Card")

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

    # total_send = fields.Monetary(string="Total Send", compute="_compute_totals",store=True)
    # total_receive = fields.Monetary(string="Total Receive", compute="_compute_totals",store=True)

    # @api.depends('amount')
    # def _compute_totals(self):
    #     for record in self:
    #         send_records = record.amount.filtered(lambda r: r.payment_type == 'send')
    #         receive_records = record.amount.filtered(lambda r: r.payment_type == 'receive')
    #         record.total_send = sum(send_records.mapped('amount'))
    #         record.total_receive = sum(receive_records.mapped('amount'))

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

        # Ensure accounts exist
        cash_account = self.env['account.account'].search([('id', '=', self.account_receive.id)], limit=1)
        expense_account = self.env['account.account'].search([('id', '=', self.account_id.id)], limit=1)
        if not cash_account or not expense_account:
            raise ValueError("Cash or expense account not found. Please verify the accounts.")

        # Determine debit and credit accounts based on payment type
        if self.payment_type == 'receive':
            debit_account = expense_account.id
            credit_account = cash_account.id
        else:
            debit_account = cash_account.id
            credit_account = expense_account.id

        # Retrieve petty cash journal
        petty_cash_journal = self.env['account.journal'].search([('name', '=', 'petty cash')], limit=1)
        if not petty_cash_journal:
            raise ValueError("Petty Cash journal not found. Please ensure it exists.")

        # Create the journal entry
        move = self.env['account.move'].create({
            'journal_id': petty_cash_journal.id,
            'date': self.payment_date,
            'company_id':self.company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': debit_account,
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
        # Update related employee request state
        for rec in self:
            rec.employee_request.action_pay()


    def action_approve_submission(self):
        self.ensure_one()
        self.state = 'done'

        cash_account = self.env['account.account'].search([('id', '=', self.account_id.id)], limit=1)

        if not cash_account or cash_account.company_id != self.env.user.company_id:
            raise UserError("The cash account must belong to the current user's company.")

        if self.payment_type == 'send':
            account = cash_account.id

        move_line = []
        total_amount = 0.0

        for record in self.employee_submission.expense_details:
            # Ensure account compatibility
            if record.account.company_id != self.env.user.company_id:
                raise UserError(f"The account '{record.account.name}' must belong to the current user's company.")

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
                'account_id': record.account.id,
                'name': record.description,
                'ref': record.reference,
                'debit': record.amount,
                'currency_id': self.currency_id.id,
            }))
            total_amount += record.amount

        # Create the accounting move
        move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('name', '=', 'petty cash')], limit=1).id,
            'date': self.payment_date,
            'line_ids': move_line,
            'company_id': self.env.user.company_id.id,  # Ensure the move is linked to the user's company
        })

        # Post the move and handle exceptions
        try:
            move.action_post()
        except Exception as e:
            raise UserError(f"Failed to post accounting move: {e}")


        for card in self.employee_card:
            if card.open_balance is not None:
                card.open_balance -= total_amount  # Ensure consistent balance updates
            else:
                raise UserError("The field 'open_balance' is missing in the model.")