# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging

class AuditItem(models.Model):
    _name = 'audit.item'
    _description = 'Audit Item'

    name = fields.Char(string='Number', readonly=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string=' Partner Name',
        required=True)
    period = fields.Date(
        string='Accounting Period',
        required=True)

    category = fields.Selection([
        ('financial', 'Financial Review'),
        ('operational', 'Operational Review'),
        ('compliance', 'Compliance Review'),
    ], string='Category', required=True)

    responsible_person = fields.Many2one('res.users', string='Prepared by')
    last_updated_by = fields.Many2one('res.users', string='Reviewed by')
    code = fields.Selection([
        ('F1', 'F1'), ('F2', 'F2'), ('GP', 'GP'), ('h_p_1', 'HP1'), ('h_p_2', 'HP2'), ('h_p_3', 'HP3'),
        ('h_p_4', 'HP4'),
        ('h_p_5', 'HP5'), ('i_p', 'IP'), ('j_p', 'JP'), ('l_p', 'LP'),
        ('MP', 'MP'), ('NP1', 'NP1'), ('NP2', 'NP2'), ('NP3', 'NP3'), ('OP', 'OP'), ('PP1', 'PP1'), ('PP2', 'PP2'),
        ('PP3', 'PP3'), ('QP1', 'QP1'), ('QP2', 'QP2'),
        ('RP1', 'RP1'), ('RP2', 'RP2'), ('RP3', 'RP3'), ('SP1', 'SP1'), ('SP2', 'SP2'), ('SP3', 'SP3'), ('SP4', 'SP4'),
        ('TP1', 'TP1'), ('TP2', 'TP2'), ('TP3', 'TP3'), ('UP1', 'UP1'),
        ('UP2', 'UP2'), ('UP3', 'UP3'), ('UP4', 'UP4'), ('UP5', 'UP5'), ('VP1', 'VP1'), ('VP2', 'VP2'), ('WP1', 'WP1'),
        ('WP2', 'WP2'), ('YP', 'YP'), ('XP', 'XP')], string='code')
    subject = fields.Selection(
        string='Subject',
        selection=[('gap', 'General Audit Procedures'), ('nlap', 'Nominal Ledger Audit Program'),
                   ('saop', 'Sales and operating income'), ('gaex', 'General and administrative expenses'),
                   ('coic', 'Costs in industrial companies'), ('purchases', 'Purchases'),
                   ('direct_costs', 'Direct costs'), ('salaries_wages', 'Salaries and wages'),
                   ('i_f_investments', 'Income from investments'), ('miscellaneous_revenues', 'Miscellaneous revenues'),
                   ('loans', 'Loans'), ('intangible_assets_goodwill', 'Intangible assets (goodwill - equity)'),
                   ('fixed_assets', 'Fixed assets'), ('establishment_expenses', 'Establishment expenses'),
                   ('Projects_under_implementation', 'Projects under implementation'),
                   ('related_parties', 'Related Parties'),
                   ('investments', 'Investments'),
                   ('i_a_related_companies', 'Investments in affiliated and related companies'),
                   ('stocks_mutual_funds', 'Investments in stocks and mutual funds'), ('stock', 'Stock'),
                   ('documentary_credits', 'Documentary credits'), ('trade_debtors', 'Trade debtors'),
                   ('provision_doubtful_debts', 'Provision for doubtful debts'),
                   ('advance_payment_suppliers', 'Advance Payment Suppliers'),
                   ('cash_in_hand_trust', 'Cash in hand and trust'), ('cash_in_banks', 'Cash in Banks'),
                   ('bank_deposits', 'Bank Deposits'), ('checks_under_collection', 'Checks under collection'),
                   ('accrued_expenses', 'Accrued Expenses'),
                   ('s_t_c_notes_payable', 'Suppliers, Trade Creditors and Notes Payable'),
                   ('r_r_a_from_customers', 'Revenue received in advance from customers'),
                   ('prepaid_expenses', 'prepaid expenses'),
                   ('other_debit_balances_m', 'Other Debit Balances - Miscellaneous Debtors'),
                   ('accrued_revenue', 'Accrued revenue'),
                   ('bounced_checks', 'Bounced checks'), ('third_party_insurance', 'Third party Insurance'),
                   ('allocations', 'Allocations'), ('miscellaneous_creditors', 'Miscellaneous Creditors'),
                   ('capital', 'Capital'), ('retained_earnings', 'Retained Earnings'),
                   ('contingent_liabilities_commitments', 'Contingent Liabilities and Contingent Commitments'),
                   ('subsequent_events', 'Subsequent events'),
                   ], required=False, readonly=True)

    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Status', default='pending')

    notes = fields.Text(string='Notes')

    date = fields.Date(string='Date')

    review_date = fields.Date(string='Date Review')


    audit_program_ids = fields.One2many(
        comodel_name='audit.program.line',
        inverse_name='audit',
        string='Audit_program_ids',
        required=False)

    program_audit_id = fields.One2many(
        comodel_name='audit.program',
        inverse_name='audit_id',
        string='Program',
        required=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('audit.item') or _('New')
        records = super(AuditItem, self).create(vals_list)

        # Execute program creation methods for each created record
        for record in records:
            record.action_create_program()
            record.action_create_program_line()
        return records

    def action_create_program(self):
        for record in self:
            # Retrieve all selection options for the 'code' field
            selection_options = self._fields['code'].selection or []
            selection_subj = self._fields['subject'].selection or []
            for option, subj in zip(selection_options, selection_subj):
                code_id = option[0]
                code_name = option[1]
                subj_id = subj[0]
                subj_name = subj[1]

                # Generate a unique program name for each code option
                program_name = f"{record.name}/{code_name}"
                # Create the program associated with this audit item
                program = self.env['audit.program'].create({
                    'name': program_name,
                    'partner_id': record.partner_id.id,
                    'period': record.period,
                    'prepared_by': record.responsible_person.id,
                    'code': code_id,
                    'subject': subj_id,
                    'audit_id': record.id,
                    'category': record.category,
                    'date': record.date,
                })

    def action_create_program_line(self):
        line_vals = []
        for record in self:
            # Create a line for each program in `program_audit_id`
            for program in record.program_audit_id:
                line_vals.append({
                    'program_audit': program.id,
                })
            record.write({
                'audit_program_ids': [Command.create(vals) for vals in line_vals]
            })

class AuditItemProgram(models.Model):
    _name = 'audit.program.line'
    _description = 'Audit Program Line'

    employee = fields.Many2one('res.users', string='Employee')

    audit = fields.Many2one(
        comodel_name='audit.item',
        string='Audit',
        required=False)

    program_audit = fields.Many2one(
        comodel_name='audit.program',
        string='Program',
        readonly=True)

    code = fields.Selection([
        ('F1', 'F1'), ('F2', 'F2'), ('GP', 'GP'), ('h_p_1', 'HP1'), ('h_p_2', 'HP2'), ('h_p_3', 'HP3'),
        ('h_p_4', 'HP4'),
        ('h_p_5', 'HP5'), ('i_p', 'IP'), ('j_p', 'JP'), ('l_p', 'LP'),
        ('MP', 'MP'), ('NP1', 'NP1'), ('NP2', 'NP2'), ('NP3', 'NP3'), ('OP', 'OP'), ('PP1', 'PP1'), ('PP2', 'PP2'),
        ('PP3', 'PP3'), ('QP1', 'QP1'), ('QP2', 'QP2'),
        ('RP1', 'RP1'), ('RP2', 'RP2'), ('RP3', 'RP3'), ('SP1', 'SP1'), ('SP2', 'SP2'), ('SP3', 'SP3'), ('SP4', 'SP4'),
        ('TP1', 'TP1'), ('TP2', 'TP2'), ('TP3', 'TP3'), ('UP1', 'UP1'),
        ('UP2', 'UP2'), ('UP3', 'UP3'), ('UP4', 'UP4'), ('UP5', 'UP5'), ('VP1', 'VP1'), ('VP2', 'VP2'), ('WP1', 'WP1'),
        ('WP2', 'WP2'), ('XP', 'YP')], string='code' , related="program_audit.code")
    subject = fields.Selection(
        string='Subject',
        selection=[('gap', 'General Audit Procedures'), ('nlap', 'Nominal Ledger Audit Program'),
                   ('saop', 'Sales and operating income'), ('gaex', 'General and administrative expenses'),
                   ('coic', 'Costs in industrial companies'), ('purchases', 'Purchases'),
                   ('direct_costs', 'Direct costs'), ('salaries_wages', 'Salaries and wages'),
                   ('i_f_investments', 'Income from investments'), ('miscellaneous_revenues', 'Miscellaneous revenues'),
                   ('loans', 'Loans'), ('intangible_assets_goodwill)', 'Intangible assets (goodwill - equity)'),
                   ('fixed_assets', 'Fixed assets'), ('establishment_expenses)', 'Establishment expenses'),
                   ('Projects_under_implementation', 'Projects under implementation'),
                   ('related_parties)', 'Related Parties'),
                   ('investments', 'Investments'),
                   ('i_a_related_companies)', 'Investments in affiliated and related companies'),
                   ('stocks_mutual_funds', 'Investments in stocks and mutual funds'), ('stock)', 'Stock'),
                   ('documentary_credits', 'Documentary credits'), ('trade_debtors)', 'Trade debtors'),
                   ('provision_doubtful_debts', 'Provision for doubtful debts'),
                   ('advance_payment_suppliers)', 'Advance Payment Suppliers'),
                   ('cash_in_hand_trust', 'Cash in hand and trust'), ('cash_in_banks)', 'Cash in Banks'),
                   ('bank_deposits', 'Bank Deposits'), ('checks_under_collection)', 'Checks under collection'),
                   ('accrued_expenses', 'Accrued Expenses'),
                   ('s_t_c_notes_payable)', 'Suppliers, Trade Creditors and Notes Payable'),
                   ('r_r_a_from_customers', 'Revenue received in advance from customers'),
                   ('prepaid_expenses)', 'prepaid expenses'),
                   ('other_debit_balances_m', 'Other Debit Balances - Miscellaneous Debtors'),
                   ('accrued_revenue)', 'Accrued revenue'),
                   ('bounced_checks', 'Bounced checks'), ('third_party_insurance)', 'Third party Insurance'),
                   ('allocations', 'Allocations'), ('miscellaneous_creditors)', 'Miscellaneous Creditors'),
                   ('capital', 'Capital'), ('retained_earnings)', 'Retained Earnings'),
                   ('contingent_liabilities_commitments', 'Contingent Liabilities and Contingent Commitments'),
                   ('subsequent_events)', 'Subsequent events'),
                   ], required=False , related="program_audit.subject")

    @api.onchange('employee')
    def onchange_method(self):
        for record in self.program_audit :
            record.work_performed_by = self.employee.id
