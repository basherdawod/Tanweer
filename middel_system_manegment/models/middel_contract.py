from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.addons.phone_validation.tools import phone_validation
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import base64
from odoo.fields import Command
from odoo.osv import expression
import re
import logging

class MiddelContract(models.Model):
    _name = "middel.contract" #middel_contract
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    name = fields.Char(string='Owner Name')
    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True)
    area_id = fields.Many2one('res.country.state', string="Aria")
    plot_no = fields.Integer(string="Plot No")
    makani_no = fields.Integer(string="Makani No")
    mob = fields.Integer(string="MOB")
    email = fields.Char(string="Email")
    quotation_id = fields.Many2one('middel.quotation', string='Quotations' , readonly=True)
    status = fields.Selection(
        [('draft', "Draft"),('complete', "Complete")],string="Status", default='draft')

    middel_list_ids = fields.One2many('middel.contract.line','contract_id',string='Product List')


    visit_ids = fields.One2many('visit.card','middel_contract_id', string='Visits')
    visit_count = fields.Integer(compute='_compute_visit_cards', string="Visit Cards")
    visit_card_id = fields.Many2one('visit.card')

    middel_quotation_id = fields.Many2one('middel.quotation',string=' Middel Quotation',required=False)

    def _compute_visit_cards(self):
        for rec in self:
            visit_cards_count = self.env['visit.card'].search_count([('middel_contract_id', '=', rec.id)])
            rec.visit_count = visit_cards_count


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_compleat(self):
        self.status = 'complete'


    def action_view_visit_cards(self):
        self.ensure_one()
        source_orders = self.visit_ids
        result = self.env['ir.actions.act_window']._for_xml_id('middel_system_manegment.action_visit_card')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('middel_system_manegment.visit_card_contract_view', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result



    def action_create_visit_card(self):
        for record in self:
            existing_visit = record.visit_ids
            if not existing_visit:
                visit_name = record.name
            else:
                next_letter = chr(65 + len(existing_visit))
                visit_name = f"{record.name}/{next_letter}"

            visit_card_record = self.env['visit.card'].create({
                'visit_no': visit_name,
                'date': fields.Date.context_today(self),
                'area': self.area_id.id,
            })
    
        return {
            'name': 'New',
            'type': 'ir.actions.act_window',
            'res_model': 'visit.card',
            'res_id': visit_card_record.id,
            'view_mode': 'form',
            'target': 'current',
        }


    # def action_create_visit_card(self):
    #     for record in self:
    #     # Get existing visits related to the current record
    #         existing_visits = record.visit_card_ids  # Assuming visit_card_ids is a One2many field

    #     # Determine the visit name based on the number of existing visits
    #         if not existing_visits:
    #         # First visit: Create without any suffix
    #             visit_name = record.name
    #         else:
    #         # Get the next letter (A, B, C, etc.) based on the number of existing visits
    #             next_letter = chr(65 + len(existing_visits))  # 65 = ASCII for 'A'
    #             visit_name = f"{record.name}/{next_letter}"

    #     # Create a new visit card
    #         card = self.env['visit.card'].create({
    #             'visit_no': visit_name,  # Use the dynamically generated visit name
    #             'area': record.area_id.id,  # Ensure area_id is valid
    #             'visit_card_id': record.id,  # Assuming 'visit_card_id' is a related field
    #         })

    #     # Post a message about the newly created visit card
    #         record.message_post(body=f"Visit Card {card.visit_no} has been created.")


    # def action_create_visit_card(self):
    #     for record in self:
    #     # Get existing visits related to the current record
    #         existing_visits = record.visit_card_ids  # Assuming visit_card_ids is a One2many field

    #     # Determine the visit name based on the number of existing visits
    #         if not existing_visits:
    #         # First visit: Create without any suffix
    #             visit_no = record.name
    #             # visit_no = 1  # Store the numeric visit number
    #         else:
    #         # Get the next letter (A, B, C, etc.) based on the number of existing visits
    #             next_letter = chr(65 + len(existing_visits))  # 65 = ASCII for 'A'
    #             # visit_name = f"{record.name}/{next_letter}"
    #             visit_no = len(existing_visits) + 1  # Increment the numeric part of the visit number

    #     # Create a new visit card
    #         card = self.env['visit.card'].create({
    #             'visit_card_id': record.quotation_id.id,  # This stores a numeric value (1, 2, 3, ...)
    #             # 'visit_name': visit_name,  # Assuming visit_name is a Char field to store "Name/A", "Name/B", etc.
    #             'date': fields.Date.context_today(self),
    #             'area': record.area_id.id,  # Ensure area_id is valid
    #             # 'visit_card_id': record.id,  # Assuming 'visit_card_id' is a related field
    #         })

    #     # Post a message about the newly created visit card
    #         record.message_post(body=f"Visit Card {card.visit_no} has been created.")


class ContractLine(models.Model):
    _name = 'middel.contract.line'  #model_middel_contract_line

    contract_id = fields.Many2one('middel.contract')
    product = fields.Many2one('middel.product',string='Product',required=False)

    description = fields.Char(string="description", related='product.description', depends=['product'],)
    quantity = fields.Integer(string="Quantity",)
    price = fields.Float(string='price')