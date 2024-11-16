from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PreExpTestCategory(models.Model):
    _name = 'pre.exp.test.category'
    _description = 'Prepaid Expense Test Category'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', store=True)
    code = fields.Char(string='Category Code', required=True)
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(string='Active', default=True)
    parent_id = fields.Many2one('pre.exp.test.category', string='Parent Category', ondelete='restrict', index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('pre.exp.test.category', 'parent_id', string='Child Categories')
    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    expense_account_id = fields.Many2one('account.account', string='Expense Account', required=True)
    prepaid_account_id = fields.Many2one('account.account', string='Prepaid Account', required=True)
    method_period = fields.Integer(string='Period Length', default=1, help="Duration in months of each period")

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursive categories.')

    @api.constrains('method_period')
    def _check_method_period(self):
        for record in self:
            if record.method_period <= 0:
                raise ValidationError("Period Length must be greater than zero.")

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]