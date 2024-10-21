from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty

class MiddelTeam(models.Model):
    """Middel East Team"""
    _name = "middel.team"
    _description = "Middle East Management System team"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    id_employee = fields.Char(string="ID Card" , readonly=True, default=lambda self: _('New'), copy=False)
    name = fields.Char(string="Name", required=True)
    country_id = fields.Many2one('res.country', string="Emirates", readonly=True,
                                 default=lambda self: self.env.ref('base.ae').id)
    employee_address = fields.Many2one('res.country.state', string="Address", domain="[('country_id', '=', country_id)]")
    street = fields.Char(string="Street")
    street2  = fields.Char(string="Street1", required=True)
    time_cost = fields.Float(
        string='Time cost',
        required=False)
    image = fields.Binary(string="Image")


    @api.constrains('name' , 'employee_address')
    def _check_name_is_capital(self):
        for record in self:
            if record.name == 'null':
                raise ValidationError("Fill The Name ")
            if record.employee_address == 'null':
                raise ValidationError("The employee address cannot be 'null'.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('id_employee', _('New')) == _('New'):
                vals['id_employee'] = self.env['ir.sequence'].next_by_code('middel.team') or _('New')
        res = super(MiddelTeam, self).create(vals_list)
        return res

