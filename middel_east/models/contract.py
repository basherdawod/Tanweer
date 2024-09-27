from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty

class MiddelEastContract(models.Model):
    """Middel East Team"""
    _name = "middel.east.contract"
    _description = "Middle East Management System Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", readonly=True, default=lambda self: _('New'), copy=False)
    date = fields.Date(string="Contract Date", default=fields.date.today(), required=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)
    contract_middel = fields.Many2one('middel.east', string="Middel Order")
    partner_id = fields.Many2one(related='contract_middel.partner_id', depends=['partner_id'])
    location_Details = fields.Char(related="contract_middel.location" , string= "Location Details")
    phone = fields.Char(related="contract_middel.phone" , string= "Phone Details")
    qty_count = fields.Integer(compute="_compute_origin_middel_count", string='Middel Count')

    @api.model_create_multi
    def create_action(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('middel.east.contract') or _('New')
        res = super(MiddelEastContract, self).create(vals_list)
        return res

    def action_view_source_middel_booking(self):
        return {
            'name': 'Visit Middel Esat',
            'type': 'ir.actions.act_window',
            'res_model': 'middel.east',
            'view_mode': 'form',
            'res_id': self.contract_middel.id,
            'target': 'current',
        }


    @api.depends('contract_middel')
    def _compute_origin_middel_count(self):
        for move in self:
            move.qty_count = len(move.contract_middel)


