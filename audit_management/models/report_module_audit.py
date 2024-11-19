from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date

class AuditFinancialReport(models.Model):
    _name = "audit.financial.program"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Audit Report"

    name = fields.Char(strring="Number" ,readonly=True, default=lambda self: _('New'), copy=False,
                      translate=True)

    level1 = fields.Many2one('type.class.account' , 'Main Type',domain="[('id', '!=', level2),('id', '!=', level3)]")
    level2 = fields.Many2one('type.class.account' , 'Main Type' , domain="[('id', '!=', level1),('id', '!=', level2)]")
    level3 = fields.Many2one('type.class.account' , 'Main Type' , default=lambda self: self._get_default_level3(),  domain="[('id', '!=', level1),('id', '!=', level2)]")

    level_sub1 = fields.Many2one('type.class.line' , 'Main Sub' ,domain="[('type_class_id', '=', level1)]")
    level_sub2 = fields.Many2one('type.class.line' , 'Main Sub' ,domain="[('type_class_id', '=', level1)]")

    level2_sub1 = fields.Many2one('type.class.line' , 'Main Sub' , domain="[('type_class_id', '=', level2)]" )
    level2_sub2 = fields.Many2one('type.class.line' , 'Main Sub' , domain="[('type_class_id', '=', level2)]")

    # Assuming the relation is correct, the final code should look like this:

    audit_lines1_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        column2='level_sub1',
        string='Audit Lines',
        required=False,
        domain="[('type', '=', 'asset_current')]",
    )


    audit_lines2_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,
    )
    audit_lines3_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,
    )
    audit_lines4_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,
    )
    audit_lines5_ids = fields.One2many(
            comodel_name='account.type.level',
            inverse_name='audit_financial_id',
            string='Audit Lines',
            required=False,
        )

    partner_id = fields.Many2one('financial.audit.customer', string="Customer Registration")
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
    type_line1_L1_ids = fields.Many2many(
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
    type_line2_l2_ids = fields.Many2many(
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
    total_balance_this_lival1 = fields.Float(
        string='This Year',
        required=False,
    )
    total_balance_this_lival2 = fields.Float(
            string='This Year',
            required=False,
        )
    total_balance_this_lival3 = fields.Float(
            string='This Year',
            required=False,
        )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",

        required=True,
        default=lambda self: self.env.company.currency_id
    )

    total_balance_last_lival1 = fields.Monetary(
        string='Last Year',
        required=False,
        currency_field='currency_id',
    )
    total_balance_last_lival2 = fields.Monetary(
        string='Last Year',
        required=False,
        currency_field='currency_id',
    )
    total_balance_last_lival3 = fields.Monetary(
        string='Last Year',
        required=False,
        currency_field='currency_id',
    )

    @api.model
    def _get_default_level3(self):
        # Search for the record where name is 'Equity'
        equity_record = self.env['type.class.account'].search([('name', '=', 'Equity')], limit=1)
        if equity_record:
            return equity_record.id
        return False  # In case no record is found, return False to not set a default

    current_datetime = fields.Char(string="Current Date and Time", compute="_compute_current_datetime")
    #
    # @api.onchange('level1', 'level2', 'level3')
    # def _onchange_levels(self):
    #     domain = {}
    #     if self.level1:
    #         domain['level2'] = [('id', '!=', self.level1.id)]
    #     if self.level2:
    #         domain['level3'] = [('id', '!=', self.level2.id)]
    #     return {'domain': domain}

    def _compute_current_datetime(self):
        for record in self:
            record.current_datetime = fields.Datetime.now().strftime("%A, %d %B %Y")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('audit.financial.program') or _('New')

        # records = self.with_context(skip_generate_lines=True).action_create_audit_line()
        
        records = super(AuditFinancialReport, self).create(vals_list)

        return records


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
                line_vals.append({'display_type': 'line_section', 'name': record.level1, 'seq': '1'})
                num = 0
                line_type=[]
                # for line in record.type_line_L1_ids:
                #     label = line.type
                #     if label not in line_type:
                #         line_type.append(label)
                #         num +=1
                # print("###############", line_type , num)

                for line in record.type_line_L1_ids:
                    selection = line._fields['type'].selection
                    label = dict(selection).get(line.type, 'Unknown Type')

                    if label not in line_type:
                        line_type.append(label)
                        num +=1
                print("###############", line_type , num)
                # line_vals.append({'display_type': 'line_sub', 'name': line_type, 'seq': '1'})
                for i in range(num):
                    line_vals.append({'display_type': 'line_section', 'name': line_type[i], 'seq': '4'})
                    # line_vals.append({'level_line_id': level_id2.id})
                    for line in record.type_line_L1_ids:
                        selection = line._fields['type'].selection
                        label = dict(selection).get(line.type, 'Unknown Type')
                        if label == line_type[i]:
                            line_vals.append({'level_line_id': line.id})
                            total_balance_this_lival1 += line.balance_this
                            total_balance_last_lival1 += line.balance_last
                    i +=1

            if level_id2:
                line_vals.append({'display_type': 'line_section', 'name': record.level2, 'seq2': '2'})
                # line_vals.append({'level_line_id': level_id2.id})
                for line in record.type_line_l2_ids:
                    line_vals.append({'level_line_id': line.id})
                    total_balance_this_lival2 += line.balance_this
                    total_balance_last_lival2 += line.balance_last

            if level_id3:
                line_vals.append({'display_type': 'line_section', 'name': record.level1, 'seq3': '3'})
                # line_vals.append({'level_line_id': level_id3.id})
                for line in record.type_line_l3_ids:
                    line_vals.append({'level_line_id': line.id})
                    total_balance_this_lival3 += line.balance_this
                    total_balance_last_lival3 += line.balance_last

            # Write the new audit lines
            self.write({
                'audit_lines_ids': [Command.create(vals) for vals in line_vals]
            })

            level_id1.write ({
                'total_balance_this': total_balance_this_lival1,
                'total_balance_last': total_balance_last_lival1
            })
            level_id2.write ({
                'total_balance_this': total_balance_this_lival2,
                'total_balance_last': total_balance_last_lival2
            })
            level_id3.write ({
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
    name = fields.Char(string="Name")

    seq = fields.Integer(string="seq")
    seq2 = fields.Integer(string="seq")
    seq3 = fields.Integer(string="seq")

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_sub', "Sub Section "),
        ],
        default=False)

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
    level1_match = fields.Boolean(string="Level 1 Match", compute="_compute_level1_match")

    @api.depends('audit_financial_id', 'level_line_id')
    def _compute_level1_match(self):
        for record in self:
            # Ensure both fields are set before comparing
            if record.audit_financial_id.level1 == record.level_line_id.name:
                record.level1_match = True
            elif record.audit_financial_id.level2 == record.level_line_id.name:
                record.level1_match = True
            elif record.audit_financial_id.level3 == record.level_line_id.name:
                record.level1_match = True
            else:
                record.level1_match = False

    @api.depends('level_line_id')
    def _compute_name(self):
        for line in self:
            # If there's no 'level_line_id', assign a name based on audit_financial_id levels
            print("Line Fields:", dir(line))
            if not line.level_line_id:
                # Handle the case where audit_financial_id is not set
                if line.name !='' and line.seq == 1:
                    line.name = line.audit_financial_id.level1
                elif line.name !='' and line.seq2 == 2:
                    line.name = line.audit_financial_id.level2
                elif line.name !='' and line.seq3 == 3:
                    line.name = line.audit_financial_id.level3
                else:
                    print("Name",line.name )
                    line.name = "No line"
                continue  # Skip the next logic if no level_line_id


            # If 'level_line_id' is set, directly use its 'name' or 'type' (depending on the field you want)
            else:
                line.name =''  # or use line.level_line_id.type if that's more appropriate


class TypeClass(models.Model):
    _name = 'type.class.account'
    _description = 'Type Class'

    name = fields.Char("name")
    tec_name = fields.Char("Tech Name")

    type_line_ids = fields.One2many(
        comodel_name='type.class.line',
        inverse_name='type_class_id',
        string='Type line id',
        required=False)

class TypeClassLine(models.Model):
    _name = 'type.class.line'
    _description = 'Type Class Line'

    name = fields.Char("name")
    tec_name = fields.Char("Tech Name")
    type_class_id = fields.Many2one(
        comodel_name='type.class.account',
        string='Type class',
        required=False)
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


    @api.model
    def create(self, vals):
        if 'tec_name' in vals and not vals.get('type'):
            if vals['tec_name'] :
                vals['type'] = vals['tec_name']
        return super(TypeClassLine, self).create(vals)




