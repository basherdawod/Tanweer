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
    makani = fields.Char(string="Makani Number" , required=True)
    margin_amount = fields.Float(
            string="Margin %",
            default=30.0 ,
            store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    phone = fields.Char(
        'Phone', tracking=50,
         compute='_compute_phone', readonly=True, store=True)

    refrenc_c = fields.Char(string="Code", readonly=True, )

    location = fields.Char(string="Customer Map Location")
    date = fields.Date(string="Date", default=fields.date.today(), required=True)
    status = fields.Selection(
        [('draft', "Draft"),('waiting', "waiting for visiting"), ('sent', "Quotations"), ('approval', "Approval"),
         ('c_complete', "Complete")],
        string="Status", default='draft')

    quotation_count = fields.Integer(compute='_compute_sale_data', string="Number of Quotations")


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
        default= 'No',
        required=False)

    customer_need_amc = fields.Selection(
        string=' Customer Need AMC ',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        default='No',
        required=False )

    customer_need_management = fields.Selection(
        string=' Customer Need AMC ',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        default='No',
        required=False )

    customer_need_drawing = fields.Selection(
        string=' Customer Need Drawing',
        selection=[('yes', 'Yes'),
                   ('No', 'NO'), ],
        default='No',
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


    m_order_line_ids = fields.One2many(
            comodel_name='middel.order.line',
            inverse_name='middel_m_order_id',
            string='Customer Need',
            required=False)

    middel_expense_line = fields.One2many(
        comodel_name='middel.expense.line',
        inverse_name='middel_expense_id',
        string='Company Expense Cost',
        required=False)

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
        compute='_compute_team_works_amount',
            store=True)

    total_amount_employee = fields.Monetary(
                string="Employee Total Amount",
            currency_field='currency_id',
            compute='_compute_team_works_amount',
                store=True)

    company_total_amount = fields.Monetary(
            string="Company Total Amount",
            currency_field='currency_id',
            compute='_compute_expenses_amount',
            store=True)

    company_cost_amount = fields.Monetary(
            string="Company Total Cost",
            currency_field='currency_id',
            compute='_compute_expenses_amount',
            store=True)

    cost_total_amount = fields.Monetary(
            string="Company Total Cost",
            currency_field='currency_id',
            store=True)
    total_amount = fields.Monetary(
                string="Total Amount",
                currency_field='currency_id',
                compute='_compute_amount_line_order',
                store=True)

    total_cost_project = fields.Monetary(
        string="Total Project Cost",
        currency_field='currency_id',
        compute='_total_project_cost_compute',
        store=True)

    total_project_amount = fields.Monetary(
        string="Lowest Project Amount",
        currency_field='currency_id',
        compute='_total_project_amount',
        store=True)

    total_expense_line_amount = fields.Monetary(
            string="Expense Line Amount",
            currency_field='currency_id',
            compute='_total_project_amount',
            store=True)

    product_cost_amount = fields.Monetary(
        string="Product Cost Amount",
        currency_field='currency_id',
        compute='_compute_product_cost_amount',
        store=True)

    petrol_Charges = fields.Many2one(
        comodel_name='middel.petrol.charges',
        string='Petrol Charges',store=True,
        required=True)

    distance = fields.Integer(
        string='Distance K/M',
        required=False)

    petrol_cost = fields.Monetary(string="Petrol Cost" ,store=True, currency_field='currency_id', compute="_petrol_cont_compute")

    visits = fields.Integer(
        string='Visits No',
        required=False)


    works_hours = fields.Integer(
        string='Works Hours',
        required=False)

    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        store=True,
        readonly=True,
        compute='_compute_amount_line_order'
    )

    amount_tax = fields.Monetary(
        string='Tax',
        store=True,
        readonly=True,
        compute='_compute_amount_line_order'
    )


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

    def write(self, vals):
        # Iterate through the records being updated
        for record in self:
            # Check if the current status is 'approval' or 'c_complete'
            if record.status in ('approval', 'c_complete'):
                # If the record is being set to draft, allow the operation
                if 'status' in vals and vals['status'] == 'draft':
                    continue
                # If the record is not being set to draft, raise an error
                raise UserError("You cannot edit this record because it is confirmed.")
        # Call the super method to perform the actual write operation
        return super(MiddelEast, self).write(vals)

    def set_to_draft(self):
        # Set the record's status to 'draft'
        self.write({'status': 'draft'})
        return True  # Indicate that the status was set to draft

    @api.depends('company_cost_amount', 'total_cost_employee', 'product_cost_amount')
    def _total_project_cost_compute(self):
        for record in self:
            record.total_cost_project = (record.company_cost_amount or 0.0) + (record.total_cost_employee or 0.0)+ (record.product_cost_amount or 0.0)

    @api.depends('company_total_amount', 'total_amount_employee', 'total_amount')
    def _total_project_amount(self):
        for record in self:
            record.total_project_amount = (record.company_total_amount or 0.0) + (record.total_amount_employee or 0.0)+ (record.total_amount or 0.0)
            record.total_expense_line_amount = (record.company_total_amount or 0.0) + (record.total_amount_employee or 0.0)

    def _compute_sale_data(self):
        for rec in self:
            q_count = self.env['middel.quotation'].search_count([('middel_quotation_id', '=', rec.id)])
            rec.quotation_count = q_count


    @api.constrains('makani')
    def _check_makani_is_numeric(self):
        """Ensure that the Makani number contains only digits."""
        for record in self:
            if record.makani and not record.makani.isdigit():
                raise ValidationError("Makani number should contain only digits.")

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

    @api.depends('middel_expense_line', 'middel_expense_line.total_cost')
    def _compute_expenses_amount(self):
        for sheet in self:
            sheet.company_cost_amount = sum([line.sub_total_amount for line in sheet.middel_expense_line])
            sheet.company_total_amount = sum([line.total_cost for line in sheet.middel_expense_line])

    @api.depends('team_work', 'team_work.total')
    def _compute_team_works_amount(self):
        for sheet in self:
            sheet.total_cost_employee = sum([line.total for line in sheet.team_work])
            sheet.total_amount_employee = sum([line.sub_amount_total for line in sheet.team_work])

    @api.depends('m_order_line_ids', 'm_order_line_ids.total_cost_amount')
    def _compute_product_cost_amount(self):
        for sheet in self:
            sheet.product_cost_amount = sum([line.total_cost_amount for line in sheet.m_order_line_ids])

    @api.depends('m_order_line_ids.price_subtotal', 'm_order_line_ids.price_tax', 'm_order_line_ids.price_total',
                 'm_order_line_ids.tax_ids')
    def _compute_amount_line_order(self):
        """Compute the total amounts of the order, including untaxed amount, tax, and total."""
        for order in self:
            # Initialize amounts
            amount_untaxed = 0.0
            amount_tax = 0.0

            # Loop through each order line to compute the amounts
            for line in order.m_order_line_ids:
                amount_untaxed += line.price_subtotal  # Sum up untaxed amounts
                amount_tax += line.price_tax  # Sum up tax amounts

            # Update the order totals
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.total_amount = amount_untaxed + amount_tax

    def action_create_quotation(self):
        middel_list = []

        # Collect Product Lines
        for data in self.m_order_line_ids:
            order_lines = {
                'product_id': data.product_id.id,
                'description': data.description,
                'categ_id': data.categ_id.id,
                'brand': data.brand.id,
                'model_no': data.model_no,
                'standard_price': data.standard_price,
                'margin_percent': data.margin_percent,
                'quantity': data.quantity,
                'list_price': data.list_price,
                'price_total': data.price_total,
                'amount_total': data.amount_total,
            }
            middel_list.append(Command.create(order_lines))

        # Collect Service Line (assuming total expense is stored in `total_expense_line_amount`)
        service_line = {
            'description': 'service',
            'product_type': "service",
            'sevice_amount': self.total_expense_line_amount,
        }
        middel_list.append(Command.create(service_line))

        # Create Quotations with Unique Names
        for record in self:
            existing_quotations = record.quotation_ids
            if not existing_quotations:
                quotation_name = record.name
            else:
                next_letter = chr(65 + len(existing_quotations))  # ASCII 'A' is 65
                quotation_name = f"{record.name}/{next_letter}"

            # Create the new quotation record
            quotation = self.env['middel.quotation'].create({
                'name': quotation_name,
                'partner_id': record.partner_id.id,
                'middel_quotation_id': record.id,
                'country_id': record.country_id.id,
                'state_id': record.state_id.id,
                'phone': record.phone,
                'project': record.project,
                'margin_amount': record.margin_amount,
                'makani': record.makani,
                'total_project_amount': record.total_project_amount,
                'customer_need_cid': record.customer_need_cid,
                'customer_need_amc': record.customer_need_amc,
                'approch': record.approch,
                'order_product_line_ids': middel_list,  # Attach order lines
            })

            # Log the creation in chatter
            record.message_post(body=f"Quotation {quotation.name} has been created.")

        # Call any additional method like `create_qrf` if necessary
        self.create_qrf()

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
    #
    # def set_to_draft(self):
    #     self.status = 'draft'

    def create_qrf(self):
        self.status = 'sent'

    def b_c_complete(self):
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

    margin_amount = fields.Float(
        string="Margin %",
        currency_field='currency_id',
        related='middel_team.margin_amount',
        store=True)

    amount_total = fields.Monetary(
            string="Total",
            compute='_compute_amount',
            currency_field='currency_id',
            store=True, precompute=True)

    sub_amount_total = fields.Monetary(
            string="Total Amount",
            compute='_compute_sub_amount_total',
            currency_field='currency_id',
            store=True)

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

    #
    # @api.depends('margin_amount', 'middel_team')
    # def _compute_margin_amount(self):
    #     """Computes the total cost based on the charges and quantity of work hours."""
    #     for record in self:
    #         # Initialize margin  amount
    #         if record.middel_team :
    #             record.margin_amount =record.middel_team[0].margin_amount


    @api.depends('time_work','time_cost', 'margin_amount')
    def _compute_sub_amount_total(self):
        """Computes the total cost based on the charges, margin amount, and quantity."""
        for line in self:
            if line.time_work:
                # Applying the margin to charges
                margin_multiplier = 1 + (line.margin_amount / 100)
                line.sub_amount_total = line.time_cost * margin_multiplier * line.time_work
            else:
                line.sub_amount_total = 0.0


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
        compute='_compute_charges_expenses',
        required=True)

    margin_amount = fields.Float(
        string="Margin %",
        currency_field='currency_id',
        related='middel_expense_id.margin_amount',
        store=True)

    quantity = fields.Integer(
        string="Work Hours",
        compute='_compute_charges_quantity',
        required=False)
    petrol = fields.Monetary(
        string="Work Hours",
        currency_field='currency_id',
        related='middel_expense_id.petrol_cost',
        required=False)
    sub_total_amount = fields.Monetary(
        string=" Sub Total Amount",
        currency_field='currency_id',
        compute='_compute_sub_total_amount',
        store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)


    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_total_cost',
        currency_field='currency_id',
        store=True,
        required=False)

    @api.depends('company_cost', 'charges', 'middel_expense_id')
    def _compute_charges_expenses(self):
        """Computes the total cost based on the charges and quantity of work hours."""
        for record in self:
            # Initialize charges
            record.charges = 0

            # Check if company_cost has multiple records and iterate over them
            for res in record.company_cost:
                if res.name == 'petrol':
                    # Handle potential multiple middel_expense_id records
                    if record.petrol:
                        record.charges += record.petrol  # Using the first record if multiple exist
                else:
                    record.charges += res.charges


    @api.depends('company_cost', 'quantity', 'middel_expense_id')
    def _compute_charges_quantity(self):
        """Computes the total cost based on the charges and quantity of work hours."""
        for record in self:
            # Initialize charges
            record.quantity = 0

            # Check if company_cost has multiple records and iterate over them
            for res in record.company_cost:
                if res.name == 'petrol':
                    # Handle potential multiple middel_expense_id records
                    if record.middel_expense_id:
                        record.quantity +=1  # Using the first record if multiple exist
                else:
                    record.quantity +=record.middel_expense_id[
                            0].works_hours

    @api.depends('quantity', 'charges', 'margin_amount')
    def _compute_total_cost(self):
        """Computes the total cost based on the charges, margin amount, and quantity."""
        for line in self:
            if line.quantity:
                # Applying the margin to charges
                margin_multiplier = 1 + (line.margin_amount / 100)
                line.total_cost = line.charges * margin_multiplier * line.quantity
            else:
                line.total_cost = 0.0

    @api.depends('quantity', 'charges')
    def _compute_sub_total_amount(self):
        """Computes the total cost based on the charges and quantity of work hours."""
        for line in self:
            line.sub_total_amount = line.charges  * line.quantity  if line.quantity else 0.0


