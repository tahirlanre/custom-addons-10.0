# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import date, timedelta
from odoo import api, fields, models


class InventoryValuationWizard(models.TransientModel):

    _name = 'inventory.valuation.wizard'
    
    choose_date = fields.Boolean('Inventory at Date')
    date = fields.Date('Date', default=fields.Date.context_today, required=True)
    
    def _prepare_inventory_valuation(self):
        self.ensure_one()
        return {
            'date' : self.date,
        }
    
    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        data = self._prepare_inventory_valuation()
        return self.env['report'].get_action(self, 'inventory_valuation.report_inventory_valuation', data=data)
        
    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        data = {}
        date = self.date
        report = self.env['report.inventory_valuation.report_inventory_valuation']
        data['report_lines'] = report._get_inventory_valuation_lines(date)
        data['date'] = date
        return {'type': 'ir.actions.report.xml',
                'report_name': 'inventory_valuation.inventory.valuation.xlsx',
                'datas': data,
                'name': 'Inventory Valuation'
                }