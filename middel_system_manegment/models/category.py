from importlib.metadata import requires

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty


class MiddelProductCategory(models.Model):
    """product Category"""

    _inherit = "product.category"

    active = fields.Boolean(string="Active",default=True )

class MiddelEastCategory(models.Model):
    """Middel East Main Category"""

    _name = "middel.main.category"
    _description = "Middle Main Category"
    _rec_name = 'name'

    name = fields.Char(string="Category Name", required=True)
    active = fields.Boolean(string="Active",default=True )

    @api.constrains('name')
    def _check_name_is_capital(self):
        for record in self:
            if record.name and not record.name.isupper():
                raise ValidationError("The Name Must Be all Capital Letter  OR Fill The Name  ")

class MiddelEastSubcategory(models.Model):
    """Middel East Sub Category"""
    _name = "middel.sub.category"
    _description = "Middle Sub Category"
    _rec_name = 'name'

    name = fields.Char(string="Sub Category Name", required=True)
    active = fields.Boolean(string="Active",default=True )
    main_Category=fields.Many2one('middel.main.category',string="Main Category" , required=True)
    brand=fields.Many2one('middel.brand',string="Brand" , required=True)

    @api.constrains('name')
    def _check_name_is_capital(self):
        for record in self:
            if record.name and not record.name.isupper():
                raise ValidationError("The Name Must Be all Capital Letter  OR Fill The Name  ")

class MiddelEastBrand(models.Model):
    """Middel East Brand"""
    _name = "middel.brand"
    _description = "Middle Brand"
    _rec_name = 'name'

    name = fields.Char(string="Brand Name", required=True)
    active = fields.Boolean(string="Active",default=True )
    product_sub = fields.Many2one(
        comodel_name='middel.sub.category',
        string='Product Sub',
        required=False)

    category_id = fields.One2many(
        'product.template','brand',
        string='Product Category',
        required=False)

    image = fields.Binary(
        string="Image",
        required=False)

    @api.constrains('name')
    def _check_name_is_capital(self):
        for record in self:
            if record.name and not record.name.isupper():
                raise ValidationError("The Name Must Be all Capital Letter  OR Fill The Name  ")
