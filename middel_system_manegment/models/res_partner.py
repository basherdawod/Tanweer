
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.osv import expression
import re

class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = __doc__

    reference_no = fields.Char(string='Customer Reference', required=True,
                               readonly=True, default=lambda self: _('New'))

    @api.constrains('phone')
    def _check_phone(self):
        pattern_with_plus = re.compile(r'^\+?[0-9]{12}$')  # If + is used, 12 digits should follow
        pattern_without_plus = re.compile(r'^[0-9]{10}$')  # If no +, only 10 digits are allowed

        for record in self:
            if record.phone:
                # If the number starts with `+`, ensure it matches the 12-digit rule
                if record.phone.startswith('+'):
                    if not pattern_with_plus.match(record.phone):
                        raise ValidationError(
                            "Phone number must be in the format '+XXXXXXXXXXXX' with exactly 12 digits.")
                else:
                    # Else, ensure it matches the 10-digit rule
                    if not pattern_without_plus.match(record.phone):
                        raise ValidationError("Phone number must contain exactly 10 digits if not using '+'.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference_no', _('New')) == _('New'):
                vals['reference_no'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')
        res = super(ResPartner, self).create(vals_list)
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=10000,
                     order=None):
        args = args or []
        domain = ['|', '|', '|','|', ('name', operator, name),
                  ('phone', operator, name), ('email', operator, name),('ref', operator, name),
                  ('mobile', operator, name)]
        return self._search(expression.AND([domain + args]), limit=limit, order=order)
