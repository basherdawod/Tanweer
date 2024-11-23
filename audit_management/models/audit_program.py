# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging

class AuditProgram(models.Model):
    _name = 'audit.program'
    _description = 'Audit Program'

    name = fields.Char(string='Audit Program Name')
    code = fields.Selection([
        ('F1', 'F1'), ('F2', 'F2'), ('GP', 'GP'), ('h_p_1', 'HP1'), ('h_p_2', 'HP2'), ('h_p_3', 'HP3'),
        ('h_p_4', 'HP4'),
        ('h_p_5', 'HP5'), ('i_p', 'IP'), ('j_p', 'JP'), ('l_p', 'LP'),
        ('MP', 'MP'), ('NP1', 'NP1'), ('NP2', 'NP2'), ('NP3', 'NP3'), ('OP', 'OP'), ('PP1', 'PP1'), ('PP2', 'PP2'),
        ('PP3', 'PP3'), ('QP1', 'QP1'), ('QP2', 'QP2'),
        ('RP1', 'RP1'), ('RP2', 'RP2'), ('RP3', 'RP3'), ('SP1', 'SP1'), ('SP2', 'SP2'), ('SP3', 'SP3'), ('SP4', 'SP4'),
        ('TP1', 'TP1'), ('TP2', 'TP2'), ('TP3', 'TP3'), ('UP1', 'UP1'),
        ('UP2', 'UP2'), ('UP3', 'UP3'), ('UP4', 'UP4'), ('UP5', 'UP5'), ('VP1', 'VP1'), ('VP2', 'VP2'), ('WP1', 'WP1'),
        ('WP2', 'WP2'), ('YP', 'YP'),('XP', 'XP')], string='code')


    date = fields.Date(string='Date')
    review_date = fields.Date(string='Date Review')
    category = fields.Selection([
        ('financial', 'Financial Review'),
        ('operational', 'Operational Review'),
        ('compliance', 'Compliance Review'),
    ], string='Category', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ], string='Status', default='pending')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string=' Partner Name',
        required=True)
    period = fields.Date(
        string='Accounting Period',
        required=True)
    subject = fields.Selection(
        string='Subject',
        selection=[('gap', 'General Audit Procedures'),('nlap', 'Nominal Ledger Audit Program'),
                   ('saop', 'Sales and operating income'),('gaex', 'General and administrative expenses'),
                   ('coic', 'Costs in industrial companies'),('purchases', 'Purchases'),
                   ('direct_costs', 'Direct costs'),('salaries_wages', 'Salaries and wages'),
                   ('i_f_investments', 'Income from investments'),('miscellaneous_revenues', 'Miscellaneous revenues'),
                   ('loans', 'Loans'),('intangible_assets_goodwill', 'Intangible assets (goodwill - equity)'),
                   ('fixed_assets', 'Fixed assets'),('establishment_expenses', 'Establishment expenses'),
                   ('Projects_under_implementation', 'Projects under implementation'),('related_parties', 'Related Parties'),
                   ('investments', 'Investments'),('i_a_related_companies', 'Investments in affiliated and related companies'),
                   ('stocks_mutual_funds', 'Investments in stocks and mutual funds'),('stock', 'Stock'),
                   ('documentary_credits', 'Documentary credits'),('trade_debtors', 'Trade debtors'),
                   ('provision_doubtful_debts', 'Provision for doubtful debts'),('advance_payment_suppliers', 'Advance Payment Suppliers'),
                   ('cash_in_hand_trust', 'Cash in hand and trust'),('cash_in_banks', 'Cash in Banks'),
                   ('bank_deposits', 'Bank Deposits'),('checks_under_collection', 'Checks under collection'),
                   ('accrued_expenses', 'Accrued Expenses'),('s_t_c_notes_payable', 'Suppliers, Trade Creditors and Notes Payable'),
                   ('r_r_a_from_customers', 'Revenue received in advance from customers'),('prepaid_expenses', 'prepaid expenses'),
                   ('other_debit_balances_m', 'Other Debit Balances - Miscellaneous Debtors'),('accrued_revenue', 'Accrued revenue'),
                   ('bounced_checks', 'Bounced checks'),('third_party_insurance', 'Third party Insurance'),
                   ('allocations', 'Allocations'),('miscellaneous_creditors', 'Miscellaneous Creditors'),
                   ('capital', 'Capital'),('retained_earnings', 'Retained Earnings'),
                   ('contingent_liabilities_commitments', 'Contingent Liabilities and Contingent Commitments'),('subsequent_events', 'Subsequent events'),
                   ],required=False ,readonly=True )

    prepared_by = fields.Many2one('res.users', string='Prepared By')
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    audit_id = fields.Many2one('audit.item', string='Audit')

    objective_accuracy = fields.Char(string="(A)" ,default="Accuracy and precision of amounts" , readonly=True)
    objective_presentation = fields.Char(string="(P)" ,default="Proper presentation and disclosure" , readonly=True)
    objective_completion = fields.Char(string="(C)" ,default="Completion of recording all amounts in books" , readonly=True)
    objective_existence = fields.Char(string="(E)" ,default="Existence" , readonly=True)
    objective_ownership = fields.Char(string="(O)"  ,default="Ownership" , readonly=True)
    objective_valuation = fields.Char(string="(V)" , default="Proper Valuation" , readonly=True)

    financial_statements_payroll = fields.Char(string="(A)" ,default="The charge in the financial statements for payroll and pensions costs is correct and properly disclosed." , readonly=True)
    preparation_of_payroll_current = fields.Char(string="(B)" ,default="The data used in preparation of the payroll is current and authorised." , readonly=True)
    payroll_correctly_calculated = fields.Char(string="(C)" ,default="The payroll is correctly calculated." , readonly=True)
    payroll_correctly_account = fields.Char(string="(D)" ,default="The payroll is correctly accounted for." , readonly=True)
    payment_salaries_controlled = fields.Char(string="(E)"  ,default="Payment of wages/salaries (by cash, cheque, or credit transfer) is controlled" , readonly=True)
    payment_recorded_nominal_account = fields.Char(string="(F)" , default="Payment of wages/salaries recorded in nominal accounts are genuine" , readonly=True)
    payment_correctly_entered_acc = fields.Char(string="(G)" , default="Payments are correctly entered in the accounting records." , readonly=True)

    credit_received_related = fields.Char(string="(A)" ,default="Invoices/credit notes received and related Value Added Tax are completely and correctly entered in the accounting records." , readonly=True)
    received_all_good = fields.Char(string="(B)" ,default="Invoices are received for all goods and services received." , readonly=True)
    purchase_other_invoices = fields.Char(string="(C)" ,default="Purchase and other expense invoices/credit notes are correct." , readonly=True)
    purchase_other_recorded = fields.Char(string="(D)" ,default="Purchases and other expenses recorded in nominal accounts are genuine." , readonly=True)
    payment_correctly_entered = fields.Char(string="(E)"  ,default="Payments are correctly entered in the accounting records." , readonly=True)

    investment_gains_losses = fields.Char(string="(A)" ,default="Investment gains and losses have been accurately calculated." , readonly=True)
    investment_gains_losses_recorded = fields.Char(string="(B)"  ,default="Investment gains and losses are recorded clearly, accurately and consistently from year to year." , readonly=True)


    test_description = fields.Text(string='Test Description')
    reference = fields.Char(string='Reference')
    work_performed_by = fields.Many2one('res.users', string='Work Performed By')
    result = fields.Text(string='Result and Conclusion')
    program_test_ids = fields.One2many(
        comodel_name='program.line.test',
        inverse_name='program_test',
        string='Program_test_ids',
        required=False)
    preliminary_inherent = fields.Char(
        string='Preliminary Inherent',
        required=False)
    final_inherent = fields.Char(
        string='Final Inherent',
        required=False)
    preliminary_control = fields.Char(
            string='Preliminary Control',
            required=False)
    final_control = fields.Char(
        string='Final Control',
        required=False)

    @api.model
    def create(self, values):
        # Add code here
        return

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AuditProgram, self).create(vals_list)
        # Execute program creation methods for each created record
        for record in records:
            record.action_create_audit_program_line()
        return records


    @api.model
    def get_action_audit_program(self):
        # Check if any records exist for `audit_id` and set default
        default_audit_id = self.search([], limit=1).id or False
        action = self.env.ref('audit_management.action_audit_program').read()[0]
        if default_audit_id:
            action['context'] = {'search_default_audit_id': default_audit_id}
        return action

    def action_create_audit_program_line(self):
        for record in self:
            line_vals = []
            # Use search to get records
            program_lines = self.env['program.line'].search([('subject', '=', record.subject)])
            for program in program_lines:
                line_vals.append({
                    'program_line_id': program.id,
                })
            # Use Command.create to create the related records
            record.write({
                'program_test_ids': [Command.create(vals) for vals in line_vals]
            })


class ProgramLineTest(models.Model):
    _name = 'program.line.test'
    _description = 'Program Line Test'

    objectives = fields.Char(string="Objectives")
    reference = fields.Char(string="Reference")
    work_p = fields.Many2one('res.users', string='Work Performed By' , related="program_test.work_performed_by")
    program_test = fields.Many2one('audit.program', string='Audit Program' )
    notes = fields.Text(string='Result and Conclusion')

    number = fields.Integer(
        string='Test No.',
        required=False ,related="program_line_id.number")
    program_line_id = fields.Many2one("program.line", string="Program Line")
    name = fields.Text(
        string="Audit test - Nature, Timing and Extent",
        compute="_compute_name_discription",
        store=True  # Set store=True if you want to save the computed value
    )

    @api.depends('program_line_id.discription_english', 'program_line_id.discription_arabic')
    def _compute_name_discription(self):
        for record in self:
            english_text = record.program_line_id.discription_english or ""
            arabic_text = record.program_line_id.discription_arabic or ""
            # Using \n for line breaks in text fields
            record.name = f"{english_text}\n{arabic_text}"


class Auditaccountprogramreport(models.Model):
    _name = 'audit.account.program.report'
    _description = 'audit.account.program.report'

    name = fields.Char()

