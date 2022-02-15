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
    year_txt = fields.Char()
    month_txt = fields.Char()
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

        rec_cursor = self.env['account.move'].browse(self.env.context['active_ids'])
        self.file_name = 'txt_generacion.txt'
        with open("/home/odoo/txt.txt", "w") as file:

            for rec in rec_cursor:
                file.write(rec.invoice_id + "\t")
                file.write(rec.moneda + "\t")
                file.write(rec.rnc + "\t")
                file.write(rec.provider_name + "\t")
                file.write(rec.tipo_bien_servicio + "\t")
                file.write(rec.ncf + "\t")
                file.write(rec.ncf_modificado + "\t")
                file.write(rec.invoice_date + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
                #file.write(self. + "\t")
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
    year_txt = fields.Char()
    month_txt = fields.Char()
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

        self.file_name = 'txt_generacion.txt'
        with open("/home/odoo/txt.txt", "w") as file:
			#periodo = '%s'%(rec.invoice_id.date)
			#periodo = periodo.replace('-', '')
			#periodo = periodo[0:6]
			#exento = abs(rec.total_factura-rec.base_imponible-rec.impuesto_iva-rec.amount)
			#total = rec.base_imponible+rec.impuesto_iva+exento
			#por_iva = rec.impuesto_iva/rec.base_imponible*100
			#fecha = rec.invoice_id.date_invoice
			#su_rif = rif_format(rec.invoice_id.partner_id.vat)
			#refer = rec.invoice_id.refund_invoice_id.number if rec.tipo=='in_refund' and rec.invoice_id.refund_invoice_id else '0'
			#total2 = str(total)
			#base_imponible = str(rec.base_imponible)
			#amount = str(rec.amount)

			#refer = str(refer)
			#number_retiva = str(rec.number_retiva)
			#exento = str(exento)
			#por_iva = str(por_iva)
			#fecha = str(fecha)
			#invoice_sequence = str(rec.invoice_id.invoice_sequence)


            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
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
    year_txt = fields.Char()
    month_txt = fields.Char()
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

        self.file_name = 'txt_generacion.txt'
        with open("/home/odoo/txt.txt", "w") as file:
			#periodo = '%s'%(rec.invoice_id.date)
			#periodo = periodo.replace('-', '')
			#periodo = periodo[0:6]
			#exento = abs(rec.total_factura-rec.base_imponible-rec.impuesto_iva-rec.amount)
			#total = rec.base_imponible+rec.impuesto_iva+exento
			#por_iva = rec.impuesto_iva/rec.base_imponible*100
			#fecha = rec.invoice_id.date_invoice
			#su_rif = rif_format(rec.invoice_id.partner_id.vat)
			#refer = rec.invoice_id.refund_invoice_id.number if rec.tipo=='in_refund' and rec.invoice_id.refund_invoice_id else '0'
			#total2 = str(total)
			#base_imponible = str(rec.base_imponible)
			#amount = str(rec.amount)

			#refer = str(refer)
			#number_retiva = str(rec.number_retiva)
			#exento = str(exento)
			#por_iva = str(por_iva)
			#fecha = str(fecha)
			#invoice_sequence = str(rec.invoice_id.invoice_sequence)


            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('C' + "\t")
            file.write('0' + "\n")




        self.write({'file_data': base64.encodestring(open("/home/odoo/txt.txt", "rb").read()),
            'file_name': "608.txt",
				})

        return self.show_view('Archivo Generado', self._name, 'l10n_do_txt_reports.608_txt_form_view', self.id)
