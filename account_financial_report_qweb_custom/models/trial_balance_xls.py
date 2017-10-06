# -*- coding: utf-8 -*-

from odoo.addons.account_financial_report_qweb.report.trial_balance_xlsx import TrialBalanceXslx
from odoo import _
    
def _get_report_columns(self, report):
    if not report.show_partner_details:
        return {
            0: {'header': _('Code'), 'field': 'code', 'width': 10},
            1: {'header': _('Account'), 'field': 'name', 'width': 60},
            2: {'header': _('Debit'),
            'field': 'final_balance',
            'type': 'amount',
            'width': 14},
            3: {'header': _('Credit'),
            'field': 'final_balance',
            'type': 'amount',
            'width': 14},
        }
    else:
        return {
            0: {'header': _('Partner'), 'field': 'name', 'width': 70},
            1: {'header': _('Debit'),
            'field': 'final_balance',
            'type': 'amount',
            'width': 14},
            2: {'header': _('Credit'),
            'field': 'final_balance',
            'type': 'amount',
            'width': 14},
        }

def write_line(self, line_object):
    """Write a line on current line using all defined columns field name.
    Columns are defined with `_get_report_columns` method.
    """
    for col_pos, column in self.columns.iteritems():
        value = getattr(line_object, column['field'])
        #import pdb; pdb.set_trace()
        cell_type = column.get('type', 'string')
        if cell_type == 'string':
            self.sheet.write_string(self.row_pos, col_pos, value or '')
        elif cell_type == 'amount':
            if column['header'] == 'Debit' and value > 0:
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.format_amount
                )
            if column['header'] == 'Credit' and value < 0:
                self.sheet.write_number(
                    self.row_pos, col_pos, abs(float(value)), self.format_amount
                )
    self.row_pos += 1

        
TrialBalanceXslx._get_report_columns = _get_report_columns
TrialBalanceXslx.write_line = write_line