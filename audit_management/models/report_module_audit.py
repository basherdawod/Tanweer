from odoo import api, fields, models, _
from datetime import date, datetime

class AuditFinancialReport(models.Model):
    _name = "audit.financial.program"
    _description = "Audit Report"

    name = fields.Char('Report Name', translate=True)

    leval1 = fields.Many2one(
        comodel_name='type.level.audit',
        string='Leval 1',
        required=False)
    leval2 = fields.Many2one(
        comodel_name='type.level.audit',
        string='Leval 2',
        required=False)
    leval3 = fields.Many2one(
        comodel_name='type.level.audit',
        string='Leval 3',
        required=False)
    type_line_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False)
    audit_lines2_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False)
    audit_lines3_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False)

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
    leval_type = fields.Many2one(
        comodel_name='leval_type',
        string='Level Type',
        required=False)
    audit_lines_ids = fields.One2many(
        comodel_name='account.type.level',
        inverse_name='audit_financial_id',
        string='Audit Lines',
        required=False)


class AccountTypeLevel(models.Model):
    _name = 'account.type.level'
    _description = 'Account Type Level'

    name = fields.Char(
        string='Name',
        required=False)
    account_level_type_ids = fields.One2many(
        comodel_name='type.account',
        inverse_name='level_id',
        string='Account Level Type IDs',
        required=False)
    audit_financial_id = fields.Many2one(
        comodel_name='audit.financial.program',
        string='Audit Financial Program')


class AccountTypeLevel(models.Model):
    _name = 'type.level.audit'
    _description = 'Type Level'

    name = fields.Char(
        string='Name',
        required=False)
    lavel_name = fields.Char(
        string='Lavel_name', 
        required=False)


class TypeAccount(models.Model):
    _name = 'type.account'
    _description = 'Type Of Account'

    name = fields.Char(
        string='Name',
        required=False)
    level_id = fields.Many2one(
        comodel_name='account.type.level',
        string='Level')
    type_line_ids = fields.One2many(
        comodel_name='type.account.line',
        inverse_name='type_account_id',
        string='Type Line IDs',
        required=False)


class TypeAccountLine(models.Model):
    _name = 'type.account.line'
    _description = 'Type Of Account Line'

    type_account_id = fields.Many2one(
        comodel_name='type.account',
        string='Type Account ID',
        required=False)
    name = fields.Char(
        string='Name',
        required=False)
