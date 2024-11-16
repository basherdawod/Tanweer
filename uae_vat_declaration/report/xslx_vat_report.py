import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date ,timedelta
from odoo.http import content_disposition, request
import base64
import io
import xlsxwriter
from io import BytesIO
from xlsxwriter import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.tools import date_utils


	class XslxVatReport(http.Controller):
		@http.route('/vat/excel/report', type='http',auth='user')
		def download_vat_report(self):
			output = io.BytesIO()
			Workbook = xlsxwriter.Workbook(output, {'in_memory' : True})
			worksheet = Workbook.add_worksheet('Vat Report')

			# header_format = Workbook.add_format({'bold':True},'bg_color':'#D3D3D3','border':1,'align':'center')
			# worksheet = workbook.add_worksheet("VAT 201 Return Report")

	        # Define formats for headers and currency
	        bold = workbook.add_format({'bold': True})
	        currency_format = workbook.add_format({'num_format': '#,##0.00'})

	        # Header section
	        worksheet.write("A1", "VAT 201 Return", bold)
	        worksheet.write("A2", "Ref:", bold)
	        worksheet.write("B2", self.name if self.name else "N/A")  # Check for empty reference
	        worksheet.write("A3", "Date:", bold)
	        worksheet.write("B3", self.date_from.strftime('%Y-%m-%d') if self.date_from else "N/A")  # Format date if available
	        worksheet.write("A4", "Tax Registration Number (TRN):", bold)
	        worksheet.write("B4", self.trn if self.trn else "N/A")  # Check TRN
	        worksheet.write("A5", "Legal Name in English:", bold)
	        worksheet.write("B5", self.legal_name if self.legal_name else "N/A")  # Check legal name

	        # Column headers for Supplies Section
	        worksheet.write("A7", "Description", bold)
	        worksheet.write("B7", "Amount (AED)", bold)
	        worksheet.write("C7", "VAT Amount (AED)", bold)
	        worksheet.write("D7", "Adjustment (AED)", bold)
 
	        # Add data rows from `vat_sales_outputs`
	        vat_sales_outputs = self.vat_sales_outputs
	        start_row = 8
	        row = start_row
	        for line in vat_sales_outputs:
	            worksheet.write(row, 0, line.description or "N/A")  # Provide fallback for empty description
	            worksheet.write(row, 1, line.amount, currency_format)
	            worksheet.write(row, 2, line.taxamount, currency_format)
	            worksheet.write(row, 3, line.adjustment, currency_format)
	            row += 1

	        # Totals Row
	        worksheet.write(row, 0, "Total", bold)
	        worksheet.write_formula(row, 1, f"SUM(B{start_row}:B{row})", currency_format)
	        worksheet.write_formula(row, 2, f"SUM(C{start_row}:C{row})", currency_format)
	        worksheet.write_formula(row, 3, f"SUM(D{start_row}:D{row})", currency_format)

	        # Footer for Net Tax Summary
	        row += 2
	        worksheet.write(row, 0, "Total Value of Due Tax for the Period", bold)
	        worksheet.write_formula(row, 1, f"C{row-2}", currency_format)  # Use VAT Amount Total
	        row += 1
	        worksheet.write(row, 0, "Total Value of Recoverable Tax for the Period", bold)
	        worksheet.write_formula(row, 1, f"C{start_row}:C{row-3}", currency_format)  # Sum all VAT amounts
	        row += 1
	        worksheet.write(row, 0, "Payable Tax for the Period", bold)
	        worksheet.write_formula(row, 1, f"B{row-2}-B{row-1}", currency_format)

	        # Finalize workbook and create attachment
	        workbook.close()
	        output.seek(0)
	        # file_data = buffer.read()

	        # # Attach the report
	        # attachment = self.env['ir.attachment'].sudo().create({
	        #     'name': "VAT Report.xlsx",
	        #     'type': 'binary',
	        #     'datas': base64.b64encode(file_data),
	        #     'res_model': self._name,
	        #     'res_id': self.id,
	        #     'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	        # })

	        # # Provide a download link
	        # download_url = "/web/content/{}/?download=true".format(attachment.id)
	        # return {
	        #     'type': 'ir.actions.act_url',
	        #     'url': download_url,
	        #     'target': 'new',
	        # }

	        file_name = 'Vat Report.xlsx'

	        return request.make_response(

	        	output.getvalue(),

	        	)
