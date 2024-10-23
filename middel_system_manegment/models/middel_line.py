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
    _description = 'Middel order Line'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product"
    )

    description = fields.Char(string="description",
                              )
    model_no = fields.Char(string="Model No",
                           )

    product_category = fields.Many2one(
        comodel_name='middel.main.category',
        string='Product Category',
        required=False)
    quantity = fields.Integer(
        string="Quantity", default=1.0,
        required=False)

    product_sub = fields.Many2one(
        comodel_name='middel.sub.category',
        string='Product Sub Category',
        required=False)

    brand = fields.Many2one(
        comodel_name='middel.brand',
        string='Brand',
        required=False)
    list_price = fields.Float(
        'Product Price', default=0.0, compute='_compute_price_unit', inverse='_set_price_unit',
        help="Price at which the product is sold to customers.",
    )
    standard_price = fields.Float(
        'Cost',
        digits='Product Cost',
        help="""Value of the product (automatically computed in AVCO).
            Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
            Used to compute margins on sale orders.""")
    categ_id = fields.Many2one(
        'product.category', 'Product Category', )
    margin_percent = fields.Float(string='Margin %', inverse='_set_price_unit', compute='_compute_margin_unit',
                                  )
    image = fields.Binary(
        string="Image", related="brand.image",
        required=False)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    product_order_line = fields.Many2one('middel.quotation', string='Middel quotation')

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    price_total = fields.Monetary(
        string="Total",
        compute='_compute_price_reduce_taxexcl',
        currency_field='currency_id',
        store=True, precompute=True)

    amount_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        currency_field='currency_id',
        store=True, precompute=True)

    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            line.update({
                'amount_total': line.amount_total + line.price_total,
            })

    @api.depends('standard_price', 'margin_percent')
    def _compute_price_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.standard_price and line.margin_percent:
                line.list_price = line.standard_price * (1 + line.margin_percent / 100)
            else:
                line.list_price = line.product_id.list_price

    @api.depends('standard_price', 'list_price', 'product_id')
    def _compute_margin_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.list_price:
                line_price = ((line.list_price - line.standard_price) / line.standard_price) * 100
                if line_price >= 1:
                    line.margin_percent = line_price
                else:
                    line.margin_percent = -line_price
            else:
                line.margin_percent = line.product_id.margin_percent

    def _set_price_unit(self):
        """ Inverse method to allow the price_unit to be set manually if necessary """
        for line in self:
            if line.standard_price:
                line.margin_percent = ((line.list_price - line.standard_price) / line.standard_price) * 100
            else:
                line.margin_percent = 0.0

    @api.depends('list_price', 'quantity', 'price_total')
    def _compute_price_reduce_taxexcl(self):
        for line in self:
            line.price_total = line.list_price * line.quantity if line.quantity else 0.0

    @api.onchange('product_id')
    def _update_data_fields(self):
        if self.product_id:
            for line in self:
                line.description = line.product_id.description
                line.model_no = line.product_id.model_no
                line.product_sub = line.product_id.product_sub
                line.brand = line.product_id.brand
                line.standard_price = line.product_id.standard_price
                line.list_price = line.product_id.list_price
                line.categ_id = line.product_id.categ_id
                line.margin_percent = line.product_id.margin_percent