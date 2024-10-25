from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty


class MiddelProduct(models.Model):
    """Middel East Team"""
    _inherit = 'product.template'
    _description = 'Middel Product Template'

    description = fields.Char(string="description",
                              )
    model_no = fields.Char(string="Model No" ,
                            )
    margin_percent = fields.Float(string='Margin %',
                                  store=True)

    active = fields.Boolean(
        string='Item Active',
        required=False)

    product_category = fields.Many2one(
        comodel_name='middel.main.category',
        string='Main Category',
        required=False)

    product_sub = fields.Many2one(
        comodel_name='middel.sub.category',
        string='Product Sub Category',
        required=False)

    brand = fields.Many2one(
            comodel_name='middel.brand',
            string='Brand',
            required=False)

    @api.onchange('standard_price', 'margin_percent')
    def _compute_price_unit(self):
        """ Compute the Sales Price based on the Cost Price and Margin % """
        for line in self:
            if line.standard_price and line.margin_percent:
                line.list_price = line.standard_price * (1 + line.margin_percent / 100)
            else:
                line.list_price = 0.0
