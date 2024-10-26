from collections import defaultdict
from odoo.osv import expression
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.addons.phone_validation.tools import phone_validation
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import float_is_zero, float_compare, float_round, format_date, groupby


class MiddelService(models.Model):
    """Middel Service"""
    _name = "middel.service.line"
    _description = 'Middel service Line'


    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        domain="[('brand', '=', brand)]"  # Filter products by the selected brand
    )
    product_type = fields.Selection(related='product_id.detailed_type')

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

    margin_percent = fields.Monetary(
        string="Margin %",
        currency_field='currency_id',
        related='product_order_line.margin_amount',
        store=True)

    image = fields.Binary(
        string="Image",related="product_id.image_1920",
        required=False)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    product_order_line = fields.Many2one('middel.quotation', string='Middel quotation')

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

    sevice_amount = fields.Monetary(
        string="service Amount",
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
            if line.product_type == 'service':
                line.price_total =  line.sevice_amount if line.sevice_amount else 0.0
            else:
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

    @api.depends('standard_price', 'margin_percent', 'sevice_amount', 'product_type')
    def _compute_price_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.product_type == "service":
                line.list_price = float(line.sevice_amount) if line.sevice_amount else 0.0
            elif line.standard_price and line.margin_percent:
                line.list_price = line.standard_price * (1 + line.margin_percent / 100)
            else:
                line.list_price = float(line.sevice_amount) if line.sevice_amount else 0.0

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


