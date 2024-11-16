from odoo import models

class ProgramAuditReport(models.AbstractModel):
    _name = 'report.audit.program.report_audit_program_line_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['audit.program'].browse(docids)
        return {
            'docs': docs,
        }
