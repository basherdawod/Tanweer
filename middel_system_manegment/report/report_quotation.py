from odoo import models

class MiddelQuotationReport(models.AbstractModel):
    _name = 'report.middel.quotation.report_quotation_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['middel.quotation'].browse(docids)
        return {
            'docs': docs,
        }

class MiddelVisitorEstm(models.AbstractModel):
    _name = 'report.middel.east.report_middel_east_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['middel.east'].browse(docids)
        return {
            'docs': docs,
        }

class MiddelVisitorForm(models.AbstractModel):
    _name = 'report.middel.east.report_middel_visitor_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['middel.east'].browse(docids)
        return {
            'docs': docs,
        }
