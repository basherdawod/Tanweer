# models/maintenance.py
from odoo import models, fields

class Maintenance(models.Model):
    _name = 'middel.maintenance'
    _description = 'Maintenance Contract'

    name = fields.Char(string='Contract Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Maintenance Frequency')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
