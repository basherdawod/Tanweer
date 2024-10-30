from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class VatRegistration(models.Model):
    _name = 'vat.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VAT Registration'
    _rec_name = 'trn'  

    trn = fields.Char(string='TRN', readonly=True, copy=False, default=lambda self: _('New'), unique=True)
    legal_name_english = fields.Char(string='Legal Name of Entity (English)', required=True)
    legal_name_arabic = fields.Char(string='Legal Name of Entity (Arabic)', required=True)
    tax_type = fields.Selection([
        ('vat', 'Vat'),
        ('corporate_tax', 'Corporate Tax')
    ], string='Tax Type', required=True)

    basic_rate_supplies_emirate = fields.Selection([
        ('abu_dhabi', 'Abu Dhabi'),
        ('dubai', 'Dubai'),
        ('sharjah', 'Sharjah'),
        ('ajman', 'Ajman'),
        ('umm_al_quwain', 'Umm Al Quwain'),
        ('ras_al_khaimah', 'Ras Al Khaimah'),
        ('fujairah', 'Fujairah')
    ], string='The supplies subject to the basic rate in', required=True)

    reverse_charge_mechanism = fields.Boolean(string='Reverse Charge Mechanism Applicable')
    vat_due_date_q1 = fields.Date(string='VAT Due Date Q1')
    vat_due_date_q2 = fields.Date(string='VAT Due Date Q2')
    vat_due_date_q3 = fields.Date(string='VAT Due Date Q3')
    vat_due_date_q4 = fields.Date(string='VAT Due Date Q4')
    corporate_tax_due_date = fields.Date(string='Corporate Tax Due Date')
    
    def _get_year_selection(self):
        current_year = datetime.now().year
        return [(str(year), str(year)) for year in range(current_year - 5, current_year + 6)]

    year = fields.Selection(selection=_get_year_selection, string='Year', required=True)

    @api.onchange('year')
    def _onchange_year(self):
        if self.year:
            year = int(self.year)
            self.vat_due_date_q1 = fields.Date.from_string(f'{year}-01-31')
            self.vat_due_date_q2 = fields.Date.from_string(f'{year}-04-30')
            self.vat_due_date_q3 = fields.Date.from_string(f'{year}-07-31')
            self.vat_due_date_q4 = fields.Date.from_string(f'{year}-10-31')
            self.corporate_tax_due_date = fields.Date.from_string(f'{year}-09-30')

    @api.onchange('legal_name_english')
    def _onchange_legal_name_english(self):
        if self.legal_name_english:
            emirate = 'dubai'  # Default to Dubai if no match is found
            name_lower = self.legal_name_english.lower()
            if 'abu dhabi' in name_lower:
                emirate = 'abu_dhabi'
            elif 'sharjah' in name_lower:
                emirate = 'sharjah'
            elif 'ajman' in name_lower:
                emirate = 'ajman'
            elif 'umm al quwain' in name_lower:
                emirate = 'umm_al_quwain'
            elif 'ras al khaimah' in name_lower:
                emirate = 'ras_al_khaimah'
            elif 'fujairah' in name_lower:
                emirate = 'fujairah'
            self.basic_rate_supplies_emirate = emirate

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