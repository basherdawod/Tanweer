from odoo import models

class MiddelQuotationReport(models.AbstractModel):
    _name = 'report.middel.quotation.report_quotation_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['middel.quotation'].browse(docids)
        return {
            'docs': docs,
        }
