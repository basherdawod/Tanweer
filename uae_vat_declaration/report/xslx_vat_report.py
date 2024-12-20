import io
from odoo import http
from odoo.http import request
import xlsxwriter

class XlsxVatReport(http.Controller):
    @http.route('/vat/excel/report', type='http', auth='user')
    def generate_xlsx_report(self, workbook, data, records):
	    worksheet = workbook.add_worksheet("VAT 201 Return Report")

	    # إعداد التنسيقات
	    title_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'align': 'center', 'font_size': 14})
	    bold = workbook.add_format({'bold': True})
	    currency_format = workbook.add_format({'num_format': '#,##0.00'})

	    # إعداد عنوان التقرير
	    worksheet.merge_range('A1:D1', "VAT 201 Return Report", title_format)

	    # كتابة معلومات التقرير الأساسية
	    worksheet.write("A2", "Ref:", bold)
	    worksheet.write("B2", records.name if records.name else "N/A")
	    worksheet.write("A3", "Date:", bold)
	    worksheet.write("B3", records.date_from.strftime('%Y-%m-%d') if records.date_from else "N/A")
	    worksheet.write("A4", "Tax Registration Number (TRN):", bold)
	    worksheet.write("B4", records.trn if records.trn else "N/A")
	    worksheet.write("A5", "Legal Name in English:", bold)
	    worksheet.write("B5", records.legal_name if records.legal_name else "N/A")

	    # عناوين الأعمدة لقسم المبيعات
	    worksheet.write("A7", "Description", bold)
	    worksheet.write("B7", "Amount (AED)", bold)
	    worksheet.write("C7", "VAT Amount (AED)", bold)
	    worksheet.write("D7", "Adjustment (AED)", bold)

	    # إضافة البيانات من `vat_sales_outputs`
	    vat_sales_outputs = records.vat_sales_outputs
	    start_row = 8
	    row = start_row
	    for line in vat_sales_outputs:
	        worksheet.write(row, 0, line.description or "N/A")
	        worksheet.write(row, 1, line.amount, currency_format)
	        worksheet.write(row, 2, line.taxamount, currency_format)
	        worksheet.write(row, 3, line.adjustment, currency_format)
	        row += 1

	        # شرط التلخيص الأولي عند وصول السطر إلى 20
	     
	    worksheet.write(21, 0, "Total Sales", bold)
	    worksheet.write_formula(21, 1, f"SUM(B{start_row}:B{row})", currency_format)
	    worksheet.write_formula(21, 2, f"SUM(C{start_row}:C{row})", currency_format)
	    worksheet.write_formula(21, 3, f"SUM(D{start_row}:D{row})", currency_format)
	           

	    # إضافة عنوان فرعي لقسم المشتريات
	    row += 2  # إضافة فاصل بسيط
	    worksheet.merge_range(f'A{row}:D{row}', "Purchase Summary", title_format)

	    # تلخيص المشتريات
	    row += 1
	    worksheet.write(row, 0, "Total Purchase", bold)
	    worksheet.write_formula(row, 1, f"SUM(B21:B{row-1})", currency_format)
	    worksheet.write_formula(row, 2, f"SUM(C21:C{row-1})", currency_format)
	    worksheet.write_formula(row, 3, f"SUM(D21:D{row-1})", currency_format)

	    workbook.close()




import io
from odoo import models
from datetime import datetime
import base64
from xlsxwriter import Workbook

class VatDeclarationXlsxReport(models.AbstractModel):
    _name = 'report.uae_vat_declaration.vat_declaration_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        worksheet = workbook.add_worksheet("VAT 201 Return Report")

        # Define formats for headers and currency
        bold = workbook.add_format({'bold': True})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})

        # Header section
        worksheet.write("A1", "VAT 201 Return Report", bold)
        worksheet.write("A2", "Ref:", bold)
        worksheet.write("B2", records.name if records.name else "N/A")
        worksheet.write("A3", "Date:", bold)
        worksheet.write("B3", records.date_from.strftime('%Y-%m-%d') if records.date_from else "N/A")
        worksheet.write("A4", "Tax Registration Number (TRN):", bold)
        worksheet.write("B4", records.trn if records.trn else "N/A")
        worksheet.write("A5", "Legal Name in English:", bold)
        worksheet.write("B5", records.legal_name if records.legal_name else "N/A")

        # Column headers for Supplies Section
        worksheet.write("A7", "Description", bold)
        worksheet.write("B7", "Amount (AED)", bold)
        worksheet.write("C7", "VAT Amount (AED)", bold)
        worksheet.write("D7", "Adjustment (AED)", bold)

        # Add data rows from `vat_sales_outputs`
        vat_sales_outputs = records.vat_sales_outputs
        start_row = 8
        row = start_row
        for line in vat_sales_outputs:
            worksheet.write(row, 0, line.description or "N/A")
            worksheet.write(row, 1, line.amount, currency_format)
            worksheet.write(row, 2, line.taxamount, currency_format)
            worksheet.write(row, 3, line.adjustment, currency_format)
            row += 1


        
        worksheet.write(24, 0, "Total Sale", bold)
        worksheet.write_formula(24, 1, "SUM(B9:B21)", currency_format)
        worksheet.write_formula(24, 2, "SUM(C9:C21)", currency_format)
        worksheet.write_formula(24, 3, "SUM(D9:D21)", currency_format)

        worksheet.write(25, 0, "Total Purchace", bold)
        worksheet.write_formula(25, 1, "SUM(B22:B23)", currency_format)
        worksheet.write_formula(25, 2, "SUM(C22:C23)", currency_format)
        worksheet.write_formula(25, 3, "SUM(D22:D23)", currency_format)

        workbook.close()
