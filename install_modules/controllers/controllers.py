# -*- coding: utf-8 -*-
from odoo import http

# class TestScaffold(http.Controller):
#     @http.route('/test_scaffold/test_scaffold/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_scaffold/test_scaffold/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_scaffold.listing', {
#             'root': '/test_scaffold/test_scaffold',
#             'objects': http.request.env['test_scaffold.test_scaffold'].search([]),
#         })

#     @http.route('/test_scaffold/test_scaffold/objects/<model("test_scaffold.test_scaffold"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_scaffold.object', {
#             'object': obj
#         })