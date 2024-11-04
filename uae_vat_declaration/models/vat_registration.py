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

    # basic_rate_supplies_emirate = fields.Selection([
    #     ('abu_dhabi', 'Abu Dhabi'),
    #     ('dubai', 'Dubai'),
    #     ('sharjah', 'Sharjah'),
    #     ('ajman', 'Ajman'),
    #     ('umm_al_quwain', 'Umm Al Quwain'),
    #     ('ras_al_khaimah', 'Ras Al Khaimah'),
    #     ('fujairah', 'Fujairah')
    # ], string='The supplies subject to the basic rate in', required=True)

    # basic_rate_supplies_emirate = fields.Many2one(
    #     'res.country.state',  
    #     string='Basic Rate Supplies Emirate',
    #     related='company_id.state_id',
    #     store=True)

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
    creation_date = fields.Date(string='Creation Date')


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


    # company_tax_id = fields.Many2one(
    #     'account.tax', 
    #     string='Company Tax',
    #     related='company_id.tax_id',
    #     readonly=True,
    #     store=True
    # )

    # @api.onchange('basic_rate_supplies_emirate')
    # def _onchange_basic_rate_supplies_emirate(self):
    #     emirate_tax_mapping = {
    #         'abu_dhabi': 'abu_dhabi_tax_id',
    #         'dubai': 'dubai_tax_id',
    #         'sharjah': 'sharjah_tax_id',
    #         'ajman': 'ajman_tax_id',
    #         'umm_al_quwain': 'umm_al_quwain_tax_id',
    #         'ras_al_khaimah': 'ras_al_khaimah_tax_id',
    #         'fujairah': 'fujairah_tax_id'
    #     }
        
    #     tax_external_id = emirate_tax_mapping.get(self.basic_rate_supplies_emirate)
    #     if tax_external_id:
    #         tax = self.env.ref(f'my_module.{tax_external_id}', raise_if_not_found=False)
    #         self.tax_id = tax if tax else False


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'

    # def _get_year_selection(self):
    #     current_year = datetime.now().year
    #     return [(str(year), str(year)) for year in range(current_year - 5, current_year + 6)]

    # year = fields.Selection(selection=_get_year_selection, string='Year', required=True)
    # date = fields.Date(string="Date",required=True)
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

    # @api.depends('vat_due_date_q1', 'vat_due_date_q2', 'vat_due_date_q3', 'vat_due_date_q4')
    # def _compute_due_date(self):
    #     for record in self:
    #         today = fields.Date.today()
            
    #         if today <= record.vat_due_date_q1:
    #             record.corporate_tax_due_date = record.vat_due_date_q2 - relativedelta(days=2)
    #         elif today <= record.vat_due_date_q2:
    #             record.corporate_tax_due_date = record.vat_due_date_q3 - relativedelta(days=2)
    #         elif today <= record.vat_due_date_q3:
    #             record.corporate_tax_due_date = record.vat_due_date_q4 - relativedelta(days=2)
    #         elif today <= record.vat_due_date_q4:
    #             record.corporate_tax_due_date = record.vat_due_date_q1 - relativedelta(days=2)
    #         else:
    #             record.corporate_tax_due_date = record.vat_due_date_q1 + relativedelta(years=1, days=-2)

    @api.depends('vat_due_date_q1', 'vat_due_date_q2', 'vat_due_date_q3', 'vat_due_date_q4')
    def _compute_due_date(self):
        today = fields.Date.today()
        for record in self:
            # تحقق من وجود تواريخ استحقاق صالحة
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
                # تعيين قيمة فارغة إذا كانت التواريخ غير صالحة
                record.corporate_tax_due_date = False



    # @api.onchange('date')
    # def _onchange_date(self):
    #     if self.date:
    #         date = int(self.date)
    #         self.vat_due_date_q1 = fields.Date.from_string(f'{date}-01-31')
    #         self.vat_due_date_q2 = fields.Date.from_string(f'{date}-04-30')
    #         self.vat_due_date_q3 = fields.Date.from_string(f'{date}-07-31')
    #         self.vat_due_date_q4 = fields.Date.from_string(f'{date}-10-31')
    #         self.corporate_tax_due_date = fields.Date.from_string(f'{date}-09-30')

    # @api.onchange('legal_name_english')
    # def _onchange_legal_name_english(self):
    #     if self.legal_name_english:
    #         emirate = 'dubai'  # Default to Dubai if no match is found
    #         name_lower = self.legal_name_english.lower()
    #         if 'abu dhabi' in name_lower:
    #             emirate = 'abu_dhabi'
    #         elif 'sharjah' in name_lower:
    #             emirate = 'sharjah'
    #         elif 'ajman' in name_lower:
    #             emirate = 'ajman'
    #         elif 'umm al quwain' in name_lower:
    #             emirate = 'umm_al_quwain'
    #         elif 'ras al khaimah' in name_lower:
    #             emirate = 'ras_al_khaimah'
    #         elif 'fujairah' in name_lower:
    #             emirate = 'fujairah'
    #         self.basic_rate_supplies_emirate = emirate

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

    # @api.constrains('legal_name_english')
    # def _check_legal_name_english(self):
    #     for record in self:
    #         if not re.match(r'^[A-Za-z\s]+$', record.legal_name_english):
    #             raise ValidationError("The Legal Name of Entity (English) must contain only English letters. Please modify the name.")

    # @api.constrains('legal_name_arabic')
    # def _check_legal_name_arabic(self):
    #     for record in self:
    #         if not re.match(r'^[\u0600-\u06FF\s]+$', record.legal_name_arabic):
    #             raise ValidationError("The Legal Name of Entity (Arabic) must contain only Arabic letters. Please modify the name.")


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

    # @api.depends('creation_date')
    # def _compute_due_date(self):
    #     for record in self:
    #         if record.creation_date:
    #             record.corporate_tax_due_date = record.creation_date + relativedelta(months=4, day=1) - relativedelta(days=1)
    # @api.depends('creation_date')
    # def _compute_vat_due_dates(self):
    #     for record in self:
    #         if record.creation_date:
    #             creation_date = fields.Date.from_string(record.creation_date)
                
    #             # تواريخ الاستحقاق لكل ربع
    #             vat_due_date_q1 = creation_date + relativedelta(months=3) - relativedelta(days=2)
    #             vat_due_date_q2 = creation_date + relativedelta(months=6) - relativedelta(days=2)
    #             vat_due_date_q3 = creation_date + relativedelta(months=9) - relativedelta(days=2)
    #             vat_due_date_q4 = creation_date + relativedelta(months=12) - relativedelta(days=2)

    #             # تحديث الحقول في السجل
    #             record.vat_due_date_q1 = vat_due_date_q1
    #             record.vat_due_date_q2 = vat_due_date_q2
    #             record.vat_due_date_q3 = vat_due_date_q3
    #             record.vat_due_date_q4 = vat_due_date_q4

    #             today = date.today()
    #             if today <= vat_due_date_q1:
    #                 record.corporate_tax_due_date = vat_due_date_q1
    #             elif today <= vat_due_date_q2:
    #                 record.corporate_tax_due_date = vat_due_date_q2
    #             elif today <= vat_due_date_q3:
    #                 record.corporate_tax_due_date = vat_due_date_q3
    #             elif today <= vat_due_date_q4:
    #                 record.corporate_tax_due_date = vat_due_date_q4
    #             else:
    #                 record.corporate_tax_due_date = vat_due_date_q1 + relativedelta(years=1)


