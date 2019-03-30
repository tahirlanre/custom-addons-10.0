# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
import datetime
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.report import report_sxw


class AssetReportXlsx(ReportXlsx):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(AssetReportXlsx, self).__init__(
            name, table, rml, parser, header, store)

        # main sheet which will contains report
        self.sheet = None

        # columns of the report
        self.columns = None

        # row_pos must be incremented at each writing lines
        self.row_pos = None

        # Formats
        self.format_right = None
        self.format_right_bold_italic = None
        self.format_bold = None
        self.format_header_left = None
        self.format_header_center = None
        self.format_header_right = None
        self.format_header_amount = None
        self.format_amount = None
        self.format_percent_bold_italic = None
        self.format_report_title = None
        self.format_string_bold = None
        self.format_amount_bold = None
        
AssetReportXlsx('report.account_asset_report.report_asset_register_xlsx','report_asset_register_qweb',parser=report_sxw.rml_parse)