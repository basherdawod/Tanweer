from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty


class MiddelProduct(models.Model):
    """Middel East Team"""
    _name = "middel.product"
    _description = 'Middel Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name",
                       required=True)
    description = fields.Char(string="description",
                              required=True)
    model_no = fields.Char(string="Model No" ,
                              required=True)
    cost_price = fields.Float(string='Cost Price'
                              , store=True)
    margin_percent = fields.Float(string='Margin %',
                                  store=True)
    price = fields.Float(string='Price',
                         compute='_compute_price_unit', store=True, inverse='_set_price_unit')
    image = fields.Binary(
        string="Image" ,
        required=False)
    active = fields.Boolean(
        string='Item Active',
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

    # validation methods For the product inform
    @api.constrains('name','product_category')
    def _check_name_is_not_null(self):
        for record in self:
            if record.name == 'null':
                raise ValidationError("Fill The Name ")
            if record.product_category == 'null':
                raise ValidationError("Add Product Category .")


    @api.depends('cost_price', 'margin_percent')
    def _compute_price_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.cost_price and line.margin_percent:
                line.price = line.cost_price * (1 + line.margin_percent / 100)
            else:
                line.price = 0.0

    def _set_price_unit(self):
        """ Inverse method to allow the price_unit to be set manually if necessary """
        for line in self:
            if line.cost_price:
                line.margin_percent = ((line.price - line.cost_price) / line.cost_price) * 100
            else:
                line.margin_percent = 0.0
