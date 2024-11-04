from odoo import models, fields, api

class VatDeclarationLineDemo(models.Model):
    _name = 'vat.declaration.line.demo'
    _description = 'Demo Data for VAT Declaration Line'

    @api.model
    def create_demo_data(self):
        # البحث عن الفاتورة (VAT Declaration) المراد الربط بها
        declaration = self.env['vat.declaration'].search([], limit=1)
        
        if declaration:
            # إنشاء بيانات تجريبية
            demo_data = [
                {
                    'declaration_id': declaration.id,
                    'description': 'Sales for November',
                  
                },
                {
                    'declaration_id': declaration.id,
                    'description': 'Office Supplies',
                   
                },
                {
                    'declaration_id': declaration.id,
                    'description': 'Sales for December',
                    
                }
            ]

            # إنشاء السجلات
            for data in demo_data:
                self.create(data)

# يجب استدعاء هذه الدالة في مكان ما لتحميل البيانات التجريبية
