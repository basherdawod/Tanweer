from collections import defaultdict
from odoo.osv import expression
from odoo import models, fields, api, _


class MiddelExpense(models.Model):
    _inherit = "hr.expense"

    middel_expense_id = fields.Many2one('middel.east', string="Middel Expense", ondelete='cascade')



