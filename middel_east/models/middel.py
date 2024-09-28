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



INVOICE_STATUS = [
    ('upselling', 'Upselling Opportunity'),
    ('invoiced', 'Fully Invoiced'),
    ('to invoice', 'To Invoice'),
    ('no', 'Nothing to Invoice')
]

class MiddelEast(models.Model):
    """Middle East Management System"""
    _name = "middel.east"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Middle East Management System"
    _rec_name = 'name'

    name = fields.Char(string='Booking Number', readonly=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    phone = fields.Char(
        'Phone', tracking=50,
        compute='_compute_phone', inverse='_inverse_phone', readonly=False, store=True)
    refrenc_c = fields.Char(string="Code", readonly=True, )
    email = fields.Char(string="Email")
    # visit_type =fields.Selection([('draft', "Draft"),('quotations', "Quotations"), ('approval', "Approval"),('in_progress', "In Progress"),  ('c_complete', "Complete")],
    #                           string="Visit Type", default='draft')
    street = fields.Char(string="Street", translate=True)
    location = fields.Char(string="Customer Map Location")
    date = fields.Date(string="Receiving Date", default=fields.date.today(), required=True)
    user_middel = fields.Many2one('res.users', default=lambda self: self.env.user, required=True,
                                  string="Responsible")
    status = fields.Selection(
        [('draft', "Draft"), ('sent', "Quotations"), ('approval', "Approval"), ('in_progress', "In Progress"),
         ('c_complete', "Complete")],
        string="Status", default='draft')
    middel_east_team_id = fields.Many2one('middel.east.team', string="Middel Team")

    middel_team_members_ids = fields.Many2many(related="middel_east_team_id.team_member_ids", string="Member")

    team_member_ids = fields.Many2many('res.users', string="Team Members",
                                       domain="[('id', 'in', middel_team_members_ids)]")

    project_id = fields.Many2one(related='middel_east_team_id.project_id', string="Project")
    project_task_id = fields.Many2one('project.task', string="Team Task")
    task_count = fields.Integer(compute="_compute_task_count")
    quotation_count = fields.Integer(compute='_compute_sale_data', string="Number of Quotations")

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    total_charge = fields.Monetary(string="Total")
    invoice_id = fields.Many2one('account.move', string='Invoice')
    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced', tracking=True)
    invoice_ids = fields.One2many('account.move', 'middel_id', string="Invoices", copy=False, tracking=True)

    contract_id = fields.Many2one('middel.east.contract', string='Contract')
    contract_count = fields.Integer(string="Invoice Count", compute='_get_contract', tracking=True)
    contract_ids = fields.One2many('middel.east.contract', 'contract_middel', string="Contract", copy=False, tracking=True)

    payment_state = fields.Selection(related="invoice_id.payment_state", string="Invoice Status")
    attachment_id = fields.Binary(string="Attachment")
    image = fields.Binary(string="Image")
    order_ids = fields.One2many('sale.order', 'order_middel_oppo_id', string='Orders')
    quotations_id = fields.Many2many('sale.order', string='Quotations')


    note = fields.Html(
        string="Terms and conditions",
        compute='_compute_note',
        store=True, readonly=False, precompute=True)
    middel_order_line_ids = fields.One2many('sale.order.line', 'middel_east_order_line', string="Middel Service")
    middel_expense_ids = fields.One2many('hr.expense', 'middel_expense_id', string="Middel Expense")

    middel_order_line_ids = fields.One2many('middel.service', 'middel_service_details_id', string="Middel Service")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True,
        precompute=True,
        ondelete='restrict'
    )

    prod_ids = fields.Many2many(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null'
    )



    total_amount = fields.Monetary(
        string="Total Amount",
        currency_field='currency_id', store=True,
        tracking=True,
    )

    journal_id = fields.Many2one(
        'account.journal', string="Invoicing Journal",
        compute="_compute_journal_id", store=True, readonly=False, precompute=True,
        domain=[('type', '=', 'sale')], check_company=True,
        help="If set, the SO will invoice in this journal; "
             "otherwise the sales journal with the lowest sequence is used.")
    invoice_status = fields.Selection(
        selection=INVOICE_STATUS,
        string="Invoice Status",
        compute='_compute_invoice_status',
        store=True)
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
             "The default value comes from the customer.",
    )

    team_id = fields.Many2one(
        comodel_name='crm.team',
        string="Sales Team",
        compute='_compute_team_id',
        store=True, readonly=False, precompute=True, ondelete="set null",
        change_default=True, check_company=True,  # Unrequired company
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, precompute=True,
        check_company=True,
        index='btree_not_null')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        compute='_compute_user_id',
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ))
    product_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0,
        context={'active_test': False},
        required=True)

    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, precompute=True,
        check_company=True,
        index='btree_not_null')

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")

    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)

    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)

    reference = fields.Char(
        string="Payment Ref.",
        help="The payment communication of this sale order.",
        copy=False)
    client_order_ref = fields.Char(string="Customer Reference", copy=False)

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Terms",
        compute='_compute_payment_term_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


    def _compute_sale_data(self):
        for rec in self:
            q_count = self.env['sale.order'].search_count([('order_middel_oppo_id', '=', rec.id)])
            rec.quotation_count = q_count

    @api.model
    def name_search(self, name, operator='ilike', limit=100):
        partner_id = self.search(['|', '|', ('name', operator, name), ('phone', operator, name),
                                  ('email', operator, name)])  # here you need to pass the args as per your requirement.
        return partner_id.name_get()
    def _compute_journal_id(self):
        self.journal_id = False

    def action_sale_quotations_new_middel(self):
        if self.partner_id and self.name:
            return self.action_new_quotation_middel()

    def action_new_quotation_middel(self):
        # if self.middel_order_line_ids != 'null' :

        middel_list = []
        for data in self.middel_order_line_ids:
            order_lines = {
                'display_type': data.display_type,
                'product_id': data.product_id.id,
                'product_uom_qty': data.product_uom_qty,
                'price_unit': data.price_unit,
                'discount': data.discount,
                'state': self.status,
                'price_subtotal': data.price_subtotal,
                'price_total': data.price_total,
                'tax_id': [Command.set(data.product_id.taxes_id.ids)],
            }
            middel_list.append(Command.create(order_lines))
        action = self.env['sale.order'].sudo().create({
                'order_middel_oppo_id': self.id,
                'partner_id': self.partner_id.id,
                'origin': self.name,
                'order_line': middel_list,
            })
        return action
        # self.status = 'sent'
        # action = self.env["ir.actions.actions"]._for_xml_id("middel_east.middel_action_quotations_new")
        # action['context'] = self._prepare_opportunity_quotation_context()
        #
        # action['context']['search_default_order_middel_oppo_id'] = self.id
        #
        # # else:
        # #     raise ValidationError('You cannot Create Quotations Product Line is Empty .')
        #
        # return action

    def action_view_middel_quotation(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = self._prepare_opportunity_quotation_context()
        action['context']['search_default_draft'] = 1
        action['domain'] =  self._get_action_view_sale_quotation_domain()
        quotations = self.order_ids.filtered_domain(self._get_action_view_sale_quotation_domain())
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    # def action_view_middel_contract(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id("middel_east.action_contract")
    #     action['context'] = self._prepare_opportunity_quotation_context()
    #     action['context']['search_default_draft'] = 1
    #     action['domain'] =  self._get_action_view_sale_quotation_domain()
    #     quotations = self.order_ids.filtered_domain(self._get_action_view_sale_quotation_domain())
    #     if len(quotations) == 1:
    #         action['views'] = [(self.env.ref('middel_east.view_order_form').id, 'form')]
    #         action['res_id'] = quotations.id
    #     return action

    def _get_action_view_sale_quotation_domain(self):
        return [('order_middel_oppo_id', '=', self.id)]


    def _prepare_opportunity_quotation_context(self):
        """ Prepares the context for a new quotation (sale.order) by sharing the values of common fields """
        self.ensure_one()
        
        middel_list = []
        for data in self.middel_order_line_ids:
            order_lines = {
                'display_type': data.display_type,
                'product_id': data.product_id.id,
                'product_uom_qty': data.product_uom_qty,
                'price_unit': data.price_unit,
                'discount': data.discount,
                'state': self.status,
                'price_subtotal': data.price_subtotal,
                'price_total': data.price_total,
                'tax_id': [Command.set(data.product_id.taxes_id.ids)],
            }

            middel_list.append(Command.create(order_lines))
            print('##########################',middel_list)
        quotation_context = {
            'default_order_middel_oppo_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_origin': self.name,
            'default_order_line': middel_list,
        }
        return quotation_context

    @api.depends('status', 'middel_order_line_ids.invoice_status')
    def _compute_invoice_status(self):
        confirmed_orders = self.filtered(lambda so: so.status == 'a_draft')
        (self - confirmed_orders).invoice_status = 'no'
        if not confirmed_orders:
            return
        lines_domain = [('is_downpayment', '=', False), ('display_type', '=', False)]
        line_invoice_status_all = [
            (order.id, invoice_status)
            for order, invoice_status in self.env['middel.service']._read_group(
                lines_domain + [('middel_service_details_id', 'in', confirmed_orders.ids)],
                ['middel_service_details_id', 'invoice_status']
            )
        ]
        for order in confirmed_orders:
            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            if order.status != 'a_draft':
                order.invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                if any(invoice_status == 'no' for invoice_status in line_invoice_status):
                    # If only discount/delivery/promotion lines can be invoiced, the SO should not
                    # be invoiceable.
                    invoiceable_domain = lines_domain + [('invoice_status', '=', 'to invoice')]
                    invoiceable_lines = order.order_line.filtered_domain(invoiceable_domain)
                    special_lines = invoiceable_lines.filtered(
                        lambda sol: not sol._can_be_invoiced_alone()
                    )
                    if invoiceable_lines == special_lines:
                        order.invoice_status = 'no'
                    else:
                        order.invoice_status = 'to invoice'
                else:
                    order.invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                order.invoice_status = 'invoiced'
            elif line_invoice_status and all(
                    invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                order.invoice_status = 'upselling'
            else:
                order.invoice_status = 'no'

    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for order in self:
            order = order.with_company(order.company_id)
            order.payment_term_id = order.partner_id.property_payment_term_id

    @api.depends('partner_id', 'user_id')
    def _compute_team_id(self):
        cached_teams = {}
        for order in self:
            default_team_id = self.env.context.get('default_team_id',
                                                   False) or order.partner_id.team_id.id or order.team_id.id
            user_id = order.user_id.id
            company_id = order.company_id.id
            key = (default_team_id, user_id, company_id)
            if key not in cached_teams:
                cached_teams[key] = self.env['crm.team'].with_context(
                    default_team_id=default_team_id,
                )._get_default_team_id(
                    user_id=user_id,
                    domain=self.env['crm.team']._check_company_domain(company_id),
                )
            order.team_id = cached_teams[key]

    @api.depends('partner_id')
    def _compute_user_id(self):
        for order in self:
            if order.partner_id and not (order._origin.id and order.user_id):
                # Recompute the salesman on partner change
                #   * if partner is set (is required anyway, so it will be set sooner or later)
                #   * if the order is not saved or has no salesman already
                order.user_id = (
                        order.partner_id.user_id
                        or order.partner_id.commercial_partner_id.user_id
                        or (self.user_has_groups('sales_team.group_sale_salesman') and self.env.user)
                )

    @api.depends('middel_order_line_ids.price_subtotal', 'middel_order_line_ids.price_tax', 'middel_order_line_ids.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.middel_order_line_ids.filtered(lambda x: not x.display_type)

            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = order.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                amount_tax = sum(order_lines.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = order.partner_id.address_get(['invoice'])[
                'invoice'] if order.partner_id else False

    @api.depends_context('lang')
    @api.depends('middel_order_line_ids.tax_id', 'middel_order_line_ids.price_unit', 'amount_total', 'amount_untaxed',
                 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.middel_order_line_ids.filtered(lambda x: not x.display_type)
            order.tax_totals = order.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        for order in self:
            if order.status != 'a_draft':
                continue
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            order.partner_shipping_id = order.partner_id.address_get(['delivery'])[
                'delivery'] if order.partner_id else False

    @api.depends('invoice_ids')
    def _get_invoiced(self):
        for middel in self:
            middel.invoice_count = len(middel.invoice_ids)

    @api.depends('contract_id')
    def _get_contract(self):
        for middel in self:
            middel.contract_count = len(middel.contract_id)

    @api.depends('partner_shipping_id', 'partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            fpos_id_before = order.fiscal_position_id.id
            key = (order.company_id.id, order.partner_id.id, order.partner_shipping_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    order.company_id
                )._get_fiscal_position(order.partner_id, order.partner_shipping_id).id

            order.fiscal_position_id = cache[key]

    @api.depends('invoice_ids')
    def _get_payment_state(self):
        for middel in self:
            if middel.invoice_ids:
                for invoicese in middel.invoice_ids:
                    middel.payment_state = invoicese.payment_state

    @api.depends('receiving_date', 'delivery_days')
    def validate_date(self):
        self.delivery_date = self.receiving_date + relativedelta(days=self.delivery_days)


    @api.depends('company_id')
    def _compute_currency_id(self):
        for order in self:
            order.currency_id = order.company_id.currency_id

    @api.depends('partner_id')
    def _compute_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if not use_invoice_terms:
            return
        for order in self:
            order = order.with_company(order.company_id)
            if order.terms_type == 'html' and self.env.company.invoice_terms_html:
                baseurl = html_keep_url(order._get_note_url() + '/terms')
                context = {'lang': order.partner_id.lang or self.env.user.lang}
                order.note = _('Terms & Conditions: %s', baseurl)
                del context
            elif not is_html_empty(self.env.company.invoice_terms):
                order.note = order.with_context(lang=order.partner_id.lang).env.company.invoice_terms

    def create_team_task(self):
        if self.project_id and self.team_member_ids != 'null' :
            project_task_id = self.env['project.task'].sudo().create({
                'name': self.middel_east_team_id.name,
                'project_id': self.project_id.id,
                'partner_id': self.partner_id.id,
                'user_ids': self.team_member_ids.ids,
                'date_assign': self.date,
                'middel_east_id': self.id
            })
            self.project_task_id = project_task_id.id
            self.status = 'in_progress'
        else:
            raise ValidationError('You cannot Create Task  completed The information Of Project.')

    def create_contract(self):
            if self.status in ('approval' ,'in_progress') :
                contract_middel_id = self.env['middel.east.contract'].sudo().create({
                    'contract_middel': self.id
                })
                self.contract_id = contract_middel_id.id
            else:
                raise ValidationError('You cannot Create Task  completed The information Of Project.')

    def _compute_task_count(self):
        for rec in self:
            task_count = self.env['project.task'].search_count([('middel_east_id', '=', rec.id)])
            rec.task_count = task_count

    def action_team_task(self):
        return {
            'name': 'Washing Team Task',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': self.project_task_id.id,
            'target': 'current',
        }

    def action_contract(self):
        return {
            'name': 'Contract',
            'type': 'ir.actions.act_window',
            'res_model': 'middel.east.contract',
            'view_mode': 'form',
            'res_id': self.contract_id.id,
            'target': 'current',
        }

    @api.depends('middel_order_line_ids.price_subtotal', 'middel_order_line_ids.price_tax',
                 'middel_order_line_ids.price_total')


    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.middel_order_line_ids.filtered(lambda x: not x.display_type)

            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = order.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                amount_tax = sum(order_lines.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.depends_context('lang')
    @api.depends('middel_order_line_ids.tax_id', 'middel_order_line_ids.price_unit', 'amount_total', 'amount_untaxed',
                 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.middel_order_line_ids.filtered(lambda x: not x.display_type)
            order.tax_totals = order.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

    @api.depends('partner_id.phone')
    def _compute_phone(self):
        for lead in self:
            if lead.partner_id.phone and lead._get_partner_phone_update():
                lead.phone = lead.partner_id.phone

    def _inverse_phone(self):
        for lead in self:
            if lead._get_partner_phone_update():
                lead.partner_id.phone = lead.partner_id

    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_id and self.phone != self.partner_id.phone:
            lead_phone_formatted = self._phone_format(fname='phone') or self.phone or False
            partner_phone_formatted = self.partner_id._phone_format(fname='phone') or self.partner_id.phone or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    def action_approval(self):
        self.status = 'approval'
        # users = self.env.ref('elevator_contract.group_contract_approval').users
        # for user in users:
        #     self.activity_schedule('elevator_contract.mail_act_contract_approval', user_id=user.id,
        #                            note=f'Please Approve Contract {self.partner_id.name} with Contract Number {self.num} ')

    def set_to_draft(self):
        self.status = 'draft'

    def create_qrf(self):
        self.status = 'quotations'

    def b_in_progress(self):
        self.status = 'c_complete'

    def b_in_progress_to_c_complete(self):
        self.status = 'c_complete'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('middel.east') or _('New')
        res = super(MiddelEast, self).create(vals_list)
        return res

    def unlink(self):
        for res in self:
            if res.status != 'c_complete':
                res = super(MiddelEast, res).unlink()
                return res
            else:
                raise ValidationError('You cannot delete the completed order.')
            
            
    def action_middel_invoice(self):
        for rec in self:
            record = ""

            invoice_lines = [(0, 0, [])]
            data = {
                'partner_id': self.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines
            }
            invoice_id = self.env['account.move'].sudo().create(data)
            invoice_id.action_post()
            self.invoice_id = invoice_id.id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'res_model': 'account.move',
                'res_id': invoice_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    def unlink(self):
        for res in self:
            if res.status != 'c_complete':
                res = super(MiddelEast, res).unlink()
                return res
            else:
                raise ValidationError('You cannot delete the completed order.')


    def create_invoices(self):
        self.ensure_one()
        self = self.with_company(self.company_id)
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        if not self.middel_order_line_ids:
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
        for data in self.middel_order_line_ids:
            invoice_lines = {
                'display_type': 'product',
                'product_id': data.product_id.id,
                'product_uom_id': data.product_id.uom_id.id,
                 'quantity': data.product_uom_qty,
                'price_unit': data.price_unit,
                'discount': data.discount,
                'price_subtotal': data.price_subtotal,
                'price_total': data.price_total,
                'tax_ids': [Command.set(data.product_id.taxes_id.ids)],

            }
            middel_list.append(Command.create(invoice_lines))

        values = {
            'move_type': 'out_invoice',
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'middel_id': self.id,
            'invoice_user_id': self.user_middel.id,
            'company_id': self.company_id.id,
            'invoice_line_ids':  middel_list,
            'user_id': self.user_middel.id,
        }

        return values



class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = __doc__

    middel_east_id = fields.Many2one('middel.east', string="Middle Contract")

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue
            line = line.with_context(lang=self.env.lang)
            name = line._get_sale_order_line_multiline_description_sale()
            line.name = name

    def _get_sale_order_line_multiline_description_sale(self):

        self.ensure_one()
        return self.product_id.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_middel_oppo_id = fields.Many2one(
        'middel.east', string='Visiter', check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    middel_count_num = fields.Integer(compute='_compute_sale_visitor', string="Visitor")

    def action_view_middel_quotation(self):
        self.ensure_one()
        source_orders = self.order_middel_oppo_id
        result = self.env['ir.actions.act_window']._for_xml_id('middel_east.action_middel_east')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('middel_east.middel_east_form_view', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def _get_action_view_sale_quotation_domain(self):
        return [('quotations_id', '=', self.id)]

    def _compute_sale_visitor(self):
        for rec in self:
            q_count = self.env['middel.east'].search_count([('quotations_id', '=', rec.id)])
            rec.middel_count_num = q_count



    def action_confirm(self):
        return super(SaleOrder, self.with_context({k:v for k,v in self._context.items() if k != 'default_tag_ids'})).action_confirm()

