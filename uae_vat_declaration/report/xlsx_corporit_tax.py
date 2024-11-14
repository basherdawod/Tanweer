import io
from odoo import models
from odoo.tools import date_utils
from datetime import datetime
import base64
from xlsxwriter import Workbook

class CorporateTaxXlsxReport(models.AbstractModel):
    _name = 'report.uae_vat_declaration.report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        worksheet = workbook.add_worksheet("Corporate Tax Report")

        # Define formats for headers, currency, and bold text
        bold = workbook.add_format({'bold': True})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Header section
        worksheet.write("A1", "Corporate Tax Report", bold)
        worksheet.write("A2", "Corporate Tax Number:", bold)
        worksheet.write("B2", records.trn)
        
        # Column headers for tax calculation
        worksheet.write("A5", "Income (AED)", bold)
        worksheet.write("B5", records.income)
        worksheet.write("A6", "Other Income (AED)", bold)
        worksheet.write("B6", records.other_income)
        worksheet.write("A7", "Expenses (AED)", bold)
        worksheet.write("B7", records.expense)
        worksheet.write("A8", "Other Expenses (AED)", bold)
        worksheet.write("B8", records.other_expense)
        worksheet.write("A9", "ToTal Balance (AED)", bold)
        worksheet.write("B9", records.income_total)


        workbook.close()
