# models/visitor_schedule.py
from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class VisitorSchedule(models.Model):
    _name = 'visitor.schedule'
    _description = 'Visitor Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Visitor Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    visit_date = fields.Date(string='Next Visit Date', required=True)
    recurring_day = fields.Integer(string='Recurring Day of Month', required=True)
    team_id = fields.Many2one('res.users', string='Assigned Team', required=True)
    user_id = fields.Many2one('res.users', string='Assigned User', default=lambda self: self.env.user)

    @api.model
    def schedule_next_visit(self):
        today = fields.Date.context_today(self)
        visitors = self.search([])

        for visitor in visitors:
            if visitor.visit_date and visitor.visit_date <= today:
                next_visit_date = self._calculate_next_visit_date(visitor.recurring_day)
                visitor.write({'visit_date': next_visit_date})

    @staticmethod
    def _calculate_next_visit_date(day):
        today = datetime.today()
        next_month = today.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        next_visit_date = next_month.replace(day=day)
        return next_visit_date

    @api.model
    def create(self, vals):
        if vals.get('recurring_day') not in range(1, 32):
            raise exceptions.UserError('Please select a valid day of the month (1-31).')
        return super(VisitorSchedule, self).create(vals)

    def _check_access_rights(self):
        if not self.env.user.has_group('visitor_schedule.group_admin'):
            self.ensure_one()
            if self.user_id != self.env.user and self.team_id != self.env.user:
                raise exceptions.AccessError("You do not have permission to access this visitor.")
