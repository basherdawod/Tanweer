import re
from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class VatRegistration(models.Model):
    _name = 'vat.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VAT Registration'
    _rec_name = 'trn'  

    trn = fields.Char(string='TRN', readonly=True, copy=False, default=lambda self: _('New'), unique=True)
    legal_name_english = fields.Char(string='Legal Name of Entity (English)',related='company_id.name')
    legal_name_arabic = fields.Char(string='Legal Name of Entity (Arabic)',related='company_id.name_ar')
    # st = fields.Char(string='State',related='company_id.state_id')
    tax_type = fields.Selection([
        ('vat', 'Vat'),
        ('corporate_tax', 'Corporate Tax')
    ], string='Tax Type', required=True)


    basic_rate_supplies_emirate = fields.Many2one(
        'res.country.state', 
        string='State', 
        domain="[('country_id.code', '=', 'AE')]"
    )

    reverse_charge_mechanism = fields.Boolean(string='Reverse Charge Mechanism Applicable')
    vat_due_date_q1 = fields.Date(string='VAT Due Date Q1', compute='_compute_vat_due_dates', store=True)
    vat_due_date_q2 = fields.Date(string='VAT Due Date Q2', compute='_compute_vat_due_dates', store=True)
    vat_due_date_q3 = fields.Date(string='VAT Due Date Q3', compute='_compute_vat_due_dates', store=True)
    vat_due_date_q4 = fields.Date(string='VAT Due Date Q4', compute='_compute_vat_due_dates', store=True)
    corporate_tax_due_date = fields.Date(string='Corporate Tax Due Date', compute='_compute_due_date', store=True)
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft')
    creation_date = fields.Date(string='Creation Date',required=True)


    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_vat = fields.Char(string='Company VAT', related='company_id.vat', store=True, readonly=True)



    
    tax_id = fields.Many2one('account.tax', string="Tax")

    @api.onchange('legal_name_english')
    def _onchange_legal_name_english(self):
        if self.legal_name_english:
            translator = Translator()
            try:
                translation = translator.translate(self.legal_name_english, dest='ar')
                self.legal_name_arabic = translation.text
            except Exception as e:
                self.legal_name_arabic = self.legal_name_english
                _logger.error(f"Translation failed: {e}")




    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'

    account_id = fields.Many2one('account.account',string="Account")

    

    @api.depends('creation_date')
    def _compute_vat_due_dates(self):
        for record in self:
            if record.creation_date:
                creation_date = fields.Date.from_string(record.creation_date)
                record.vat_due_date_q1 = creation_date
                record.vat_due_date_q2 = creation_date + relativedelta(months=3)
                record.vat_due_date_q3 = creation_date + relativedelta(months=6)
                record.vat_due_date_q4 = creation_date + relativedelta(months=9)

    @api.depends('vat_due_date_q1', 'vat_due_date_q2', 'vat_due_date_q3', 'vat_due_date_q4')
    def _compute_due_date(self):
        today = fields.Date.today()
        for record in self:
            if record.vat_due_date_q1 and record.vat_due_date_q2 and record.vat_due_date_q3 and record.vat_due_date_q4:
                if today <= record.vat_due_date_q1:
                    record.corporate_tax_due_date = record.vat_due_date_q2 - relativedelta(days=2)
                elif today <= record.vat_due_date_q2:
                    record.corporate_tax_due_date = record.vat_due_date_q3 - relativedelta(days=2)
                elif today <= record.vat_due_date_q3:
                    record.corporate_tax_due_date = record.vat_due_date_q4 - relativedelta(days=2)
                elif today <= record.vat_due_date_q4:
                    record.corporate_tax_due_date = record.vat_due_date_q1 - relativedelta(days=2)
                else:
                    record.corporate_tax_due_date = record.vat_due_date_q1 + relativedelta(years=1, days=-2)
            else:
                record.corporate_tax_due_date = False


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('trn', _('New')) == _('New'):
                vals['trn'] = self.env['ir.sequence'].next_by_code('vat.trn.sequence') or _('New')
        return super(VatRegistration, self).create(vals_list)

    @api.constrains('trn')
    def _check_trn_unique(self):
        for record in self:
            if self.search_count([('trn', '=', record.trn)]) > 1:
                raise ValidationError(_("This TRN already exists!"))


    @api.model
    def check_vat_due_dates(self):
        today = date.today()
        records = self.search([])

        for record in records:
            if (record.vat_due_date_q1 == today or
                record.vat_due_date_q2 == today or
                record.vat_due_date_q3 == today or
                record.vat_due_date_q4 == today):
                
                message = f"VAT Due Date {record.trn}."
                record.message_post(
                    body=message,
                    message_type='notification',
                    subtype_id=self.env.ref('mail.mt_note').id,
                    partner_ids=[self.env.user.partner_id.id]
                )
