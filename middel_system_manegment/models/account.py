
from odoo import models, fields, api, _



class AccountMove(models.Model):
    _inherit = 'account.move'

    middel_id = fields.Many2one('middel.quotation')
    middel_count = fields.Integer(compute="_compute_origin_middel_count", string='Middel Count')

    @api.depends('middel_id')
    def _compute_origin_middel_count(self):
        for move in self:
            move.middel_count = len(move.middel_id)

    def action_view_source_middel_booking(self):
        self.ensure_one()
        source_orders = self.middel_id
        result = self.env['ir.actions.act_window']._for_xml_id('middel_system_manegment.action_middel_quotation_east')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('middel_system_manegment.middel_quotation_form_view', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
