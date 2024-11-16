from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty

class MiddelEastContract(models.Model):
    """Middel East Team"""
    _name = "middel.east.contract"
    _description = "Middle East Management System Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'contract'

    contract = fields.Char(string="Name", readonly=True, default=lambda self: _('New'), copy=False)
    date = fields.Date(string="Contract Date", default=fields.date.today(), required=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)
    contract_middel = fields.Many2one('middel.east', string="Middel Order")

    partner_id = fields.Many2one(related='contract_middel.partner_id', depends=['partner_id'])
    location_Details = fields.Char(related="contract_middel.location" , string= "Location Details")
    phone = fields.Char(related="contract_middel.phone" , string= "Phone Details")
    qty_count = fields.Integer(compute="_compute_origin_middel_count", string='Middel Count')
    qty_co = fields.Integer(compute='_compute_data', string='Middel Count')
    contract_order = fields.Many2one('sale.order', string="Quotations")
    project_id = fields.Many2one('project.project', string="Project Name")

    @api.model
    def name_search(self, name, operator='ilike', limit=100):
        partner_id = self.search(['|', '|', ('name', operator, name), ('phone', operator, name),
                                  ('email', operator, name)])
        return partner_id.name_get()
    @api.constrains('contract_middel')
    def _check_partner_id(self):
        for record in self:
            if record.contract_middel.id ==0 :
                raise ValidationError("The Partner cannot be Empty.")

    status = fields.Selection(
        [('draft', "Draft"),('confirmed', "Confirm")],
        string="Status", default='draft')

    def action_confirm(self):
        self.status = 'confirmed'
        self.create_project()

    def set_to_draft(self):
        self.status = 'draft'

    @api.depends('contract_order')
    def _compute_data(self):
        for order in self.id :
            print('UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU',order)


    def create_project (self):
        self.env['project.project'].sudo().create({
            'name': self.contract_middel.name,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'partner_id': self.partner_id.id,
            'sale_order_id': self.contract_order.id,
            'date_start': self.date,
        })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('contract', _('New')) == _('New'):
                vals['contract'] = self.env['ir.sequence'].next_by_code('middel.east.contract') or _('New')
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

    def action_view_source_contract_quotations(self):
        return {
            'name': 'Visit Middel Esat',
            'type': 'ir.actions.act_window',
            'res_model': 'sales.order',
            'view_mode': 'form',
            'res_id': self.contract_order.id,
            'target': 'current',
        }


    @api.depends('contract_middel')
    def _compute_origin_middel_count(self):
        for move in self:
            move.qty_count = len(move.contract_middel)


