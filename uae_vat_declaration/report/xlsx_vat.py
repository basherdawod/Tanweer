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


            if row == 20:
                worksheet.write(21, 0, "Total Sale", bold)
                worksheet.write_formula(21, 1, "SUM(B9:B20)", currency_format)
                worksheet.write_formula(21, 2, "SUM(C9:C20)", currency_format)
                worksheet.write_formula(21, 3, "SUM(D9:D20)", currency_format)
                row += 1

        worksheet.write(25, 0, "Total Purchace", bold)
        worksheet.write_formula(25, 1, "SUM(B21:B22)", currency_format)
        worksheet.write_formula(25, 2, "SUM(C21:C22)", currency_format)
        worksheet.write_formula(25, 3, "SUM(D21:D22)", currency_format)

        workbook.close()
