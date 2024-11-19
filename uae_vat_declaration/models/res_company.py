from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    name_ar = fields.Char(string="Name In Arabic")
    corporate_tax = fields.Char(string="Corporate Tax")
    effective_reg_date = fields.Date(string="Effective Regestration Date")
    corporit_tax_date = fields.Date(string="Corporate Tax Date")