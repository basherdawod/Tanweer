# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging

class ProgramLine(models.Model):
    _name = 'program.line'
    _description = 'Program.line'
    _rec_name = 'subject'

    number = fields.Integer(
        string='Number',
        required=False)
    discription_arabic = fields.Text(
        string=" Description Arabic",
        required=False)
    discription_english = fields.Text(
        string=" Description English",
        required=False)

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