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
from datetime import datetime ,timedelta

class MiddelContract(models.Model):
    _name = "middel.contract" #middel_contract
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    name = fields.Char(string='Owner Name', readonly=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True)
    area_id = fields.Many2one('res.country.state', string="Aria")
    plot_no = fields.Integer(string="Plot No", required=True)
    makani_no = fields.Char(string="Makani No", required=True)
    mob = fields.Char(string='MOB',compute='_compute_phone', readonly=True, store=True)
    email = fields.Char(string='email',compute='_compute_email', readonly=True, store=True)
    quotation_id = fields.Many2one('middel.quotation', string='Quotations' , readonly=True)
    status = fields.Selection(
        [('draft', "Draft"),('complete', "Complete")],string="Status", default='draft' )
    date_today = fields.Date(string='Date Today', default=lambda self: fields.Date.today(),readonly=True)
    date_next_year = fields.Date(string='Date Next Year', default=lambda self: fields.Date.today() + timedelta(days=365),readonly=True)

    middel_list_ids = fields.One2many('middel.contract.line','contract_id',string='Product List')


    visit_ids = fields.One2many('visit.card','middel_contract_id', string='Visits')
    visit_count = fields.Integer(compute='_compute_visit_counts', string="Visit Cards")
    visit_card_id = fields.Many2one('visit.card')

    middel_quotation_id = fields.Many2one('middel.quotation',string=' Middel Quotation',required=False)


    @api.depends('partner_id.phone')
    def _compute_phone(self):
        for lead in self:
            if lead.partner_id.phone and lead._get_partner_phone_update():
                lead.mob = lead.partner_id.phone

    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_id and self.mob != self.partner_id.phone:
            lead_phone_formatted = self._phone_format(fname='phone') or self.mob or False
            partner_phone_formatted = self.partner_id._phone_format(fname='phone') or self.partner_id.mob or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    @api.depends('partner_id.email')
    def _compute_email(self):
        for lead in self:
            if lead.partner_id.email and lead._get_partner_email_update():
                lead.email = lead.partner_id.email

    def _get_partner_email_update(self):
        self.ensure_one()
        if self.partner_id and self.email != self.partner_id.email:
            lead_email_formatted = self._phone_format(fname='email') or self.email or False
            partner_phone_formatted = self.partner_id._phone_format(fname='phone') or self.partner_id.email or False
            return lead_email_formatted != partner_phone_formatted
        return False

    @api.depends('visit_ids')
    def _compute_visit_counts(self):
        for rec in self:
            rec.visit_count = len(rec.visit_ids)

    # @api.depends('visit_ids')
    # def _compute_visit_counts(self):
    #     for record in self:
    #         record.visit_count = len(record.visit_ids)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('middel.contract') or _('New')
        res = super(MiddelContract, self).create(vals_list)
        return res

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

    # def get_visit_card_date(self):
    #     visit_card = self.visit_ids and self.visit_ids[0]
    #     return visit_card.date if visit_card else None

    def get_visit_card_dates(self):
        dates = [visit_card.date for visit_card in self.visit_ids]
        return dates

    def action_create_visit_card(self):
        base_date = fields.Date.context_today(self)
        for record in self:
            # Get existing visit count
            existing_visit_count = len(record.visit_ids)

            for i in range(4):
                # Calculate the next letter based on the existing visit count and loop index
                next_letter = chr(65 + existing_visit_count + i)
                visit_name = f"{record.name}/{next_letter}"

                # Calculate the future date by adding months
                future_date = base_date + relativedelta(months=i * 3)

                # Create the visit card record
                try:
                    visit_card_record = self.env['visit.card'].create({
                        'name': visit_name,
                        'partner_id': record.partner_id.id,
                        'middel_contract_id':record.id,
                        'date': future_date,
                        'area': record.area_id.id,
                        'makani_no':record.makani_no
                    })

                    if not visit_card_record:
                        raise UserError("Error creating visit card record")

                except Exception as e:
                    raise UserError(f"An unexpected error occurred: {str(e)}")

class ContractLine(models.Model):
    _name = 'middel.contract.line'  #model_middel_contract_line

    contract_id = fields.Many2one('middel.contract')
    product = fields.Many2one('middel.product',string='Product',required=False)

    description = fields.Char(string="description", related='product.description', depends=['product'],)
    quantity = fields.Integer(string="Quantity",)
    price = fields.Float(string='price')