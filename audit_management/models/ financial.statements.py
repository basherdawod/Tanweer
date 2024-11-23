from odoo import api, fields, models, _, tools, Command

class ComprehensiveIncome(models.Model):
    _name = 'financial.statements' #model_financial_statements
    _description = 'Financial Statements'