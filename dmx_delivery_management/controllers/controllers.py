# -*- coding: utf-8 -*-
from odoo import http

# class DmxDeliveryManagement(http.Controller):
#     @http.route('/dmx_delivery_management/dmx_delivery_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dmx_delivery_management/dmx_delivery_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dmx_delivery_management.listing', {
#             'root': '/dmx_delivery_management/dmx_delivery_management',
#             'objects': http.request.env['dmx_delivery_management.dmx_delivery_management'].search([]),
#         })

#     @http.route('/dmx_delivery_management/dmx_delivery_management/objects/<model("dmx_delivery_management.dmx_delivery_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dmx_delivery_management.object', {
#             'object': obj
#         })