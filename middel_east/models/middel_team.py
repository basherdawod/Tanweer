from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty

class MiddelEastTeam(models.Model):
    """Middel East Team"""
    _name = "middel.east.team"
    _description = "Middle East Management System team"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    color = fields.Integer()

    name = fields.Char(string="Name Of Task", required=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)
    team_member_ids = fields.Many2many('res.users', string="Team Members")
    project_id = fields.Many2one('project.project', string="Team Project")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MiddelEastTeam, self).create(vals_list)
        project_id = self.env['project.project'].sudo().create({
            'name': res.name,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
        })
        res.project_id = project_id.id
        return res
