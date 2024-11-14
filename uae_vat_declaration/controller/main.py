from odoo import http
from odoo.http import request
import base64

class VatReportController(http.Controller):

    @http.route('/report/vat_xlsx/<int:record_id>', type='http', auth="user")
    def download_vat_xlsx(self, record_id, **kwargs):
        # Fetch the VAT declaration record using the ID from the URL
        vat_declaration = request.env['vat.declaration'].sudo().browse(record_id)
        
        if not vat_declaration.exists():
            return request.not_found()  # Return a 404 error if the record is not found

        # Call the method to generate the Excel report
        report_data = vat_declaration.action_generate_vat_excel_report()

        # Prepare the filename
        filename = f"{vat_declaration.name or 'VAT Report'}.xlsx"
        
        # Send the Excel file content as a response
        return request.make_response(
            base64.b64decode(report_data['file_content']),  # Decode the file content
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={filename}')
            ]
        )
