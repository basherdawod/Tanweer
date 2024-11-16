from odoo import http
from odoo.http import request

class VatReportController(http.Controller):
    @http.route('/vat_declaration/excel_report', type='http', auth='user')
    def download_vat_excel_report(self, record_id):
        record = request.env['vat.declaration'].sudo().browse(int(record_id))
        if record.exists():
            return record.action_generate_vat_excel_report()
        return request.not_found()
