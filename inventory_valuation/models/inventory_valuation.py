# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models


class InventoryValuation(models.AbstractModel):
    """Model of Customer Activity Statement"""

    _name = 'report.inventory_valuation.report_inventory_valuation'
    
    def _get_internal_locations(self):
        internal_locations = self.env['stock.location'].search([('usage','=','internal')])
        return internal_locations.ids
        
    def _get_inventory_valuation_lines(self, date):
        product_ids = self.env['product.product'].search([]).ids
        locations = self._get_internal_locations()
        data = {}
        self.env.cr.execute("""
            SELECT h.product_id, SUM(h.quantity) as qty, SUM(h.price_unit_on_quant * h.quantity) as value FROM stock_history h, stock_move m WHERE h.move_id=m.id 
            AND h.location_id in %s AND m.date <= %s GROUP BY h.product_id
        """ , (tuple(locations), date)
        )
        for row in self.env.cr.dictfetchall():
            data[row['product_id']] = {
                'qty' : row['qty'],
                'value': row['value']
            }
            
        return data
            
    def render_html(self, docids, data):
        date = data['date']
        lines_to_display = self._get_inventory_valuation_lines(date)
        product_ids = []
        for product_id in lines_to_display.keys():
            product_ids.append(product_id)
        
        docargs = {
            'doc_ids': product_ids,
            'doc_model': 'product.product',
            'docs': self.env['product.product'].browse(product_ids),
            'Lines': lines_to_display,
            'Date': date,
        }
        
        return self.env['report'].render(
            'inventory_valuation.report_inventory_valuation', values=docargs)
