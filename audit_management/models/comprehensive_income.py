from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date

class ComprehensiveIncome(models.Model):
    _name = "comprehensive.income"
    _description = "Comprehensive Income"

    name = fields.Char(strring="Number" ,readonly=True, default=lambda self: _('New'), copy=False,
                      translate=True)


    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        string='Status',
    )
    financial_id = fields.Many2one('financial.audit.customer', string="Financial Report")
    comprehensive_income_ids = fields.Many2one("account.type.level")

    level_sub1 = fields.Many2one('type.line.class' , 'Comprehensive Income',
                domain="[('id', '!=', level_sub2),('id', '!=', level2_sub1),('id', '!=', level2_sub2),('id', '!=', level3_sub1)]"
                                 )
    audit_report = fields.Char(string="Audit Sequence")
    type1 = fields.Selection(
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
        related="level_sub1.type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )
    level_sub2 = fields.Many2one('type.line.class' , 'Comprehensive Income',
                domain="[('id', '!=', level_sub1),('id', '!=', level2_sub1),('id', '!=', level2_sub2),('id', '!=', level3_sub1)]")
    type2 = fields.Selection(
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
        related="level_sub2.type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )
    level2_sub1 = fields.Many2one('type.line.class' , 'Comprehensive Income',
                domain="[('id', '!=', level_sub1),('id', '!=', level2_sub2),('id', '!=', level_sub2),('id', '!=', level3_sub1)]")
    type3 = fields.Selection(
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
        related="level2_sub1.type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )
    level2_sub2 = fields.Many2one('type.line.class' , 'Comprehensive Income' ,
                                  domain="[('id', '!=', level_sub1),('id', '!=', level2_sub1),('id', '!=', level_sub2),('id', '!=', level3_sub1)]")
    type4 = fields.Selection(
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
        related="level2_sub2.type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )

    audit_lines1_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='comprehensive_income_id',
        string='Audit Lines',
        required=False,
        domain = lambda self: [('type', '=', self.type1)]
    )
    audit_lines2_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='comprehensive_income_id',
        string='Audit Lines',
        required=False,
        domain=lambda self: [('type', '=', self.type2)]
    )
    audit_lines3_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='comprehensive_income_id',
        string='Audit Lines',
        required=False,
        domain=lambda self: [('type', '=', self.type3)]
    )
    audit_lines4_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='comprehensive_income_id',
        string='Audit Lines',
        required=False,
        domain=lambda self: [('type', '=', self.type4)]
    )
    audit_lines5_ids = fields.One2many(
            comodel_name='account.type.level',
            inverse_name='comprehensive_income_id',
            string='Audit Lines',
            required=False,
        domain=lambda self: [('type', '=', self.type5)]
        )
    level3_sub1 = fields.Many2one('type.line.class', 'Comprehensive Income',
                                  domain="[('id', '!=', level_sub1),('id', '!=', level2_sub1),('id', '!=', level_sub2),('id', '!=', level2_sub2)]")
    type5 = fields.Selection(
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
        related="level3_sub1.type",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
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


    comprehensive_income_line_ids = fields.One2many('comprehensive.income.line','comprehensive_income_id',string="Comprehensive Income Line")
    audit_lines_ids = fields.One2many(
        comodel_name='account.audit.line.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False
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

    @api.model
    def _get_default_level4(self):
        # Search for the record where name is 'Equity'
        equity_record = self.env['type.class.line'].search([('name', '=', 'Equity')], limit=1)
        if equity_record:
            return equity_record.id
        return False  # In case no record is found, return False to not set a default

    current_datetime = fields.Char(string="Current Date and Time", compute="_compute_current_datetime")

    def _compute_current_datetime(self):
        for record in self:
            record.current_datetime = fields.Datetime.now().strftime("%A, %d %B %Y")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('comprehensive.income') or _('New')
        records = super(ComprehensiveIncome, self).create(vals_list)
        return records


    def action_create_audit_line(self):
        # Clear existing audit lines
        self.write({
            'audit_lines_ids': [(5, 0, 0)]  # Clears all existing records in the field
        })

        line_vals = []
        total_balance_this_lival1 = 0.0
        total_balance_last_lival1 = 0.0
        # total_balance_this_lival2 = 0.0
        # total_balance_last_lival2 = 0.0
        # total_balance_this_lival3 = 0.0
        # total_balance_last_lival3 = 0.0

        for record in self:
            # Fetch or create level records
            level = self.env['account.type.level'].search([('comprehensive_income_id', '=', record.id)])
            if level:
    # Leval1 add line
                if record.level_sub1:
                    line_vals.append({'display_type': 'line_section', 'name': record.level_sub1.name, 'seq': '4'})
                    for line in level:
                        if line.type == record.type1:
                            line_vals.append({'level_line_id': line.id})
                            total_balance_this_lival1 += line.balance_this
                            total_balance_last_lival1 += line.balance_last
                if record.level_sub2:
                    line_vals.append({'display_type': 'line_section', 'name': record.level_sub2.name, 'seq': '4'})
                    for line in level:
                        if line.type == record.type2:
                            line_vals.append({'level_line_id': line.id})
                            total_balance_this_lival1 += line.balance_this
                            total_balance_last_lival1 += line.balance_last
    # Leval2 add line
                if record.level2_sub1:
                    line_vals.append({'display_type': 'line_section', 'name': record.level2_sub1.name, 'seq': '4'})
                    for line in level:
                        if line.type == record.type3:
                            line_vals.append({'level_line_id': line.id})
                            total_balance_this_lival1 += line.balance_this
                            total_balance_last_lival1 += line.balance_last
                if record.level2_sub2:
                    line_vals.append({'display_type': 'line_section', 'name': record.level2_sub2.name, 'seq': '4'})
                    for line in level:
                        if line.type == record.type4:
                            line_vals.append({'level_line_id': line.id})
                            total_balance_this_lival1 += line.balance_this
                            total_balance_last_lival1 += line.balance_last
    # Leval3 add line
                if record.level3_sub1:
                    line_vals.append({'display_type': 'line_section', 'name': record.level3_sub1.name, 'seq': '4'})
                    for line in level:
                        if line.type == record.type5:
                            line_vals.append({'level_line_id': line.id})
                            total_balance_this_lival1 += line.balance_this
                            total_balance_last_lival1 += line.balance_last



            # Write the new audit lines
            self.write({
                'audit_lines_ids': [Command.create(vals) for vals in line_vals]
            })

class ClassType(models.Model):
    _name = 'type.account.class'
    _description = 'Class Type'

    name = fields.Char("name")
    tec_name = fields.Char("Tech Name")

    type_line_ids = fields.One2many(
        comodel_name='type.line.class',
        inverse_name='type_class_id',
        string='Type line id',
        required=False)

class TypeLineClass(models.Model):
    _name = 'type.line.class' #model_type_line_class
    _description = 'Type Line Class'

    name = fields.Char("name")
    tec_name = fields.Char("Tech Name")
    type_class_id = fields.Many2one(
        comodel_name='type.account.class',
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
        # related = "type_class_id.tec_name",
        help="These types are defined according to your country. The type contains more information " \
             "about the account and its specificities."
    )

    @api.model
    def create(self, vals):
        if 'tec_name' in vals and not vals.get('type'):
            if vals['tec_name'] :
                vals['type'] = vals['tec_name']
        return super(TypeLineClass, self).create(vals)




class ComprehensiveIncomeLine(models.Model):
    _name = 'comprehensive.income.line' #model_comprehensive_income_line
    _description = 'Comprehensive Income Line'


    code = fields.Char(string="Code")
    account_name = fields.Char(string="Account Name")
    total_last_year = fields.Float(string="Total Last Year")
    total_this_year = fields.Float(string="Total This Year")
    comprehensive_income_id = fields.Many2one('comprehensive.income','comprehensive_income_line_ids')
    financial_line_id = fields.Many2one('financial.audit.customer', string="Financial Report")

