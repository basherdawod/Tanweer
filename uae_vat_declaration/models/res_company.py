from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    name_ar = fields.Char(string="Name In Arabic")