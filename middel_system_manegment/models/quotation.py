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


class MiddelQuotation(models.Model):
    """Middle East quotation"""
    _name = "middel.quotation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Middle East Quotation"
    _rec_name = 'name'
    name = fields.Char(string='Booking Number', readonly=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    user_id = fields.Many2many('res.users', string="Assigned User")  # Link to res.users
    country_id = fields.Many2one('res.country', string="Emirates",readonly=True, default=lambda self: self.env.ref('base.ae').id)
    state_id = fields.Many2one('res.country.state', string="Makani", domain="[('country_id', '=', country_id)]")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    margin_amount = fields.Monetary(
        string="Margin %",
        currency_field='currency_id',
        store=True , readonly=True,)
    makani = fields.Char(string="Makani Number", readonly=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id.id, string="Company")
    total_project_amount = fields.Monetary(
        string="Project Amount",
        currency_field='currency_id',
        readonly=True,
        store=True)
    total_expense_line_amount = fields.Monetary(
        string="Expense Line Amount",
        currency_field='currency_id',readonly=True,
        store=True)

    phone = fields.Char(
        'Phone', tracking=50,
         compute='_compute_phone', readonly=True, store=True)

    refrenc_c = fields.Char(string="Code", readonly=True, )

    date = fields.Date(string="Date", default=fields.date.today(), required=True)
    status = fields.Selection(
        [('draft', "Draft"),('Confirm', "Confirm"), ('Cancel', "Cancel")],
        string="Status", default='draft')

    project = fields.Selection(
        string='Project',
        selection=[
                   ('Villa', 'Villa'),('VUC', 'Villa Under Construction'),
                    ('Building ', 'Building'),('BUC', 'Building Under Construction'),
            ('Farm','Farm'),('SOF Office','Shop Or Office'),('Factory','Factory'),],
        required=False, )
    customer_need_cid = fields.Selection(
        string=' Customer Need CID ',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        required=False, )

    customer_need_amc = fields.Selection(
        string=' Customer Need AMC ',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        required=False, )

    customer_need_drawing = fields.Selection(
        string=' Customer Need Drawing',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        required=False, )
    approch = fields.Selection(
            string=' Approch ',
            selection=[('direct', 'Direct'),
                       ('Instagram', 'Instagram'),
                       ('snap', 'Snap'),
                       ('twitter', 'Twitter'),
                       ('Shop', 'shop'),
                       ('Tik_tok', 'Tik Tok'),
                       ('Friend', 'Friend'), ],
            required=False, )

    middel_quotation_id = fields.Many2one(
        comodel_name='middel.east',
        string=' Middel Quotation',
        required=False)


    order_product_line_ids = fields.One2many(
        comodel_name='middel.service.line',
        inverse_name='product_order_line',
        string='Order Product line',
        required=False)


    visitor_count = fields.Integer(compute='_compute_middel_data', string="Number of Visitor")
    invoice_ids = fields.One2many('account.move', 'middel_id', string="Invoices", copy=False, tracking=True)


    invoice_id = fields.Many2one('account.move', string='Invoice')
    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced', tracking=True)
    middel_contract_line_ids = fields.One2many('middel.contract.line','contract_id')

    #
    # def write(self, vals):
    #     for record in self:
    #         # Check if the record's status is 'Confirm'
    #         if record.status == 'confirm':
    #             # If creating invoices allows modification, continue; otherwise, raise an error
    #             if not record.create_invoices():
    #                 raise UserError("You cannot edit this record because it is confirmed.")

    @api.depends('invoice_ids')
    def _get_invoiced(self):
        for middel in self:
            middel.invoice_count = len(middel.invoice_ids)

    def _compute_middel_data(self):
        for rec in self:
            q_count = self.env['middel.east'].search_count([('id', 'in', rec.middel_quotation_id.ids)])
            rec.visitor_count = q_count

    def action_view_middel_visitor(self):
        self.ensure_one()
        source_orders = self.middel_quotation_id  # Reference the recordset, not just the id
        result = self.env['ir.actions.act_window']._for_xml_id('middel_system_manegment.action_middel_east')

        if source_orders:  # If source_orders is not empty
            if len(source_orders) > 1:  # If it's more than one record
                result['domain'] = [('id', 'in', source_orders.ids)]
            else:  # If it's a single record
                result['views'] = [(self.env.ref('middel_system_manegment.middel_east_form_view', False).id, 'form')]
                result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

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
        self.ensure_one()
        self = self.with_company(self.company_id)
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        if not self.order_product_line_ids:
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
        return self.action_view_invoice(invoices=moves)

    def _prepare_invoice(self):

        self.ensure_one()
        middel_list = []
        for data in self.order_product_line_ids:
            invoice_lines = {
                'display_type': 'product',
                'product_id': data.product_id.id,
                'quantity': data.quantity,
                'price_unit': data.list_price,
                'price_subtotal': data.price_total,
            }
            middel_list.append(Command.create(invoice_lines))

        values = {
            'move_type': 'out_invoice',
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'middel_id': self.id,
            'company_id': self.company_id.id,
            'invoice_line_ids':  middel_list,
        }
        return values

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    total_charge = fields.Monetary(string="Total")


    attachment_id = fields.Binary(string="Attachment")
    image = fields.Binary(string="Image")

    def action_approval(self):
        if self.middel_quotation_id:
            self.middel_quotation_id.action_approval()
            self.status = 'Confirm'

    def set_to_draft(self):
        self.status = 'draft'

    def action_cancel(self):
        self.status = 'Cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('middel.quotation') or _('New')
        res = super(MiddelQuotation, self).create(vals_list)
        return res

    def unlink(self):
        for res in self:
            if res.status != 'Confirm':
                res = super(MiddelQuotation, res).unlink()
                return res
            else:
                raise ValidationError('You cannot delete the completed order contact To Admin or Rest To draft First .')

    maintenance_count = fields.Integer(compute='_compute_maintenance', string="Maintrnance Count")
    qu_ids = fields.One2many('middel.contract','middel_quotation_id', string='Maintrnance')
    
    def _compute_maintenance(self):
        for rec in self:
            mainte_count = self.env['middel.contract'].search_count([('middel_quotation_id', '=', rec.id)])
            rec.maintenance_count = mainte_count
    def action_view_maintenance(self):
        self.ensure_one()
        source_orders = self.qu_ids
        result = self.env['ir.actions.act_window']._for_xml_id('middel_system_manegment.action_middel_contract')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('middel_system_manegment.middel_east_contract_view', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def action_create_maintenance(self):
        if not self.order_product_line_ids:
            raise ValidationError("No Products found.")
        maintenance_line = []
        for data in self.order_product_line_ids:
            if not data.product_id: 
                raise ValidationError("Product not found in line.")
            product_lines = {
                'product': data.product_id.id,
                'description': data.description,
                'quantity': data.quantity,
                'price': data.price_total,
            }
            maintenance_line.append(Command.create(product_lines))

            maintenance_record = self.env['middel.contract'].create({
                'partner_id': self.partner_id.id, 
                'quotation_id': self.id,
                'middel_quotation_id': self.id,
                'area_id':self.state_id.id,
                'middel_list_ids':maintenance_line,
            
           
             })
        # return {
        #     'name': 'New',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'middel.contract',
        #     'res_id': maintenance_record.id,
        #     'view_mode': 'form',
        #     'target': 'current', 
        # }

    