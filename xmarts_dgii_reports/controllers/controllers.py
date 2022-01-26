# -*- coding: utf-8 -*-
# from odoo import http


# class XmartsDgiiReports(http.Controller):
#     @http.route('/xmarts_dgii_reports/xmarts_dgii_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/xmarts_dgii_reports/xmarts_dgii_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('xmarts_dgii_reports.listing', {
#             'root': '/xmarts_dgii_reports/xmarts_dgii_reports',
#             'objects': http.request.env['xmarts_dgii_reports.xmarts_dgii_reports'].search([]),
#         })

#     @http.route('/xmarts_dgii_reports/xmarts_dgii_reports/objects/<model("xmarts_dgii_reports.xmarts_dgii_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('xmarts_dgii_reports.object', {
#             'object': obj
#         })
