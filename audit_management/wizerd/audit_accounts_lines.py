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
        try:
            # Decode and load the Excel file
            file_data = base64.b64decode(self.excel_file)
            file_stream = BytesIO(file_data)
            workbook = openpyxl.load_workbook(file_stream, read_only=True)
            sheet = workbook.active  # Get the first sheet

            for record in sheet.iter_rows(min_row=2, max_row=None, values_only=True):
                # Check if the account line already exists, otherwise create a new one
                existing_record = self.env['audit.account.account.line'].search([
                    ('code', '=', record[1])  # Search by code (you can modify this if needed)
                ], limit=1)

                if not existing_record:
                    # Create a new record if it doesn't exist
                    self.env['audit.account.account.line'].create({
                        'name': record[0],
                        'code': record[1],
                        'account_type': record[2],
                        'opening_debit': record[3],
                        'opening_credit': record[4],
                        'opening_balance': record[5],
                    })
                else:
                    # Optionally, update the existing record if needed
                    existing_record.write({
                        'name': record[0],
                        'account_type': record[2],
                        'opening_debit': record[3],
                        'opening_credit': record[4],
                        'opening_balance': record[5],
                    })
        except Exception as e:
            raise UserError(_('Please insert a valid file: %s' % str(e)))

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
    #         file_stream = BytesIO(data)
    #         workbook = openpyxl.load_workbook(file_stream)
    #         sheet = workbook.active 
    #         # sheet = workbook.data
    #         for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
    #             self.env['audit.account.account.line'].create({
    #                 'name': row[0].value,
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