class MiddelOrderProuduct(models.Model):
    """Middel Service"""
    _name = "middel.order.line"
    _description = 'Middel order Line'


    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        domain="[('brand', '=', brand)]"  # Filter products by the selected brand
    )


    description = fields.Char(string="description",
                              )
    model_no = fields.Char(string="Model No" ,
                            )

    product_category = fields.Many2one(
        comodel_name='middel.main.category',
        string='Product Category',
        required=False)
    quantity = fields.Integer(
        string="Quantity",default=1.0,
        required=False)

    product_sub = fields.Many2one(
        comodel_name='middel.sub.category',
        string='Product Sub Category',
        required=False)


    brand = fields.Many2one(
        comodel_name='middel.brand',
        string='Brand',
        domain="[('category_id', '=', categ_id)]"  # Filter brands by selected category
    )
    list_price = fields.Float(
        'Product Price', default=0.0,compute='_compute_price_unit',
        help="Price at which the product is sold to customers.",
    )
    standard_price = fields.Float(
        'Cost',
        digits='Product Cost',
        help="""Value of the product (automatically computed in AVCO).
           Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
           Used to compute margins on sale orders.""")
    categ_id = fields.Many2one(
        'product.category', 'Product Category',)

    margin_percent = fields.Float(
        string="Margin %",
        currency_field='currency_id',
        related='middel_m_order_id.margin_amount',
        store=True)

    image = fields.Binary(
        string="Image",related="product_id.image_1920",
        required=False)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    middel_m_order_id = fields.Many2one('middel.east', string='Middel Reference' , ondelete='cascade')


    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    price_total = fields.Monetary(
        string="Total",
        compute='_compute_price_reduce_taxincl',
        currency_field='currency_id',
        store=True, precompute=True)

    price_subtotal = fields.Monetary(
        string="Untaxed Amount",
        compute='_compute_amount',
        store=True
    )

    price_tax = fields.Monetary(
        string="Tax Amount",
        compute='_compute_amount',
        store=True
    )

    amount_total = fields.Monetary(
            string="Total",
            compute='_compute_amount',
        currency_field='currency_id',
            store=True)

    total_line_amount = fields.Monetary(
        string="Total Line Amount",
        compute='_compute_total_line_amount',
        currency_field='currency_id',
        store=True
    )

    total_cost_amount = fields.Monetary(
        string="Total Cost Amount",
        compute='_compute_total_cost_amount',
        currency_field='currency_id',
        store=True
    )

    discount = fields.Float(string='Discount (%)', default=0.0)
    tax_ids = fields.Many2many('account.tax', string='Taxes')


    @api.depends('price_subtotal', 'price_tax')
    def _compute_total_line_amount(self):
        """Compute the total amount for the line, including both untaxed amount and taxes."""
        for line in self:
            line.total_line_amount = line.price_subtotal + line.price_tax

    @api.depends('list_price', 'quantity', 'discount')
    def _compute_price_reduce_taxincl(self):
        for line in self:
            discount_amount = (line.discount / 100) * line.list_price
            line.price_total = (line.list_price - discount_amount) * line.quantity if line.quantity else 0.0

    @api.depends('list_price', 'quantity', 'discount', 'tax_ids')
    def _compute_amount(self):
        """Compute the untaxed amount, tax amount, and total amount."""
        for line in self:
            # Calculate discount
            discount_amount = (line.discount / 100) * line.list_price
            price_after_discount = line.list_price - discount_amount

            # Untaxed amount (subtotal)
            line.price_subtotal = price_after_discount * line.quantity

            # Tax computation
            taxes = line.tax_ids.compute_all(line.price_subtotal, currency=line.currency_id)

            # Tax amount
            line.price_tax = taxes['total_included'] - taxes['total_excluded']

            # Total amount including taxes
            line.amount_total = taxes['total_included']



    @api.depends('standard_price', 'quantity',)
    def _compute_total_cost_amount(self):
        """Compute the cost total amount."""
        for line in self:
            # cost total amount
            line.total_cost_amount = line.standard_price * line.quantity


    @api.depends('standard_price', 'margin_percent')
    def _compute_price_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.standard_price and line.margin_percent:
                line.list_price = line.standard_price * (1 + line.margin_percent / 100)
            else:
                line.list_price = line.product_id.list_price

    @api.onchange('categ_id')
    def _onchange_product_category(self):
        """Update the brand field domain based on the selected product category."""
        self.brand = False  # Clear the brand selection when category changes
        return {
            'domain': {
                'brand': [('category_id', '=', self.categ_id.id)]
            }
        }

    @api.onchange('brand')
    def _onchange_brand(self):
        """Update the product field domain based on the selected brand."""
        self.product_id = False  # Clear the product selection when brand changes
        return {
            'domain': {
                'product_id': [('brand', '=', self.brand.id)]
            }
        }

    @api.onchange('product_id')
    def _update_data_fields(self):
        """Update fields based on the selected product."""
        if self.product_id:
            self.description = self.product_id.description
            self.model_no = self.product_id.model_no
            self.standard_price = self.product_id.standard_price
            self.list_price = self.product_id.list_price


