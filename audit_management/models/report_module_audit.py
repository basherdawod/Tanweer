from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date

class AuditFinancialReport(models.Model):
    _name = "audit.financial.program"
    _description = "Audit Report"

    name = fields.Char(strring="Number" ,readonly=True, default=lambda self: _('New'), copy=False,
                      translate=True)
    level1 = fields.Char('Level 1', translate=True)
    level2 = fields.Char('Level 2', translate=True)
    level3 = fields.Char('Level 3 ', translate=True)

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

    type_line_L1_ids = fields.Many2many(
        comodel_name='account.type.level',
        relation='audit_financial_level1_rel',
        column1='audit_financial_id',
        column2='type_level_id',
        string='Level 1 Lines',
    )

    type_line_l2_ids = fields.Many2many(
        comodel_name='account.type.level',
        relation='audit_financial_level2_rel',
        column1='audit_financial_id',
        column2='type_level_id',
        string='Level 2 Lines',
    )

    type_line_l3_ids = fields.Many2many(
        comodel_name='account.type.level',
        relation='audit_financial_level3_rel',
        column1='audit_financial_id',
        column2='type_level_id',
        string='Level 3 Lines',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('audit.financial.program') or _('New')

        # records = self.with_context(skip_generate_lines=True).action_create_audit_line()
        
        records = super(AuditFinancialReport, self).create(vals_list)

        for record in records:
            try:
                record.action_create_audit_line()
                print ()
            except Exception as e:
                _logger.error(f"Error creating audit lines for record {record.id}: {e}")
                raise UserError(_("An error occurred while creating audit lines. Please contact the administrator."))

        return records
    #
    # def action_create_audit_line(self):
    #     # Collecting the audit line values to create
    #     self.write({
    #         'audit_lines_ids': [(5, 0, 0)]  # This clears all existing records in the field
    #     })
    #     line_vals = []
    #     total_balance_this_lival1 = 0.0
    #     total_balance_last_lival1  = 0.0
    #     total_balance_this_lival2 = 0.0
    #     total_balance_last_lival2  = 0.0
    #     total_balance_this_lival3 = 0.0
    #     total_balance_last_lival3  = 0.0
    #
    #
    #     for record in self:
    #         level_id1 = self.env['account.type.level'].search([('name', '=', record.level1)], limit=1)
    #         level_id2 = self.env['account.type.level'].search([('name', '=', record.level2)], limit=1)
    #         level_id3 = self.env['account.type.level'].search([('name', '=', record.level3)], limit=1)
    #         #
    #         if level_id1:  # Assuming level1 is a field, if not, adapt the code to your model
    #             line_vals.append({
    #                 'level_line_id': level_id1.id,  # Replace 'level1' with the correct field
    #             })
    #             # Add the lines associated with 'type_line_L1_ids'
    #             for line in record.type_line_L1_ids:
    #                 line_vals.append({
    #                     'level_line_id': line.id,
    #                 })
    #                 total_balance_this_lival1 += line.balance_this
    #                 total_balance_last_lival1 += line.balance_last
    #         else:
    #             li = self.env['account.type.level'].create({'name': record.level1,})
    #             line_vals.append({
    #                 'level_line_id': li.id,  # Replace 'level1' with the correct field
    #             })
    #             # Add the lines associated with 'type_line_L1_ids'
    #             for line in record.type_line_L1_ids:
    #                 line_vals.append({
    #                     'level_line_id': line.id,
    #                 })
    #                 total_balance_this_lival1 += line.balance_this
    #                 total_balance_last_lival1 += line.balance_last
    #                 #
    #         if level_id2:  # Assuming level1 is a field, if not, adapt the code to your model
    #             line_vals.append({
    #                 'level_line_id': level_id2.id,  # Replace 'level1' with the correct field
    #             })
    #             # Add the lines associated with 'type_line_L1_ids'
    #             for line in record.type_line_l2_ids:
    #                 line_vals.append({
    #                     'level_line_id': line.id,
    #                 })
    #                 total_balance_this_lival2 += line.balance_this
    #                 total_balance_last_lival2 += line.balance_last
    #         else:
    #             li = self.env['account.type.level'].create({'name': record.level2,})
    #             line_vals.append({
    #                 'level_line_id': li.id,  # Replace 'level1' with the correct field
    #             })
    #             # Add the lines associated with 'type_line_L1_ids'
    #             for line in record.type_line_l2_ids:
    #                 line_vals.append({
    #                     'level_line_id': line.id,
    #                 })
    #                 total_balance_this_lival2 += line.balance_this
    #                 total_balance_last_lival2 += line.balance_last
    #             #
    #         if level_id3:  # Assuming level1 is a field, if not, adapt the code to your model
    #             line_vals.append({
    #                 'level_line_id': level_id3.id,  # Replace 'level1' with the correct field
    #             })
    #             # Add the lines associated with 'type_line_L1_ids'
    #             for line in record.type_line_l3_ids:
    #                 line_vals.append({
    #                     'level_line_id': line.id,
    #                 })
    #                 total_balance_this_lival3 += line.balance_this
    #                 total_balance_last_lival3 += line.balance_last
    #         else:
    #             li = self.env['account.type.level'].create({'name': record.level3,})
    #             line_vals.append({
    #                 'level_line_id': li.id,  # Replace 'level1' with the correct field
    #             })
    #             # Add the lines associated with 'type_line_L1_ids'
    #             for line in record.type_line_l3_ids:
    #                 line_vals.append({
    #                     'level_line_id': line.id,
    #                 })
    #                 total_balance_this_lival3 += line.balance_this
    #                 total_balance_last_lival3 += line.balance_last
    #         self.write({
    #             'audit_lines_ids': [Command.create(vals) for vals in line_vals]
    #         })
    #         print ("Line 1 " ,  total_balance_this_lival1)
    #         print ("Line 1# " ,  total_balance_last_lival1)
    #         print ("Line 2 " ,  total_balance_this_lival2)
    #         print ("Line 2# " ,  total_balance_last_lival2)
    #         print ("Line 3 " ,  total_balance_this_lival3)
    #         print ("Line 3# " ,  total_balance_last_lival3)
    #         for line_id in record.audit_lines_ids:
    #             if line_id.level_line_id.name == record.level1:
    #                 line_id.level_line_id.write({
    #                     'balance_this': total_balance_this_lival1 ,
    #                     'balance_last': total_balance_last_lival1
    #                 })
    #             elif line_id.level_line_id.name == record.level2:
    #                 line_id.level_line_id.write({
    #                     'balance_this': total_balance_this_lival2,
    #                     'balance_last': total_balance_last_lival2
    #                 })
    #             elif line_id.level_line_id.name == record.level3:
    #                 line_id.level_line_id.write({
    #                     'balance_this': total_balance_this_lival3,
    #                     'balance_last': total_balance_last_lival3
    #                 })
    #
    def action_create_audit_line(self):
        # Clear existing audit lines
        self.write({
            'audit_lines_ids': [(5, 0, 0)]  # Clears all existing records in the field
        })

        line_vals = []
        total_balance_this_lival1 = 0.0
        total_balance_last_lival1 = 0.0
        total_balance_this_lival2 = 0.0
        total_balance_last_lival2 = 0.0
        total_balance_this_lival3 = 0.0
        total_balance_last_lival3 = 0.0

        for record in self:
            # Fetch or create level records
            level_id1 = self.env['account.type.level'].search([('name', '=', record.level1)], limit=1)
            if not level_id1:
                level_id1 = self.env['account.type.level'].create({'name': record.level1})

            level_id2 = self.env['account.type.level'].search([('name', '=', record.level2)], limit=1)
            if not level_id2:
                level_id2 = self.env['account.type.level'].create({'name': record.level2})

            level_id3 = self.env['account.type.level'].search([('name', '=', record.level3)], limit=1)
            if not level_id3:
                level_id3 = self.env['account.type.level'].create({'name': record.level3})

            # Add level lines for L1, L2, L3
            if level_id1:
                line_vals.append({'level_line_id': level_id1.id})
                for line in record.type_line_L1_ids:
                    line_vals.append({'level_line_id': line.id})
                    total_balance_this_lival1 += line.balance_this
                    total_balance_last_lival1 += line.balance_last

            if level_id2:
                line_vals.append({'level_line_id': level_id2.id})
                for line in record.type_line_l2_ids:
                    line_vals.append({'level_line_id': line.id})
                    total_balance_this_lival2 += line.balance_this
                    total_balance_last_lival2 += line.balance_last

            if level_id3:
                line_vals.append({'level_line_id': level_id3.id})
                for line in record.type_line_l3_ids:
                    line_vals.append({'level_line_id': line.id})
                    total_balance_this_lival3 += line.balance_this
                    total_balance_last_lival3 += line.balance_last

            # Write the new audit lines
            self.write({
                'audit_lines_ids': [Command.create(vals) for vals in line_vals]
            })
            level_id1.write({
                'total_balance_this': total_balance_this_lival1,
                'total_balance_last': total_balance_last_lival1
            })
            level_id2.write({
                'total_balance_this': total_balance_this_lival2,
                'total_balance_last': total_balance_last_lival2
            })
            level_id3.write({
                'total_balance_this': total_balance_this_lival3,
                'total_balance_last': total_balance_last_lival3
            })
# Separate models for each level
class AccountTypeLevelL1(models.Model):
    _name = 'account.type.level.l1'
    _description = 'Account Type Level for Level 1'

    record_id = fields.Many2one('account.type.level', string='Record')
    audit_financial_id = fields.Many2one('audit.financial.report', string='Audit Financial Program')


class AccountTypeLevelL2(models.Model):
    _name = 'account.type.level.l2'
    _description = 'Account Type Level for Level 2'

    record_id = fields.Many2one('account.type.level', string='Record')
    audit_financial_id = fields.Many2one('audit.financial.report', string='Audit Financial Program')


class AccountTypeLevelL3(models.Model):
    _name = 'account.type.level.l3'
    _description = 'Account Type Level for Level 3'

    record_id = fields.Many2one('account.type.level', string='Record')
    audit_financial_id = fields.Many2one('audit.financial.report', string='Audit Financial Program')



class AccountTypeLevel(models.Model):
    _name = 'account.audit.level.line'
    _description = 'Account Level Line'

    audit_financial_id = fields.Many2one(
        comodel_name='audit.financial.program',
        string='Account Type',
        required=False , readonly=True )

    level_line_id = fields.Many2one(
        comodel_name='account.type.level',
        string='Account Type',
        readonly=True,
        required=False)

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


