# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class InventorySalesAnalysisXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)

InventorySalesAnalysisXlsx('report.inventory_sales_analysis.inventory_sales_analysis_xlsx','report_inventory_sales_analysis_qweb')