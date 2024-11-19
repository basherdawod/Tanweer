import base64
# import openpyxl
from odoo import models, fields, api

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

            # Load the workbook using openpyxl
            workbook = openpyxl.load_workbook(filename=bytes(data))
            sheet = workbook.active  # Get the first sheet

            # Iterate over the rows (skip header)
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                self.env['audit.account.account.line'].create({
                    'name': row[0].value,  # Adjust based on your column structure
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
    #         raise UserError(_("Please upload a valid Excel file."))

    #     try:

    #         data = base64.b64decode(self.excel_file)
    #         workbook = xlrd.open_workbook(file_contents=data)
    #         sheet = workbook.sheet_by_index(0)

    #         for row_idx in range(1, sheet.nrows):
    #             row = sheet.row_values(row_idx)

    #             self.env['audit.account.account.line'].create({
    #                 'name': row[0],  
    #                 'code': row[1], 
    #                 'account_type': row[2], 
    #                 'opening_debit': row[3],  
    #                 'opening_credit': row[4], 
    #                 'opening_balance': row[5], 
    #             })

    #     except Exception as e:
    #         raise UserError(_("Error processing Excel file: %s") % e)

    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }

