# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging

_logger = logging.getLogger(__name__)

class PreExpTestModel(models.Model):
    _name = 'pre.exp.test.model'
    _description = 'Prepaid Expense Test Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, readonly=True, copy=False, default=lambda self: _('New'), tracking=True)
    default_date = fields.Date(string='Default Date', default=fields.Date.context_today, required=True, tracking=True)
    account_id = fields.Many2one('account.account', string='Prepaid Expense Account', tracking=True, required=True,
                                 domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    expense_account_id = fields.Many2one('account.account', string='Expense Account', tracking=True, required=True,
                                         domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    account_number = fields.Char(string='Account Number', related='account_id.code', readonly=True)
    category_id = fields.Many2one('pre.exp.test.category', string='Category', tracking=True, required=True)
    contract_start_date = fields.Date(string='Contract Start Date', tracking=True, required=True)
    contract_end_date = fields.Date(string='Contract End Date', tracking=True)
    method_period = fields.Integer(string='Period (months)', default=1, tracking=True, required=True)
    contract_amount = fields.Monetary(string='Contract Amount', tracking=True, required=True)
    contract_fees_amount = fields.Monetary(string='Contract Fees Amount', tracking=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    remaining_days = fields.Integer(string='Remaining Days', compute='_compute_remaining_days', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    #month_remaining_amount = fields.Monetary(string='Month Remaining Amount', compute='_compute_month_remaining_amount', store=True)
    journal_entry_ids = fields.One2many('account.move', 'prepaid_expense_id', string='Journal Entries')
    report_ids = fields.One2many('pre.exp.test.report', 'expense_id', string='Reports')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('computed', 'Computed'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('validate', 'Validated'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    line_ids = fields.One2many('pre.exp.test.line', 'expense_id', string='Expense Lines')

    @api.depends('account_id')
    def _compute_account_number(self):
        for record in self:
            record.account_number = record.account_id.code if record.account_id else ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('pre.exp.test.sequence') or _('New')
        return super(PreExpTestModel, self).create(vals_list)

    @api.depends('contract_amount', 'contract_fees_amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.contract_amount + record.contract_fees_amount

    @api.depends('contract_start_date', 'contract_end_date')
    def _compute_remaining_days(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.contract_start_date and record.contract_end_date:
                if record.contract_end_date > today:
                    end_of_month = record.contract_start_date + relativedelta(day=31)
                    record.remaining_days = max((end_of_month - today).days, 0)
                else:
                    record.remaining_days = 0
            else:
                record.remaining_days = 0

    #@api.depends('total_amount', 'line_ids.amount')
    #def _compute_month_remaining_amount(self):
        #for record in self:
            #expensed_amount = sum(record.line_ids.mapped('amount'))
            #record.month_remaining_amount = record.total_amount - expensed_amount

    @api.onchange('category_id')
    def _onchange_category(self):
        if self.category_id:
            self.account_id = self.category_id.prepaid_account_id
            self.expense_account_id = self.category_id.expense_account_id
            self.method_period = self.category_id.method_period

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft records can be confirmed."))
            record.write({'state': 'confirm'})
        return True

    def action_compute(self):
        for record in self:
            if record.state != 'confirm':
                raise UserError(_("Only confirmed records can be computed."))
            
            if not record.contract_start_date or not record.method_period:
                raise UserError(_("Contract start date and period must be set before computing."))

            record._compute_total_amount()
            record.line_ids.unlink()

            current_date = record.contract_start_date
            end_date = record.contract_end_date
            total_days = (end_date - current_date).days + 1
            if total_days <= 0:
                raise UserError(_("The contract end date must be after the start date."))

            daily_amount = record.total_amount / total_days

            line_vals = []
            while current_date <= end_date:
                next_date = min(current_date + relativedelta(months=1, day=1) - relativedelta(days=1), end_date)
                days_in_period = (next_date - current_date).days + 1
                amount = daily_amount * days_in_period

                line_vals.append({
                    'name': f"Expense from {current_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}",
                    'date': next_date,
                    'days': days_in_period,
                    'amount': amount,
                    'debit': 0.0,
                    'credit': amount,
                    'account_id': record.expense_account_id.id,
                })

                current_date = next_date + relativedelta(days=1)

            record.write({
                'state': 'computed',
                'line_ids': [Command.create(vals) for vals in line_vals]
            })
        return True
 
    def action_to_approve(self):
        for record in self:
            if record.state != 'computed':
                raise UserError(_("Only computed records can be submitted for approval."))
            record.write({'state': 'to_approve'})
        return True

    def action_approve(self):
        for record in self:
            record.state = 'approved'
        return True

    def action_validate(self):
        for record in self:
            if record.state != 'approved':
                raise UserError(_("Only approved records can be validated."))
            record.write({'state': 'validate'})
        return True

    def action_done(self):
        for record in self:
            if record.state != 'validate':
                raise UserError(_("Only validated records can be marked as done."))
            record.write({'state': 'done'})
        return True

    def action_draft(self):
        for record in self:
            if record.state in ['done', 'cancel']:
                record.write({'state': 'draft'})
            else:
                raise UserError(_("Only done or cancelled records can be reset to draft."))
        return True

    def action_cancel(self):
        for record in self:
            if record.state not in ['done', 'cancel']:
                record.write({'state': 'cancel'})
            else:
                raise UserError(_("Done or already cancelled records cannot be cancelled."))
        return True

    # def action_post_journal_entries(self):
    #     for record in self:
    #         move_lines = []
    #         for line in record.line_ids:
    #             move_lines.append(Command.create({
    #                 'name': f"Prepaid Expense - {line.name}",
    #                 'account_id': record.account_id.id,
    #                 'debit': 0.0,
    #                 'credit': line.amount,
    #             }))
                
    #             move_lines.append(Command.create({
    #                 'name': f"Expense Recognition - {line.name}",
    #                 'account_id': record.expense_account_id.id,
    #                 'debit': line.amount,
    #                 'credit': 0.0,
    #             }))



    #         journal_entry = self.env['account.move'].create({
    #             'date': fields.Date.today(),
    #             'ref': f"Prepaid Expense - {record.name}",
    #             'line_ids': move_lines,
    #             'prepaid_expense_id': record.id,
    #         })

    #         try:
    #             journal_entry.action_post()
    #         except Exception as e:
    #             raise UserError(_("Error posting journal entry: %s") % str(e))

    #         record.write({
    #             'state': 'validate',
    #             'journal_entry_ids': [(4, journal_entry.id)]
    #         })

    #     return True


    def action_generate_report(self):
        self.ensure_one()
        return self.env.ref('pre_exp_testa.action_report_prepaid_expense').report_action(self)


    @api.model
    def pre_exp_cron_job_method(self):
        today = fields.Date.today()
        records = self.search([('line_ids.date', '=', today)])

        for record in records:
            move_lines = []
            for line in record.line_ids:
                if line.date == today:
                    move_lines.append(Command.create({
                        'name': f"Prepaid Expense - {line.name}",
                        'account_id': record.account_id.id,
                        'debit': 0.0,
                        'credit': line.amount,
                    }))
                
                    move_lines.append(Command.create({
                        'name': f"Expense Recognition - {line.name}",
                        'account_id': record.expense_account_id.id,
                        'debit': line.amount,
                        'credit': 0.0,
                    }))

            if move_lines:
                journal_entry = self.env['account.move'].create({
                    'date': today,
                    'ref': f"Prepaid Expense - {record.name}",
                    'line_ids': move_lines,
                    'prepaid_expense_id': record.id,
                })

                try:
                    journal_entry.action_post()
                except Exception as e:
                    raise UserError(_("Error posting journal entry: %s") % str(e))

                record.write({
                    'state': 'validate',
                    'journal_entry_ids': [(4, journal_entry.id)]
                })

                _logger.info(f"Journal entry posted successfully for record {record.id}")

        return True


class PreExpTestReport(models.Model):
    _name = 'pre.exp.test.report'
    _description = 'Prepaid Expense Report'

    expense_id = fields.Many2one('pre.exp.test.model', string='Prepaid Expense', required=True, ondelete='cascade')
    date = fields.Date(string='Report Date', default=fields.Date.context_today)
    category_id = fields.Many2one('pre.exp.test.category', string='Category', related='expense_id.category_id', readonly=True, store=True)
    amount = fields.Monetary(string='Amount', related='expense_id.total_amount', readonly=True, store=True)
    debit = fields.Monetary(string='Debit', compute='_compute_debit_credit', store=True)
    credit = fields.Monetary(string='Credit', compute='_compute_debit_credit', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='expense_id.currency_id', readonly=True, store=True)
   

    @api.depends('expense_id', 'expense_id.line_ids')
    def _compute_debit_credit(self):
        for record in self:
            record.debit = sum(record.expense_id.line_ids.mapped('debit'))
            record.credit = sum(record.expense_id.line_ids.mapped('credit'))

    @api.onchange('expense_id')
    def _onchange_expense_id(self):
        if self.expense_id:
            self.date = fields.Date.today()

class PreExpTestLine(models.Model):
    _name = 'pre.exp.test.line'
    _description = 'Prepaid Expense Test Line'

    expense_id = fields.Many2one('pre.exp.test.model', string='Prepaid Expense', ondelete='cascade')
    name = fields.Char(string='Description')
    date = fields.Date(string='Date')
    days = fields.Integer(string='Days', help="Number of days in this expense period")
    amount = fields.Monetary(string='Amount')
    debit = fields.Monetary(string='Debit', default=0.0)
    credit = fields.Monetary(string='Credit', default=0.0)
    account_id = fields.Many2one('account.account', string='Account')
    month_remaining_amount = fields.Monetary(string='Month Remaining Amount', compute='_compute_month_remaining_amount', store=True)
    move_id = fields.Many2one('account.move', string='Journal Entry')
    company_id = fields.Many2one('res.company', related='expense_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='expense_id.currency_id', store=True, readonly=True)

    @api.depends('expense_id.total_amount', 'amount')
    def _compute_month_remaining_amount(self):
        for record in self:
            previous_lines = record.expense_id.line_ids.filtered(lambda r: r.date <= record.date)
            expensed_amount = sum(previous_lines.mapped('amount'))
            record.month_remaining_amount = record.expense_id.total_amount - expensed_amount

class AccountMove(models.Model):
    _inherit = 'account.move'

    prepaid_expense_id = fields.Many2one('pre.exp.test.model', string='Prepaid Expense')


    

class PreExpTestModelOld(models.Model):
    _name = 'pre.exp.test.model.old'
    _description = 'Prepaid Expense Test Model (Old)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, readonly=True, copy=False, default=lambda self: _('New'), tracking=True)
    default_date = fields.Date(string='Default Date', default=fields.Date.context_today, required=True, tracking=True)
    # journal_id = fields.Many2one('account.journal', string='Journal', required=True, tracking=True)
    prepaid_account_id = fields.Many2one('account.account', string='Prepaid Account', related='category_id.prepaid_account_id', readonly=True, store=True)
    account_id = fields.Many2one('account.account', string='Account', tracking=True)
    account_number = fields.Char(string='Account Number', tracking=True)
    category_id = fields.Many2one('pre.exp.test.category', string='Category', tracking=True, required=True)
    contract_start_date = fields.Date(string='Contract Start Date', tracking=True)
    contract_end_date = fields.Date(string='Contract End Date', tracking=True)
    method_period = fields.Integer(string='Period (months)', default=1, tracking=True)
    contract_amount = fields.Monetary(string='Contract Amount', tracking=True)
    contract_fees_amount = fields.Monetary(string='Contract Fees Amount', tracking=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    remaining_days = fields.Integer(string='Remaining Days', compute='_compute_remaining_days', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    journal_entry_ids = fields.One2many('account.move', 'prepaid_expense_id', string='Journal Entries')
    report_ids = fields.One2many('pre.exp.test.report', 'expense_id', string='Reports')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('computed', 'Computed'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('validate', 'Validated'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    line_ids = fields.One2many('pre.exp.test.line', 'expense_id', string='Expense Lines')
    report_id = fields.Many2one('ir.attachment', string='Report', readonly=True)

    @api.onchange('category_id', 'journal_id')
    def _onchange_category_journal(self):
        if self.category_id:
            self.method_period = self.category_id.method_period
            if self.category_id.journal_id:
                self.journal_id = self.category_id.journal_id
            if self.category_id.prepaid_account_id:
                self.account_id = self.category_id.prepaid_account_id
        if self.journal_id and not self.account_id:
            self.account_id = self.journal_id.default_account_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('pre.exp.test.sequence.old') or _('New')
        return super(PreExpTestModelOld, self).create(vals_list)

    @api.depends('contract_amount', 'contract_fees_amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.contract_amount + record.contract_fees_amount

    @api.depends('contract_start_date', 'contract_end_date')
    def _compute_remaining_days(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.contract_start_date and record.contract_end_date:
                if record.contract_end_date > today:
                    end_of_month = record.contract_start_date + relativedelta(day=31)
                    record.remaining_days = max((end_of_month - today).days, 0)
                else:
                    record.remaining_days = 0
            else:
                record.remaining_days = 0

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft records can be confirmed."))
            record.write({'state': 'confirm'})
        return True

    def action_compute(self):
        for record in self:
            if record.state != 'confirm':
                raise UserError(_("Only confirmed records can be computed."))
            
            if not record.contract_start_date or not record.method_period:
                raise UserError(_("Contract start date and period must be set before computing."))

            try:
                record.contract_end_date = record.contract_start_date + relativedelta(months=record.method_period)
            except ValueError as e:
                raise UserError(_("Error in date calculation: %s. Please check the contract start date and period.") % str(e))

            record._compute_total_amount()
            record.line_ids.unlink()

            current_date = record.contract_start_date
            end_date = record.contract_end_date
            total_days = (end_date - current_date).days + 1
            if total_days <= 0:
                raise UserError(_("The contract end date must be after the start date."))

            daily_amount = record.total_amount / total_days

            line_vals = []
            while current_date <= end_date:
                next_date = min(current_date + relativedelta(months=1, day=1) - relativedelta(days=1), end_date)
                days_in_period = (next_date - current_date).days + 1
                amount = daily_amount * days_in_period

                line_vals.append({
                    'name': f"Expense from {current_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}",
                    'date': next_date,
                    'days': days_in_period,
                    'amount': amount,
                    'debit': 0.0,
                    'credit': amount,
                    'account_id': record.account_id.id,
                })

                current_date = next_date + relativedelta(days=1)

            record.write({
                'state': 'computed',
                'line_ids': [Command.create(vals) for vals in line_vals]
            })
        return True   
        
    def action_to_approve(self):
        for record in self:
            if record.state != 'computed':
                raise UserError(_("Only computed records can be submitted for approval."))
            record.write({'state': 'to_approve'})
        return True

    def action_validate(self):
        for record in self:
            if record.state != 'approved':
                raise UserError(_("Only approved records can be validated."))
            record.write({'state': 'validate'})
        return True

    def action_done(self):
        for record in self:
            if record.state != 'validate':
                raise UserError(_("Only validated records can be marked as done."))
            record.write({'state': 'done'})
        return True

    def action_draft(self):
        for record in self:
            if record.state in ['done', 'cancel']:
                record.write({'state': 'draft'})
            else:
                raise UserError(_("Only done or cancelled records can be reset to draft."))
        return True

    def action_cancel(self):
        for record in self:
            if record.state not in ['done', 'cancel']:
                record.write({'state': 'cancel'})
            else:
                raise UserError(_("Done or already cancelled records cannot be cancelled."))
        return True
            
       

    def action_post_journal_entries(self):
        for record in self:
            move_lines = []
            for line in record.line_ids:
                move_lines.append(Command.create({
                    'name': f"Prepaid Expense - {line.name}",
                    'account_id': record.account_id.id,
                    'debit': line.amount,
                    'credit': 0.0,
                }))
                
                move_lines.append(Command.create({
                    'name': f"Payment for {line.name}",
                    'account_id': record.journal_id.default_account_id.id,
                    'debit': 0.0,
                    'credit': line.amount,
                }))

            journal_entry = self.env['account.move'].create({
                'journal_id': record.journal_id.id,
                'date': fields.Date.today(),
                'ref': f"Prepaid Expense - {record.name}",
                'line_ids': move_lines,
                'prepaid_expense_id': record.id,
            })

            try:
                journal_entry.action_post()
            except Exception as e:
                raise UserError(_("Error posting journal entry: %s") % str(e))

    def action_generate_report(self):
        self.ensure_one()
        return self.env.ref('pre_exp_testa.action_report_prepaid_expense_old').report_action(self)