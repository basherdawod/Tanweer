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
    plot_no = fields.Integer(string="Plot No")
    makani_no = fields.Char(string="Makani No",)
    mob = fields.Char(string='MOB',compute='_compute_phone', readonly=True, store=True)
    email = fields.Char(string='email',compute='_compute_email', readonly=True, store=True)
    quotation_id = fields.Many2one('middel.quotation', string='Quotations' , readonly=True)
    status = fields.Selection(
        [('draft', "Draft"),('confirm', "Confirm"),('done', "Done")],string="Status", default='draft' )
    date_today = fields.Date(string='Date Today', default=lambda self: fields.Date.today(),readonly=True)
    date_next_year = fields.Date(string='Date Next Year', default=lambda self: fields.Date.today() + timedelta(days=365),readonly=True)

    middel_list_ids = fields.One2many('middel.contract.line','contract_id',string='Product List')


    visit_ids = fields.One2many('visit.card','middel_contract_id', string='Visits')
    visit_count = fields.Integer(compute='_compute_visit_counts', string="Visit Cards")
    visit_card_id = fields.Many2one('visit.card')

    middel_quotation_id = fields.Many2one('middel.quotation',string=' Middel Quotation',required=False)

    middel_contract_line_ids = fields.One2many('middel.contract.line', 'contract_id', string="Contract Lines")
    button_disabled = fields.Boolean(string="Disable Button", default=False)

    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id.id, string="Company")

    tax_ids = fields.Many2many('account.tax', string='Taxes')



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

    def set_to_done(self):
        self.status = 'done'

    def set_to_confirm(self):
        self.status = 'confirm'


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
        self.button_disabled = True
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


    def action_view_invoice(self, invoices=None):
        self.ensure_one()
        source_orders = invoices or self.invoice_ids  # Use passed invoices or default to self.invoice_ids
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')

        if source_orders:
            if len(source_orders) > 1:
                result['domain'] = [('id', 'in', source_orders.ids)]
            else:
                result['views'] = [(self.env.ref('account.view_move_form', False).id, 'form')]
                result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    def create_invoices(self):
        self.status = 'confirm'
        self.ensure_one()
        self = self.with_company(self.company_id)
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        if not self.middel_list_ids:
            raise ValidationError(
                _("No service product found, please define one.")
            )

        # 1) Create invoices.
        invoice_vals_list = []
        for middel in self:
            middel = middel.with_company(middel.company_id).with_context(lang=middel.partner_id.lang)
            invoice_vals = middel._prepare_invoice()
            invoice_vals_list.append(invoice_vals)
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        if moves :
            moves.action_post()
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        for move in moves:
            move.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': move, 'origin': self},
                subtype_xmlid='mail.mt_note',
            )


    def _prepare_invoice(self):

        self.ensure_one()
        middel_list = []
        for data in self.middel_list_ids:
            invoice_lines = {
                'display_type': 'product',
                'product_id': data.product_id.id,
                'quantity': data.quantity,
                'tax_ids': self.tax_ids,
                'price_unit': data.list_price,
                'price_subtotal': data.price_total,
            }
            middel_list.append(Command.create(invoice_lines))

        values = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'middel_id': self.id,
            'company_id': self.company_id.id,
            'invoice_line_ids':  middel_list,
        }

        self.button_disabled = True
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
                    
        return values



class ContractLine(models.Model):
    _name = 'middel.contract.line'  #model_middel_contract_line

    contract_id = fields.Many2one('middel.contract')
    product_id = fields.Many2one(comodel_name='product.product',string="Product",domain="[('brand', '=', brand), ('categ_id', '=', categ_id)]")

    description = fields.Char(string="description")
    quantity = fields.Integer(string="Quantity",)
    price = fields.Float(string='price')
    categ_id = fields.Many2one('product.category', 'Product Category',)
    brand = fields.Many2one(comodel_name='middel.brand', string='Brand')
    model_no = fields.Char(string="Model No" )
    standard_price = fields.Float('Cost',digits='Product Cost',
        help="""Value of the product (automatically computed in AVCO).
           Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
           Used to compute margins on sale orders.""")
    list_price = fields.Float('Product Price', default=0.0,
        help="Price at which the product is sold to customers.")
    image = fields.Binary(
        string="Image",related="product_id.image_1920",
        required=False)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    price_total = fields.Char(string="Total")


    @api.onchange('brand')
    def _onchange_brand(self):
        """Update the product field domain based on the selected brand."""
        self.product_id = False  # Clear the product selection when brand changes
        return {
            'domain': {
                'product_id': [('brand', '=', self.brand.id)]
            }
        }