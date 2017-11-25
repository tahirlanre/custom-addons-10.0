# -*- coding: utf-8 -*-

import datetime
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import _


class inventory_valuation_xlsx(ReportXlsx):
    
    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)
        
inventory_valuation_xlsx('report.inventory_valuation.inventory.valuation.xlsx', 'product.product')