from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
from datetime import datetime, date

import qrcode
from io import BytesIO

class AuditFinancialReport(models.Model):
    _name = "audit.financial.program"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Audit Report"

    name = fields.Char(strring="Number" ,readonly=True, default=lambda self: _('New'), copy=False,
                      translate=True)

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',  # Default status is 'draft'
        string='Status',
    )

    level1 = fields.Many2one('type.class.account' , 'Main Type',domain="[('id', '!=', level2),('id', '!=', level3)]")
    level2 = fields.Many2one('type.class.account' , 'Main Type' , domain="[('id', '!=', level1),('id', '!=', level2)]")
    level3 = fields.Many2one('type.class.account' , 'Main Type' , default=lambda self: self._get_default_level3(),  domain="[('id', '!=', level1),('id', '!=', level2)]")

    level_sub1 = fields.Many2one('type.class.line' , 'Main Sub' ,domain="[('type_class_id', '=', level1)]")

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
    level_sub2 = fields.Many2one('type.class.line' , 'Main Sub' ,domain="[('type_class_id', '=', level1)]")
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
    level2_sub1 = fields.Many2one('type.class.line' , 'Main Sub' , domain="[('type_class_id', '=', level2)]" )
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
    level2_sub2 = fields.Many2one('type.class.line' , 'Main Sub' , domain="[('type_class_id', '=', level2)]")
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
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,domain=lambda self: [('type', '=', self.type1)]
    )


    audit_lines2_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,domain=lambda self: [('type', '=', self.type2)]
    )
    audit_lines3_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,domain=lambda self: [('type', '=', self.type3)]
    )
    audit_lines4_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False,domain=lambda self: [('type', '=', self.type4)]
    )
    audit_lines5_ids = fields.One2many(
            comodel_name='account.type.level',
            inverse_name='audit_financial_id',
            string='Audit Lines',
            required=False,domain=lambda self: [('type', '=', self.type5)]
        )
    level3_sub1 = fields.Many2one('type.class.line', 'Main Sub', default=lambda self: self._get_default_level4())
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
    #########        QR Code
    qr_code_data = fields.Char(string='QR Code Data', compute='_compute_qr_code_image')

    def _compute_qr_code_image(self):
        for record in self:
            qr = qrcode.QRCode()
            qr.add_data(record.name)  # Replace with your QR code data
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            record.qr_code_data = base64.b64encode(buffer.getvalue())
    #########

    #########    Page Number
    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['audit.financial.program'].browse(docids)
        # Example logic for pages (simplify as per your use case)
        pages = []
        for i, doc in enumerate(docs, 1):
            pages.append({
                'current_number': i,
                'total_pages': len(docs),
                'doc': doc,
            })
        return self.env.ref('audit_management.report_audit_audit_financial_template').render({
            'docs': pages
        })

    ########
    def reset_to_draft(self):
        self.status='draft'

    def set_confirm(self):
        self.status = 'confirm'
        self.action_create_audit_line()

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
                vals['name'] = self.env['ir.sequence'].next_by_code('audit.financial.program') or _('New')
        records = super(AuditFinancialReport, self).create(vals_list)
        return records


    def action_create_program(self):
        self.audit_lines1_ids.unlink()
        self.audit_lines2_ids.unlink()
        self.audit_lines3_ids.unlink()
        self.audit_lines4_ids.unlink()
        self.audit_lines5_ids.unlink()
        for record in self:
            level_id1 = self.env['account.type.level'].search([('type', '=', record.type1)])
            level_id2 = self.env['account.type.level'].search([('type', '=', record.type2)])
            level_id3 = self.env['account.type.level'].search([('type', '=', record.type3)])
            level_id4 = self.env['account.type.level'].search([('type', '=', record.type4)])
            level_id5 = self.env['account.type.level'].search([('type', '=', record.type5)])
            value_leval2 = []  # Initialize an empty list to hold the created records
            value_leval3 = []  # Initialize an empty list to hold the created records
            value_leval4 = []  # Initialize an empty list to hold the created records
            value_leval5 = []  # Initialize an empty list to hold the created records
            value_leval1 = []  # Initialize the list for storing the created record IDs
            for line_level_id1 in level_id1:
                if line_level_id1.audit_financial_id.id != record.id:
                    new_record = self.env['account.type.level'].create({
                        'name': line_level_id1.name,
                        'audit_financial_id': record.id,
                        'type': line_level_id1.type,
                    })
                    value_leval1.append(new_record.id)
            for line_level_id2 in  level_id2:
                if line_level_id2.audit_financial_id.id != record.id:
                    new_record = self.env['account.type.level'].create({
                        'name': line_level_id2.name,
                        'audit_financial_id': record.id,
                        'type': line_level_id2.type,
                    })
                    value_leval2.append(new_record.id)
            for line_level_id3 in level_id3:
                if line_level_id3.audit_financial_id.id != record.id:
                    new_record = self.env['account.type.level'].create({
                        'name': line_level_id3.name,
                        'audit_financial_id': record.id,
                        'type': line_level_id3.type,
                    })
                    value_leval3.append(new_record.id)
            for line_level_id4 in  level_id4:
                if line_level_id4.audit_financial_id.id != record.id:
                    new_record = self.env['account.type.level'].create({
                        'name': line_level_id4.name,
                        'audit_financial_id': record.id,
                        'type': line_level_id4.type,
                    })
                    value_leval4.append(new_record.id)
            for line_level_id5 in level_id5:
                if line_level_id5.audit_financial_id.id != record.id:
                    new_record = self.env['account.type.level'].create({
                        'name': line_level_id5.name,
                        'audit_financial_id': record.id,
                        'type': line_level_id5.type,
                    })
                    value_leval5.append(new_record.id)

            self.write({
                'audit_lines1_ids': value_leval1 ,
                'audit_lines2_ids': value_leval2 ,
                'audit_lines3_ids': value_leval3 ,
                'audit_lines4_ids': value_leval4 ,
                'audit_lines5_ids': value_leval5 ,
            })



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
            level_id1 = self.env['account.type.level'].search([('name', '=', f"{'Total'} {record.level1.name}"),('audit_financial_id', '=', record.id)], limit=1)
            if not level_id1:
                level_id1 = self.env['account.type.level'].create({'name': f"{'Total'} {record.level1.name}" , 'audit_financial_id': record.id})

            level_id2 = self.env['account.type.level'].search([('name', '=', f"{'Total'} {record.level2.name}"),('audit_financial_id', '=', record.id)], limit=1)
            if not level_id2:
                level_id2 = self.env['account.type.level'].create({'name': f"{'Total'} {record.level2.name}" , 'audit_financial_id': record.id})

            level_id3 = self.env['account.type.level'].search([('name', '=', f"{'Total'} {record.level3.name}"),('audit_financial_id', '=', record.id)], limit=1)
            if not level_id3:
                level_id3 = self.env['account.type.level'].create({'name': f"{'Total'} {record.level3.name}" , 'audit_financial_id': record.id})

            level = self.env['account.type.level'].search([('audit_financial_id', '=', record.id)])
            if level:
    # Leval1 add line
                if record.level1:
                    line_vals.append({'display_type': 'line_section', 'name': record.level1.name, 'seq': '1'})
                    line_vals.append({'level_line_id': level_id1.id})
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
                if record.level2:
                    line_vals.append({'display_type': 'line_section', 'name': record.level2.name, 'seq': '2'})
                    line_vals.append({'level_line_id': level_id2.id})
                    if record.level2_sub1:
                        line_vals.append({'display_type': 'line_section', 'name': record.level2_sub1.name, 'seq': '4'})
                        for line in level:
                            if line.type == record.type3:
                                line_vals.append({'level_line_id': line.id})
                                total_balance_this_lival2 += line.balance_this
                                total_balance_last_lival2 += line.balance_last
                    if record.level2_sub2:
                        line_vals.append({'display_type': 'line_section', 'name': record.level2_sub2.name, 'seq': '4'})
                        for line in level:
                            if line.type == record.type4:
                                line_vals.append({'level_line_id': line.id})
                                total_balance_this_lival1 += line.balance_this
                                total_balance_last_lival1 += line.balance_last
    # Leval3 add line
                if record.level3:
                    line_vals.append({'display_type': 'line_section', 'name': record.level3.name, 'seq': '3'})
                    line_vals.append({'level_line_id': level_id3.id})
                    if record.level3_sub1:
                        for line in level:
                            if line.type == record.type5:
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
    audit_financial_id = fields.Many2one('audit.financial.program', string='Audit Financial Program')



class AccountTypeLevelL2(models.Model):
    _name = 'account.type.level.l2'
    _description = 'Account Type Level for Level 2'

    record_id = fields.Many2one('account.type.level', string='Record')
    audit_financial_id = fields.Many2one('audit.financial.program', string='Audit Financial Program')


class AccountTypeLevelL3(models.Model):
    _name = 'account.type.level.l3'
    _description = 'Account Type Level for Level 3'

    record_id = fields.Many2one('account.type.level', string='Record')
    audit_financial_id = fields.Many2one('audit.financial.program', string='Audit Financial Program')



class AccountTypeLevel(models.Model):
    _name = 'account.audit.level.line'
    _description = 'Account Level Line'
    _order = 'audit_financial_id, sequence, id'

    audit_financial_id = fields.Many2one(
        comodel_name='audit.financial.program',
        string='Account Type',
        required=False , readonly=True )
    sequence = fields.Integer(string="Sequence", default=10)

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

    @api.depends('level_line_id')
    def _compute_name(self):
        for line in self:
            # If there's no 'level_line_id', assign a name based on audit_financial_id levels
            print("Line Fields:", dir(line))
            if not line.level_line_id:
                # Handle the case where audit_financial_id is not set
                if line.name !='' and line.seq == 1:
                    line.name = line.audit_financial_id.level1.name
                elif line.name !='' and line.seq2 == 2:
                    line.name = line.audit_financial_id.level2.name
                elif line.name !='' and line.seq3 == 3:
                    line.name = line.audit_financial_id.level3.name
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



