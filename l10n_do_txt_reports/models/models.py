# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import logging
import calendar
import io
from io import BytesIO
from io import StringIO

import xlsxwriter
import shutil
import base64
import csv

import urllib.request

import requests


class L10nDoTxtReports(models.Model):
    _name = 'txt_report.606'

    delimiter = '\t'
    quotechar = "'"
    date_from = fields.Date()
    date_to = fields.Date()
    file_data = fields.Binary('Archivo TXT', filters=None, help="")
    file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)
    #rec_cursor = fields.Many2many('report.606', 'invoice_id')

    def show_view(self, name, model, id_xml, res_id=None, view_mode='tree,form', nodestroy=True, target='new'):
        context = self._context
        mod_obj = self.env['ir.model.data']
        view_obj = self.env['ir.ui.view']
        module = ""
        view_id = self.env.ref(id_xml).id
        if view_id:
            view = view_obj.browse(view_id)
            view_mode = view.type
        ctx = context.copy()
        ctx.update({'active_model': model})
        res = {'name': name,
                'view_type': 'form',
                'view_mode': view_mode,
                'view_id': view_id,
                'res_model': model,
                'res_id': res_id,
                'nodestroy': nodestroy,
                'target': target,
                'type': 'ir.actions.act_window',
                'context': ctx,
                }
        return res


    def action_generate_txt(self):

        #dominio = (('id','=',True),('invoice_id.type','in',('in_invoice', 'in_refund')),('invoice_id.amount_tax','!=',0.00))

        #if self.date_from:
        #    dominio.append(('create_date','>=',self.date_from))

        #if self.date_to:
        #    dominio.append(('create_date','<=',self.date_to))

        #rec_ids = self.env['account.move'].search(dominio).ids
        rec_cursor = self.env['account.move'].search([('date','>=',self.date_from),('date','<=',self.date_to),('type','=','out_invoice'),('state','=','posted')])
        #_logger.info("\n\n\n {} \n\n\n".format(self.rec_cursor))

        self.file_name = 'txt_generacion.txt'
        #rutaw="C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/l10n_do_txt_reports/wizard/txt_generacion.txt"
        #rutal="/home/odoo/txt.txt"
        with open("/home/odoo/txt.txt", "w") as file:

            for rec in rec_cursor:
             # 32 campos
                invoice_id = str(rec.name)
                moneda = rec.currency_id.name
                rnc_o = rec.partner_id.vat
                rnc = str(rnc_o)
                provider_name = rec.partner_id.name
                #tipo_bien_servicio =
                ncf = str(rec.ref)
                ncf_modificado = str(rec.l10n_do_origin_ncf)
                invoice_date = str(rec.invoice_date)
                fecha_emision = str(rec.invoice_date)
                fecha_pago = str(rec.invoice_date_due)
                #fecha_comprobante_am =
                #fecha_comprobante_d =
                #fecha_pago_am =
                #fecha_pago_d =
                monto_facturado = str(rec.amount_untaxed)
                #monto_bienes =
                #monto_facturado_aitbis =
                monto_facturado_itbis = str(rec.amount_tax_signed)
                itbis_retenido = str(rec.amount_tax)
                #itbis_sujeto_proporcionalidad =
                #itbis_llevado_costo =
                #tipo_itbis_llevado_costo =
                #itbis_adelantar =
                #tipo_itbis_por_adelantar =
                #itbis_percibido_compras =
                #tipo_isr_retenido =
                #isr_retenido =
                #monto_facturado_isc =
                #monto_otros_imp =
                #monto_facturado_propina =
                #isr_percibido_compras =
                #forma_pago =

                file.write(invoice_id + "\t")
                file.write(moneda + "\t")
                file.write('0' + "\t")
                file.write(provider_name + "\t")
                file.write('0' + "\t")
                file.write(ncf + "\t")
                file.write(ncf_modificado + "\t")
                file.write(invoice_date + "\t")
                file.write(fecha_emision + "\t")
                file.write(fecha_pago + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write(monto_facturado + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write(monto_facturado_itbis + "\t")
                file.write(itbis_retenido + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")

                file.write('0' + "\n")




        self.write({'file_data': base64.encodestring(open("/home/odoo/txt.txt", "rb").read()),
            'file_name': "606.txt",
				})

        return self.show_view('Archivo Generado', self._name, 'l10n_do_txt_reports.606_txt_form_view', self.id)
##############################################################################################
############################################################################################3#
##############################################################################################

class L10nDoTxtReportsdos(models.Model):
    _name = 'txt_report.607'

    delimiter = '\t'
    quotechar = "'"
    date_from = fields.Char()
    date_to = fields.Char()
    file_data = fields.Binary('Archivo TXT', filters=None, help="")
    file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)


    def show_view(self, name, model, id_xml, res_id=None, view_mode='tree,form', nodestroy=True, target='new'):
        context = self._context
        mod_obj = self.env['ir.model.data']
        view_obj = self.env['ir.ui.view']
        module = ""
        view_id = self.env.ref(id_xml).id
        if view_id:
            view = view_obj.browse(view_id)
            view_mode = view.type
        ctx = context.copy()
        ctx.update({'active_model': model})
        res = {'name': name,
                'view_type': 'form',
                'view_mode': view_mode,
                'view_id': view_id,
                'res_model': model,
                'res_id': res_id,
                'nodestroy': nodestroy,
                'target': target,
                'type': 'ir.actions.act_window',
                'context': ctx,
                }
        return res

    def action_generate_txt(self):

        rec_cursor = self.env['account.move'].search([('date','>=',self.date_from),('date','<=',self.date_to),('type','=','in_invoice'),('state','=','posted')])
        #_logger.info("\n\n\n {} \n\n\n".format(self.rec_cursor))

        self.file_name = 'txt_generacion.txt'
        #rutaw="C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/l10n_do_txt_reports/wizard/txt_generacion.txt"
        #rutal="/home/odoo/txt.txt"
        with open("/home/odoo/txt.txt", "w") as file:

            for rec in rec_cursor:
             # 32 campos
                invoice_id = str(rec.name)
                moneda = rec.currency_id.name
                rnc_o = rec.partner_id.vat
                rnc = str(rnc_o)
                provider_name = rec.partner_id.name
                #tipo_bien_servicio =
                ncf = str(rec.ref)
                ncf_modificado = str(rec.l10n_do_origin_ncf)
                invoice_date = str(rec.invoice_date)
                fecha_emision = str(rec.invoice_date)
                fecha_pago = str(rec.invoice_date_due)
                #fecha_comprobante_am =
                #fecha_comprobante_d =
                #fecha_pago_am =
                #fecha_pago_d =
                monto_facturado = str(rec.amount_untaxed)
                #monto_bienes =
                #monto_facturado_aitbis =
                monto_facturado_itbis = str(rec.amount_tax_signed)
                itbis_retenido = str(rec.amount_tax)
                #itbis_sujeto_proporcionalidad =
                #itbis_llevado_costo =
                #tipo_itbis_llevado_costo =
                #itbis_adelantar =
                #tipo_itbis_por_adelantar =
                #itbis_percibido_compras =
                #tipo_isr_retenido =
                #isr_retenido =
                #monto_facturado_isc =
                #monto_otros_imp =
                #monto_facturado_propina =
                #isr_percibido_compras =
                #forma_pago =

                file.write(invoice_id + "\t")
                file.write(moneda + "\t")
                file.write('0' + "\t")
                file.write(provider_name + "\t")
                file.write('0' + "\t")
                file.write(ncf + "\t")
                file.write(ncf_modificado + "\t")
                file.write(invoice_date + "\t")
                file.write(fecha_emision + "\t")
                file.write(fecha_pago + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write(monto_facturado + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write(monto_facturado_itbis + "\t")
                file.write(itbis_retenido + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")
                file.write('0' + "\t")

                file.write('0' + "\n")


        self.write({'file_data': base64.encodestring(open("/home/odoo/txt.txt", "rb").read()),
            'file_name': "607.txt",
				})

        return self.show_view('Archivo Generado', self._name, 'l10n_do_txt_reports.607_txt_form_view', self.id)
##############################################################################################
############################################################################################3#
##############################################################################################
class L10nDoTxtReportstres(models.Model):
    _name = 'txt_report.608'

    delimiter = '\t'
    quotechar = "'"
    date_from = fields.Char()
    date_to = fields.Char()
    file_data = fields.Binary('Archivo TXT', filters=None, help="")
    file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)


    def show_view(self, name, model, id_xml, res_id=None, view_mode='tree,form', nodestroy=True, target='new'):
        context = self._context
        mod_obj = self.env['ir.model.data']
        view_obj = self.env['ir.ui.view']
        module = ""
        view_id = self.env.ref(id_xml).id
        if view_id:
            view = view_obj.browse(view_id)
            view_mode = view.type
        ctx = context.copy()
        ctx.update({'active_model': model})
        res = {'name': name,
                'view_type': 'form',
                'view_mode': view_mode,
                'view_id': view_id,
                'res_model': model,
                'res_id': res_id,
                'nodestroy': nodestroy,
                'target': target,
                'type': 'ir.actions.act_window',
                'context': ctx,
                }
        return res

    def action_generate_txt(self):

        rec_cursor = self.env['account.move'].search([('date','>=',self.date_from),('date','<=',self.date_to),('state','=','cancel')])
        #_logger.info("\n\n\n {} \n\n\n".format(self.rec_cursor))

        self.file_name = 'txt_generacion.txt'
        #rutaw="C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/l10n_do_txt_reports/wizard/txt_generacion.txt"
        #rutal="/home/odoo/txt.txt"
        with open("/home/odoo/txt.txt", "w") as file:

            for rec in rec_cursor:
             # 32 campos
                invoice_id = str(rec.name)
                #moneda = rec.currency_id.name
                rnc_o = rec.partner_id.vat
                rnc = str(rnc_o)
                provider_name = rec.partner_id.name
                #tipo_bien_servicio =
                ncf = str(rec.ref)
                ncf_modificado = str(rec.l10n_do_origin_ncf)
                invoice_date = str(rec.invoice_date)


                file.write(invoice_id + "\t")
                file.write(ncf + "\t")
                file.write('0' + "\t")
                file.write(provider_name + "\t")
                file.write(invoice_date + "\t")
                file.write(invoice_date + "\t")
                file.write(invoice_date + "\t")
                file.write('0' + "\t")

                file.write('0' + "\n")



        self.write({'file_data': base64.encodestring(open("/home/odoo/txt.txt", "rb").read()),
            'file_name': "608.txt",
				})

        return self.show_view('Archivo Generado', self._name, 'l10n_do_txt_reports.608_txt_form_view', self.id)
