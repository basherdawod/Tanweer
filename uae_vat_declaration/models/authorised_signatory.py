import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class authorised_signatory(models.Model):
    _name = 'authorised.signatory' #model_authorised_signatory
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Authorised Signatory'
    _rec_name = 'name_english'

    name_english = fields.Char(string='Name of Entity (English)', required=True)
    name_arabic = fields.Char(string='Name of Entity (Arabic)', required=True)
    mobile_country_code = fields.Char(string='Mobile Country Code', required=True)
    mobile_number = fields.Char(string="Mobile Number", required=True)
    email = fields.Char(string="Email Address",required=True)
    date_of_submission = fields.Date(string="Date Of Submission",required=True)
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status',default='draft')



    @api.constrains('name_english')
    def _check_legal_name_english(self):
        for record in self:
            if not re.match(r'^[A-Za-z\s]+$', record.name_english):
                raise ValidationError("The Legal Name of Entity (English) must contain only English letters. Please modify the name.")

    @api.constrains('name_arabic')
    def _check_legal_name_arabic(self):
        for record in self:
            if not re.match(r'^[\u0600-\u06FF\s]+$', record.name_arabic):
                raise ValidationError("The Legal Name of Entity (Arabic) must contain only Arabic letters. Please modify the name.")


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_done(self):
        self.status = 'done'