#     @api.depends('creation_date')
#     def _compute_vat_due_dates(self):
#         for record in self:
#             if record.creation_date:
#                 creation_date = fields.Date.from_string(record.creation_date)
                
#                 # تواريخ الاستحقاق لكل ربع قبل نهاية الربع بيومين
#                 record.vat_due_date_q1 = (creation_date + relativedelta(months=3) - relativedelta(days=2))
#                 record.vat_due_date_q2 = (creation_date + relativedelta(months=6) - relativedelta(days=2))
#                 record.vat_due_date_q3 = (creation_date + relativedelta(months=9) - relativedelta(days=2))
#                 record.vat_due_date_q4 = (creation_date + relativedelta(months=12) - relativedelta(days=2))

#     @api.depends('last_vat_quarter')
#     def _compute_corporate_tax_due_date(self):
#         for record in self:
#             if record.last_vat_quarter:
#                 creation_date = fields.Date.from_string(record.creation_date) if record.creation_date else fields.Date.today()
# \
#                 if record.last_vat_quarter == 'q1':
#                     record.corporate_tax_due_date = creation_date + relativedelta(months=3) - relativedelta(days=2)
#                     record.last_vat_quarter = 'q2'
#                 elif record.last_vat_quarter == 'q2':
#                     record.corporate_tax_due_date = creation_date + relativedelta(months=6) - relativedelta(days=2)
#                     record.last_vat_quarter = 'q3'
#                 elif record.last_vat_quarter == 'q3':
#                     record.corporate_tax_due_date = creation_date + relativedelta(months=9) - relativedelta(days=2)
#                     record.last_vat_quarter = 'q4'
#                 elif record.last_vat_quarter == 'q4':
#                     record.corporate_tax_due_date = creation_date + relativedelta(months=12) - relativedelta(days=2)
#                     record.last_vat_quarter = 'q1'