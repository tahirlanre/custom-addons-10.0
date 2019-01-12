# -*- coding: utf-8 -*-
from odoo import http

# class DmxContactDirectory(http.Controller):
#     @http.route('/dmx_contact_directory/dmx_contact_directory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dmx_contact_directory/dmx_contact_directory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dmx_contact_directory.listing', {
#             'root': '/dmx_contact_directory/dmx_contact_directory',
#             'objects': http.request.env['dmx_contact_directory.dmx_contact_directory'].search([]),
#         })

#     @http.route('/dmx_contact_directory/dmx_contact_directory/objects/<model("dmx_contact_directory.dmx_contact_directory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dmx_contact_directory.object', {
#             'object': obj
#         })