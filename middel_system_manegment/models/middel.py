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

class MiddelEast(models.Model):
    """Middle East Management System"""
    _name = "middel.east"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Middle East Management System"
    _rec_name = 'name'

    name = fields.Char(string='Booking Number', readonly=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    user_id = fields.Many2many('res.users', string="Assigned User")  # Link to res.users
    country_id = fields.Many2one('res.country', string="Emirates",readonly=True, default=lambda self: self.env.ref('base.ae').id)
    state_id = fields.Many2one('res.country.state', string="City", domain="[('country_id', '=', country_id)]")
    makani =fields.Integer (string="Makani" , required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    phone = fields.Char(
        'Phone', tracking=50,
         compute='_compute_phone', readonly=True, store=True)

    refrenc_c = fields.Char(string="Code", readonly=True, )

    location = fields.Char(string="Customer Map Location")
    date = fields.Date(string="Date", default=fields.date.today(), required=True)
    status = fields.Selection(
        [('draft', "Draft"),('waiting', "waiting for visiting"), ('sent', "Quotations"), ('approval', "Approval"), ('in_progress', "In Progress"),
         ('c_complete', "Complete")],
        string="Status", default='draft')

    quotation_count = fields.Integer(compute='_compute_sale_data', string="Number of Quotations")

    # team_member_ids = fields.Many2many('middel.team', string="Team Members")

    team_work = fields.One2many(
        comodel_name='middel.team.line',
        inverse_name='middel_team',
        string='Team Work',
        required=False)
    project = fields.Selection(
        string='Project',
        selection=[
                    ('Villa', 'Villa'),('VUC', 'Villa Under Construction'),
                    ('Building ', 'Building'),('BUC', 'Building Under Construction'),
                    ('Farm','Farm'),('SOF_Office','Shop Or Office'),('Factory','Factory'),],
        required=False, )


    customer_need_cid = fields.Selection(
        string=' Customer Need CID ',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        required=False)

    customer_need_amc = fields.Selection(
        string=' Customer Need AMC ',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        required=False )

    customer_need_drawing = fields.Selection(
        string=' Customer Need Drawing',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        required=False )
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

    customer_need_active = fields.Boolean(
        string='Customer Need Details',
        required=False)

    customer_need_visiter = fields.Boolean(
        string='Customer Need Visitor',
        required=False)
    customer_need = fields.One2many(
        comodel_name='middel.customer.need',
        inverse_name='middel_east_id',
        string='Customer Need',
        required=False)

    middel_expense_line = fields.One2many(
        comodel_name='middel.expense.line',
        inverse_name='middel_expense_id',
        string='Company Expense Cost',
        required=False)

    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id.id, string="Company")
    total_charge = fields.Monetary(string="Total")
    attachment_id = fields.Binary(string="Attachment")
    image = fields.Binary(string="Image")
    address = fields.Char(string="Address",
                          compute="_compute_address", store=True ,readonly=True )
    quotation_ids = fields.One2many('middel.quotation',
                                    'middel_quotation_id', string='Quotations')
    currency_id = fields.Many2one('res.currency',
                                  string='Currency', default=lambda self: self.env.company.currency_id)
    total_cost_employee = fields.Monetary(
            string="Employee Total Expenses",
        currency_field='currency_id',
            store=True)
    expenses_total_amount = fields.Monetary(
            string="Company Total Cost",
            currency_field='currency_id',
            store=True)
    total_amount = fields.Monetary(
                string="Total Amount",
                currency_field='currency_id',
                store=True)

    petrol_Charges = fields.Many2one(
        comodel_name='middel.petrol.charges',
        string='Petrol Charges',store=True,
        required=True)

    distance = fields.Integer(
        string='Distance K/M',
        required=False)

    petrol_cost = fields.Monetary(string="Petrol Cost" , currency_field='currency_id', compute="_petrol_cont_compute")

    visits = fields.Integer(
        string='Visits No',
        required=False)


    works_hours = fields.Integer(
        string='Works Hours',
        required=False)


    works_employee = fields.Integer(
        string='How Many Employee Need ',
        required=False)

    @api.depends('petrol_cost', 'visits', 'distance', 'petrol_Charges')
    def _petrol_cont_compute(self):
        for record in self:
            if record.distance and record.visits and record.petrol_Charges:
                total_distance = record.distance * record.visits
                record.petrol_cost = total_distance / record.petrol_Charges.charges if record.petrol_Charges.charges else 0.0
            else:
                record.petrol_cost = 0.0


    def _compute_sale_data(self):
        for rec in self:
            q_count = self.env['middel.quotation'].search_count([('middel_quotation_id', '=', rec.id)])
            rec.quotation_count = q_count


    def action_view_middel_quotation(self):
        self.ensure_one()
        source_orders = self.quotation_ids
        result = self.env['ir.actions.act_window']._for_xml_id('middel_system_manegment.action_middel_quotation_east')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('middel_system_manegment.middel_quotation_form_view', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    #
    # @api.constrains('makani')
    # def _check_makani(self):
    #     pattern = re.compile(r'^[0-9]{10}$')  # Exactly 10 digits are allowed
    #     for record in self:
    #         if record.makani and not pattern.match(record.makani):
    #             raise ValidationError("Invalid Makani Number. It should consist of exactly 10 digits.")



    @api.depends('middel_expense_line', 'middel_expense_line.total_cost')
    def _compute_amount(self):
        for sheet in self:
            sheet.expenses_total_amount = sum([line.total_cost for line in sheet.expense_line_ids])


    @api.depends('team_work', 'team_work.total')
    def _compute_amount(self):
        for sheet in self:
            sheet.total_cost_employee = sum([line.total for line in sheet.team_work])


    @api.depends('customer_need', 'customer_need.price_total')
    def _compute_amount(self):
        for sheet in self:
            sheet.total_amount = sum([line.price_total for line in sheet.customer_need])

    def action_create_quotation(self):
        middel_list = []
        for data in self.customer_need:
            order_lines = {
                'product': data.product.id,
                'description': data.description,
                'model_no': data.model_no,
                'price': data.price,
                'quantity': data.quantity,
                'image': data.image,
                'product_category': data.product_category.id,
                'product_sub': data.product_sub.id,
                'brand': data.brand.id,
                'price_total': data.price_total,
                'amount_total': data.amount_total,
            }
            middel_list.append(Command.create(order_lines))

        for record in self:
            existing_quotations = record.quotation_ids
            if not existing_quotations:
                # First quotation: Create without any suffix
                quotation_name = record.name
            else:
                # Get the next letter (A, B, C, etc.) based on the number of existing quotations
                next_letter = chr(65 + len(existing_quotations))  # 65 = ASCII for 'A'
                quotation_name = f"{record.name}/{next_letter}"

            # Create the new quotation
            quotation = self.env['middel.quotation'].create({
                'name': quotation_name,
                'partner_id': record.partner_id.id,
                'middel_quotation_id': record.id,  # Linking back to the custom model
                'country_id': record.country_id.id,
                'state_id': record.state_id.id,
                'phone': record.phone,
                'project': record.project,
                'customer_need_cid': record.customer_need_cid,
                'customer_need_amc': record.customer_need_amc,
                'approch': record.approch,
                'order_line_ids': middel_list,  # Pass the order lines
            })

            # Add message or notification for the new quotation
            record.message_post(body=f"Quotation {quotation.name} has been created.")

    @api.onchange('country_id')
    def _onchange_country(self):
        if self.country_id:
            # Fetch all states for the selected country
            states = self.env['res.country.state'].search([('country_id', '=', self.country_id.id)])
            state_names = [state.name for state in states]
            # Optionally do something with state_names, e.g., log them
            print(f"States for {self.country_id.name}: {state_names}")

    @api.depends('partner_id.street', 'partner_id.city', 'partner_id.zip')
    def _compute_address(self):
        for lead in self:
            if lead.partner_id and lead._get_partner_address_update():
                # Concatenate the address fields from the partner to form a full address
                lead.address = ', '.join(filter(None, [
                    lead.partner_id.street,
                    lead.partner_id.city,
                    lead.partner_id.zip
                ]))
            else:
                lead.address = False

    def _get_partner_address_update(self):
        """Custom function to determine if the address needs to be updated"""
        # Add your custom logic here to check whether the address should be updated
        # For example:
        return True

    @api.depends('partner_id.phone')
    def _compute_phone(self):
        for lead in self:
            if lead.partner_id.phone and lead._get_partner_phone_update():
                lead.phone = lead.partner_id.phone


    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_id and self.phone != self.partner_id.phone:
            lead_phone_formatted = self._phone_format(fname='phone') or self.phone or False
            partner_phone_formatted = self.partner_id._phone_format(fname='phone') or self.partner_id.phone or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    def action_approval(self):
        self.status = 'approval'

    def set_to_draft(self):
        self.status = 'draft'

    def create_qrf(self):
        self.status = 'sent'


    def b_in_progress(self):
        self.status = 'c_complete'

    def b_in_progress_to_c_complete(self):
        self.status = 'c_complete'

    def get_location(self):
        # Trigger the frontend action to fetch the user's current location
        return True


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
                raise ValidationError('You cannot delete the completed order contact To Admin or Rest To draft First .')


class middelTeamLine(models.Model):
    _name = 'middel.team.line'
    _description = 'middel Team Line'

    middel_team = fields.Many2one(
        comodel_name='middel.east',
        string=' Middel Team',
        required=False)
    team_id = fields.Many2one(
        comodel_name='middel.team',
        string='Team Name',
        compute = '_compute_team_name',
        required=False)
    time_work = fields.Integer(
        string='Time Work',
        required=False)
    time_cost = fields.Float(
        string='Time cost',
        related='team_id.time_cost', depends=['team_id'],
        required=False)
    total = fields.Monetary(
        string="Total",
        compute='_compute_price_reduce_taxexcl',
        currency_field='currency_id',
        store=True, precompute=True)

    amount_total = fields.Monetary(
            string="Total",
            compute='_compute_amount',
            currency_field='currency_id',
            store=True, precompute=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    name = fields.Char(string="Employee Code",  store=True, required=True)

    @api.depends('name', 'team_id')
    def _compute_team_name(self):
        for rec in self:
            if rec.name:
                rec.team_id = self.env['middel.team'].search([('id_employee', '=', rec.name)], limit=1)
            elif rec.team_id:
                for record in rec.team_id:
                    rec.name = record.id_employee


    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            line.update({
                'amount_total': line.amount_total + line.total,
            })

    @api.depends('time_cost', 'time_work' ,'total' )
    def _compute_price_reduce_taxexcl(self):
        for line in self:
            line.total = line.time_cost * line.time_work if line.time_work else 0.0



class MiddelCustomerNeed(models.Model):
    _name = 'middel.customer.need'
    _description = 'Middel Customer Need '


    product = fields.Many2one(
        comodel_name='middel.product',
        string='Product',
        domain="[('brand', '=', brand)]",
        required=False)
    middel_east_id = fields.Many2one(
        comodel_name='middel.east',
        string='Middel East',

        required=False)

    description = fields.Char(string="description", related='product.description', depends=['product'],
                              )
    model_no = fields.Char(string="Model No", related='product.model_no', depends=['product']
                           )

    price = fields.Float(
        string=' price',compute='_compute_price_unit', store=True, inverse='_set_price_unit',
        required=False)
    cost_price = fields.Float(string='Cost Price'
                              )
    margin_percent = fields.Float(string='Margin %',inverse='_set_price_unit', compute='_compute_margin_unit',
                                  )
    quantity = fields.Integer(
        string="Quantity",
        required=False)
    image = fields.Binary(
        string="Image",related='product.image', depends=['product'],
        required=False)

    product_category = fields.Many2one(
        comodel_name='middel.main.category',
        string='Product Category',
        required=False)

    product_sub = fields.Many2one(
        comodel_name='middel.sub.category',
        string='Product Sub Category',
        domain="[('main_Category', '=', product_category)]",
        required=False)

    brand = fields.Many2one(
        comodel_name='middel.brand',
        string='Brand',
        domain="[('product_sub', '=', product_sub)]",
        required=False)

    price_total = fields.Monetary(
        string="Total",
        compute='_compute_price_reduce_taxexcl',
        currency_field='currency_id')

    amount_total = fields.Monetary(
            string="Total",
            compute='_compute_amount',
        currency_field='currency_id',
             store=True)

    total_cost = fields.Monetary(
            string="Total Cost",
            compute='_compute_amount',
        currency_field='currency_id',
             store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)


    @api.depends('cost_price', 'margin_percent')
    def _compute_price_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.cost_price and line.margin_percent:
                line.price = line.cost_price * (1 + line.margin_percent / 100)
            else:
                line.price = line.product.price

    @api.depends('cost_price', 'price' , 'product')
    def _compute_margin_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.price:
                line.margin_percent = ((line.price - line.cost_price) / line.cost_price) * 100
            else:
                line.margin_percent = line.product.margin_percent

    def _set_price_unit(self):
        """ Inverse method to allow the price_unit to be set manually if necessary """
        for line in self:
            if line.cost_price:
                line.margin_percent = ((line.price - line.cost_price) / line.cost_price) * 100
            else:
                line.margin_percent = 0.0

    @api.onchange('product')
    def cost_change(self):
        self.cost_price = self.product.cost_price

    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            line.update({
                'amount_total': line.amount_total + line.price_total,
            })

    @api.depends('price', 'quantity' ,'price_total' )
    def _compute_price_reduce_taxexcl(self):
        for line in self:
            line.price_total = line.price * line.quantity if line.quantity else 0.0

class MiddelPetrolCharges(models.Model):
    _name = 'middel.petrol.charges'
    _description = 'Middel Petrol Charges'
    
    
    name = fields.Char(string="Name" , required=True)
    active = fields.Boolean(
        string='Active', 
        required=False)
    date = fields.Date(
        string='Date',
        required=True)
    charges = fields.Float(
        string='Charges',
        required=True)

    def toggle_active(self):
        for record in self:
            record.active = not record.active


class CompanyCost(models.Model):
    _name = 'middel.expense'
    _description = 'Company Cost'

    name = fields.Char(string="description")
    charges = fields.Float(
        string='Charges per Hours',
        required=True)


class ExpenseLine(models.Model):
    _name = 'middel.expense.line'
    _description = 'Company Cost'

    company_cost = fields.Many2one(
        comodel_name='middel.expense',
        string='Company Cost',
        required=False)

    middel_expense_id = fields.Many2one(
        comodel_name='middel.east',
        string='Middel Expense',
        required=False)

    charges = fields.Float(
        string='Charges per Hour',
        related='company_cost.charges',
        required=True)

    quantity = fields.Integer(
        string="Work Hours",
        related='middel_expense_id.works_hours',
        required=False)

    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        required=False)

    @api.depends('quantity', 'charges')
    def _compute_total_cost(self):
        """Computes the total cost based on the charges and quantity of work hours."""
        for line in self:
            line.total_cost = line.charges * line.quantity if line.quantity else 0.0
