# -*- coding: utf-8 -*-

import datetime
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.report import report_sxw
from odoo import _


class account_financial_report_xlsx(ReportXlsx):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(account_financial_report_xlsx, self).__init__(
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
        
    def generate_xlsx_report(self, workbook, data, objects):
        
        report = objects
        
        self.row_pos = 0
        
        self._define_formats(workbook)
        report_name = self._get_report_name(data)
        #filters = self._get_report_filters(report)
        self.columns = self._get_report_columns()

        self.sheet = workbook.add_worksheet(report_name[:31])

        self._set_column_width()

        self._write_report_title(report_name)

        #self._write_filters(filters)

        self._generate_report_content(workbook, report)
    
    def write_array_header(self):
        """Write array header on current line using all defined columns name.
        Columns are defined with `_get_report_columns` method.
        """
        for col_pos, column in self.columns.iteritems():
            self.sheet.write(self.row_pos, col_pos, column['header'],
                             self.format_header_center)
        self.row_pos += 1
        
    def _write_filters(self):
        pass
        
    def _set_column_width(self):
        """Set width for all defined columns.
        Columns are defined with `_get_report_columns` method.
        """
        for position, column in self.columns.iteritems():
            self.sheet.set_column(position, position, column['width'])
    
    def _set_header_column_width(self):
        for col_pos, column in self.columns.iteritems():
            self.sheet.write(self.row_pos, col_pos, column['header'],
                             self.format_header_center)
        self.row_pos += 1
        
    def _get_report_filters(self, report):
        pass
    
    def _get_report_columns(self):
        return {
                5: {'header': 'Actual',
                    'field': 'balance',
                    'type': 'amount',
                    'width': 15},
                7: {'header': 'PY Actual',
                     'field': 'balance_cmp',
                     'type': 'amount',
                     'width': 15},
                }
        
    def _write_report_title(self, title):
        """Write report title on current line using all defined columns width.
        Columns are defined with `_get_report_columns` method.
        """
        self.sheet.merge_range(
            self.row_pos, 0, self.row_pos, 7,
            title, self.format_report_title
        )
        self.row_pos += 3
        
    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Those formats can be used on all cell.

        Available formats are :
         * format_bold
         * format_right
         * format_right_bold_italic
         * format_header_left
         * format_header_center
         * format_header_right
         * format_header_amount
         * format_amount
         * format_percent_bold_italic
         * format_report_title
        """
        self.format_report_title = workbook.add_format({'bold': True,'font_size':18,'align': 'center'})
        self.format_bold = workbook.add_format({'bold': True})
        self.format_right = workbook.add_format({'align': 'right'})
        self.format_right_bold_italic = workbook.add_format(
            {'align': 'right', 'bold': True, 'italic': True}
        )
        self.format_header_left = workbook.add_format(
            {'bold': True,
             'border': True})
        self.format_header_center = workbook.add_format(
            {'bold': True,
             'align': 'center'})
        self.format_header_right = workbook.add_format(
            {'bold': True,
             'align': 'right'})
        self.format_header_amount = workbook.add_format(
            {'bold': True,
             'border': True,})
        self.format_header_amount.set_num_format('#,##0.00')
        self.format_amount = workbook.add_format()
        self.format_amount.set_num_format('#,##0.00')
        self.format_percent_bold_italic = workbook.add_format(
            {'bold': True, 'italic': True}
        )
        self.format_percent_bold_italic.set_num_format('#,##0.00%')
    
    def _generate_report_content(self, workbook, report):
        self.write_array_header()
        
    def _get_report_name(self, data):
        return _(data['form']['account_report_id'][1])

account_financial_report_xlsx('report.account_financial_report_xlsx.report_financial_report_xlsx','account.financial.report',parser=report_sxw.rml_parse)
    