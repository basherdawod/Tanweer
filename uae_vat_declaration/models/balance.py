from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    corporate_tax_id = fields.Many2one('corporate.tax')
    total_balance = fields.Float(string="Total Balance") 

    @api.model
    def get_total_balance(self):
        total_balance = 0
        accounts = self.search([])  # البحث في كل الحسابات
        for account in accounts:
            total_balance += account.total_balance  # إضافة الرصيد لكل حساب
        
        # تحديث total_balance لكل السجلات التي تم البحث عنها
        accounts.write({
            'total_balance': total_balance,
        })
        
        return total_balance  # إعادة القيمة المحسوبة

