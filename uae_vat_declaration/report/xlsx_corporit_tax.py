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

        # Define formats for headers, currency, bold text, and title
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#D3D3D3', 'align': 'center'})
        bold = workbook.add_format({'bold': True})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Header section
        worksheet.merge_range('A1:B1', "Corporate Tax Report", title_format)
        worksheet.write("A2", "Corporate Tax Number:", bold)
        worksheet.write("B2", records.trn)
        worksheet.write("A3", "Report Date:", bold)
        worksheet.write("B3", datetime.today().strftime('%Y-%m-%d'), date_format)

        # Column headers for income and expenses
        worksheet.write("A5", "Income Details", title_format)
        worksheet.write("A6", "Income (AED)", bold)
        worksheet.write("B6", records.income, currency_format)
        worksheet.write("A7", "Other Income (AED)", bold)
        worksheet.write("B7", records.other_income, currency_format)

        # Expenses section
        worksheet.write("A9", "Expense Details", title_format)
        worksheet.write("A10", "Expenses (AED)", bold)
        worksheet.write("B10", records.expense, currency_format)
        worksheet.write("A11", "Other Expenses (AED)", bold)
        worksheet.write("B11", records.other_expense, currency_format)

        # # Total Balance section
        # worksheet.write("A13", "Total Balance", title_format)
        # worksheet.write("A14", "Total Balance (AED)", bold)
        # worksheet.write_formula("B14", "(B6 + B7) - (B10 - B11)", currency_format)  # Formula to calculate total balance

        # # Net Tax Calculation section
        # worksheet.write("A16", "Corporate Tax Summary", title_format)
        # worksheet.write("A17", "Taxable Income (AED)", bold)
        # worksheet.write_formula("B6", "B7", currency_format)  # Taxable income derived from total balance

        # فرضية أن معدل الضريبة هو 9%
        tax_rate = 0.09
        # worksheet.write("A18", "Corporate Tax Rate (%)", bold)
        # worksheet.write("B18", f"{tax_rate * 100}%", currency_format)
        worksheet.write("A14", "Calculated Tax (AED)", title_format)
        worksheet.write_formula("A15", f"={records.income_total}", currency_format)





        workbook.close()
