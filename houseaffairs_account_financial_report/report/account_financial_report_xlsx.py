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
        self.format_string_bold = None
        self.format_amount_bold = None
        
    def generate_xlsx_report(self, workbook, data, objects):
                        
        report = objects
        
        self.row_pos = 0
        
        self._define_formats(workbook)
        report_name = self._get_report_name(data)
        filters = self._get_report_filters(data)
        company_name = self._get_company_name()
        self.columns = self._get_report_columns()

        self.sheet = workbook.add_worksheet(report_name[:31])

        self._set_column_width()
        
        self._write_company_name(company_name)

        self._write_report_title(report_name)
        
        self._write_filters(filters)

        self._generate_report_content(workbook, data)
    
    def write_array_header(self):
        """Write array header on current line using all defined columns name.
        Columns are defined with `_get_report_columns` method.
        """
        for col_pos, column in self.columns.iteritems():
            self.sheet.write(self.row_pos, col_pos, column['header'],
                             self.format_header_center)
        self.row_pos += 1
        
    def _write_filters(self, filters):
        """Write one line per filters on starting on current line.
        Columns number for filter name is defined
        with `_get_col_count_filter_name` method.
        Columns number for filter value is define
        with `_get_col_count_filter_value` method.
        """
        col_name = 0
        col_count_filter_name = self._get_col_count_filter_name()
        col_count_filter_value = self._get_col_count_filter_value()
        col_value = col_name + col_count_filter_name + 1
        for title, value in filters:
            self.sheet.merge_range(
                self.row_pos, col_name,
                self.row_pos, col_name + col_count_filter_name - 1,
                title, self.format_header_left)
            self.sheet.merge_range(
                self.row_pos, col_value,
                self.row_pos, col_value + col_count_filter_value - 1,
                value)
            self.row_pos += 1
        self.row_pos += 2
        
    def _get_col_count_filter_name(self):
        return 2
        
    def _get_col_count_filter_value(self):
        return 3
        
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
        
    def _get_report_filters(self, data):
        return [
            [_('Date range filter'),
                _('From: %s To: %s') % (data['form']['date_from'], data['form']['date_to'])],
            [_('Target moves filter'),
                _('All posted entries') if data['form']['target_move'] == 'posted'
                else _('All entries')],
        ]
    
    def _get_report_columns(self):
        return {
                0: {'header': 'Account',
                    'field': 'name',
                    'width': 60},
                3: {'header': 'Actual',
                    'field': 'balance',
                    'type': 'amount',
                    'width': 15},
                #5: {'header': 'PY Actual',
                #    'field': 'balance_cmp',
                #    'type': 'amount',
                #    'width': 15},
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
         * format_amount_bold
         * format_string_bold
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
        self.format_amount_bold = workbook.add_format(
            {'bold': True}
        )
        self.format_amount_bold.set_num_format('#,##0.00')
        self.format_string_bold = workbook.add_format(
            {'bold': True}
        )
    
    def _generate_report_content(self, workbook, data):
        self.write_array_header()
        
        for account in data['report_lines']:
            if not account['level'] == 0:
                self.write_line(account)
            
    def write_line(self, line_object):
        cell_level = line_object['level']
        
        for col_pos, column in self.columns.iteritems():
            value = line_object[column['field']]
            cell_type = column.get('type', 'string')
            if cell_level > 3:
                if cell_type == 'string':
                    self.sheet.write_string(self.row_pos, col_pos, value or '')
                elif cell_type == 'amount':
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.format_amount
                    )
            elif cell_level == 2:
                if cell_type == 'string':
                    self.sheet.write_string(self.row_pos, col_pos, value or '', self.format_string_bold)
                elif cell_type == 'amount':
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.format_amount_bold
                    )
            elif cell_level == 1:
                if cell_type == 'string':
                    self.sheet.write_string(self.row_pos, col_pos, value or '', self.format_string_bold)
    
        self.row_pos += 1
        
        if 'sub_lines' in line_object:
            for line in line_object['sub_lines']:
                self.write_line(line)
        
        if cell_level == 1:
            for col_pos, column in self.columns.iteritems():
                value = line_object[column['field']]
                cell_type = column.get('type', 'string')
                if cell_type == 'string':
                    self.sheet.write_string(self.row_pos, col_pos, ('Total ' + value) or '', self.format_string_bold)
                elif cell_type == 'amount':
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.format_amount_bold
                    )
            self.row_pos += 1
                
    def _get_report_name(self, data):
        return _(data['form']['account_report_id'][1])
        
    def _get_company_name(self):
        return self.env.user.company_id.name
        
    def _write_company_name(self,name):
        self.sheet.merge_range(
            self.row_pos, 0, self.row_pos, 7,
            name, self.format_report_title
        )
        
        self.row_pos += 1
        

account_financial_report_xlsx('report.houseaffairs_account_financial_report.report_financial_report_xlsx','account.financial.report',parser=report_sxw.rml_parse)
    