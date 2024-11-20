from odoo import models, fields,_
import openpyxl
import base64
from io import BytesIO
from odoo.exceptions import UserError

class AuditAccountImportWizard(models.TransientModel):
    _name = 'audit.account.import.wizard'
    _description = 'Import Wizard'

    excel_file = fields.Binary(string="Upload Excel File", required=True)
    excel_filename = fields.Char(string="File Name")

    def action_import_excel(self):
        if not self.excel_file:
            raise ValueError("Please upload a valid Excel file.")
        try:
            # Decode the uploaded file
            data = base64.b64decode(self.excel_file)
            file_stream = BytesIO(data)
            workbook = openpyxl.load_workbook(file_stream)
            sheet = workbook.active 
            # sheet = workbook.data
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                self.env['audit.account.account.line'].create({
                    'name': row[0].value,
                    'code': row[1].value,
                    'account_type': row[2].value,
                    'opening_debit': row[3].value,
                    'opening_credit': row[4].value,
                    'opening_balance': row[5].value,
                })
        except Exception as e:
            raise ValueError(f"Error processing Excel file: {e}")

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




    # def action_import_excel(self):
    #     if not self.excel_file:
    #         raise ValueError("Please upload a valid Excel file.")

    #     try:
    #         # Decode the uploaded file
    #         data = base64.b64decode(self.excel_file)
    #         # Use BytesIO to convert the bytes to a file-like object
    #         file_stream = BytesIO(data)
    #         workbook = openpyxl.load_workbook(file_stream)  # Pass the BytesIO stream
    #         sheet = workbook.active  # Get the first sheet

    #         # Iterate over the rows (skip header)
    #         for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
    #             self.env['audit.account.account.line'].create({
    #                 'name': row[0].value,  # Adjust based on your column structure
    #                 'code': row[1].value,
    #                 'account_type': row[2].value,
    #                 'opening_debit': row[3].value,
    #                 'opening_credit': row[4].value,
    #                 'opening_balance': row[5].value,
    #             })
    #     except Exception as e:
    #         raise ValueError(f"Error processing Excel file: {e}")

    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }