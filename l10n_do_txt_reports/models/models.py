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

class L10nDo(models.Model):
    _inherit = 'report.606'
    #_auto = True


class L10nDoTxtReports(models.Model):
    _name = 'txt_report.606'

    delimiter = '\t'
    quotechar = "'"
    year_txt = fields.Char()
    month_txt = fields.Char()
    file_data = fields.Binary('Archivo TXT', filters=None, help="")
    file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)
    #rec_cursor = fields.Many2many('report.606', 'invoice_id')

    invoice_id = fields.Many2one('account.move')
    moneda = fields.Char()
    rnc = fields.Char()
    provider_name = fields.Char()
    tipo_bien_servicio = fields.Char()
    ncf = fields.Char()
    ncf_modificado = fields.Char()
    invoice_date = fields.Date()
    fecha_emision = fields.Char()
    fecha_pago = fields.Char()
    fecha_comprobante_am = fields.Char()
    fecha_comprobante_d = fields.Char()
    fecha_pago_am = fields.Char()
    fecha_pago_d = fields.Char()
    monto_facturado = fields.Float()
    monto_bienes = fields.Float()
    monto_facturado_aitbis = fields.Float()
    monto_facturado_itbis = fields.Float()
    itbis_retenido = fields.Float()
    itbis_sujeto_proporcionalidad = fields.Float()
    itbis_llevado_costo = fields.Float()
    tipo_itbis_llevado_costo = fields.Char()
    itbis_adelantar = fields.Float()
    tipo_itbis_por_adelantar = fields.Char()
    itbis_percibido_compras = fields.Char()
    tipo_isr_retenido = fields.Char()
    isr_retenido = fields.Float()
    monto_facturado_isc = fields.Float()
    monto_otros_imp = fields.Float()
    monto_facturado_propina = fields.Float()
    isr_percibido_compras = fields.Char()
    forma_pago = fields.Char()

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

    def _query(self, with_clause='', fields={}, where='', groupby='',from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = 	"	am.id,			\n"\
					"	am.id as invoice_id,			\n"\
					"	(			\n"\
					"	select			\n"\
					"		rc2.name		\n"\
					"	from			\n"\
					"		res_currency rc2		\n"\
					"	where			\n"\
					"		rc2.id = am.currency_id) as moneda,		\n"\
					"	rp.vat as rnc,			\n"\
					"	rp.name as provider_name,			\n"\
					"	case 		\n"\
					"		when am.l10n_do_expense_type = '01' then '01 - Gastos de Personal'	\n"\
					"		when am.l10n_do_expense_type = '02' then '02 - Gastos por Trabajo, Suministros y Servicios'	\n"\
					"		when am.l10n_do_expense_type = '03' then '03 - Arrendamientos'	\n"\
					"		when am.l10n_do_expense_type = '04' then '04 - Gastos de Activos Fijos'	\n"\
					"		when am.l10n_do_expense_type = '05' then '05 - Gastos de Representacion'	\n"\
					"		when am.l10n_do_expense_type = '06' then '06 - Otras Deducciones Admitidas'	\n"\
					"		when am.l10n_do_expense_type = '07' then '07 - Gastos Financieros'	\n"\
					"		when am.l10n_do_expense_type = '08' then '08 - Gastos Extraordinarios'	\n"\
					"		when am.l10n_do_expense_type = '09' then '09 - Compras y Gastos que forman parte del Costo de Venta'	\n"\
					"		when am.l10n_do_expense_type = '10' then '10 - Adquisiciones de Activos'	\n"\
					"		when am.l10n_do_expense_type = '11' then '11 - Gastos de Seguros'	\n"\
					"	else '' end as tipo_bien_servicio,		\n"\
					"	am.ref as ncf,			\n"\
					"	am.l10n_do_origin_ncf as ncf_modificado,			\n"\
					"	am.invoice_date as invoice_date,			\n"\
					"	to_char(am.invoice_date, 'DD/MM/YYYY') as fecha_emision,		\n"\
					"	coalesce ((			\n"\
					"	select			\n"\
					"		to_char(ap.payment_date, 'DD/MM/YYYY')		\n"\
					"	from			\n"\
					"		account_payment ap		\n"\
					"	where			\n"\
					"		ap.communication = am.ref		\n"\
					"	order by			\n"\
					"		ap.id desc		\n"\
					"	limit 1),			\n"\
					"	'') as fecha_pago,			\n"\
					"	to_char(am.invoice_date, 'YYYYMM') as fecha_comprobante_am,		\n"\
					"	to_char(am.invoice_date, 'DD') as fecha_comprobante_d,		\n"\
					"	coalesce ((			\n"\
					"	select			\n"\
					"		to_char(ap.payment_date, 'YYYYMM')		\n"\
					"	from			\n"\
					"		account_payment ap		\n"\
					"	where			\n"\
					"		ap.communication = am.ref		\n"\
					"	order by			\n"\
					"		ap.id desc		\n"\
					"	limit 1),			\n"\
					"	'') as fecha_pago_am,			\n"\
					"	coalesce ((			\n"\
					"	select			\n"\
					"		to_char(ap.payment_date, 'DD')		\n"\
					"	from			\n"\
					"		account_payment ap		\n"\
					"	where			\n"\
					"		ap.communication = am.ref		\n"\
					"	order by			\n"\
					"		ap.id desc		\n"\
					"	limit 1),			\n"\
					"	'') as fecha_pago_d,			\n"\
					"	((coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join product_product pp on			\n"\
					"		aml.product_id = pp.id		\n"\
					"	inner join product_template pt on			\n"\
					"		pt.id = pp.product_tmpl_id		\n"\
					"	where			\n"\
					"		pt.type = 'service'		\n"\
					"		and aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false		\n"\
					"		and aml.product_id is not null),		\n"\
					"	0)+ coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false		\n"\
					"		and aml.product_id is null),		\n"\
					"	0))+ (coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join product_product pp on			\n"\
					"		aml.product_id = pp.id		\n"\
					"	inner join product_template pt on			\n"\
					"		pt.id = pp.product_tmpl_id		\n"\
					"	where			\n"\
					"		pt.type = 'service'		\n"\
					"		and aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false		\n"\
					"		and aml.product_id is not null),		\n"\
					"	0)+ coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false		\n"\
					"		and aml.product_id is null),		\n"\
					"	0))) as monto_facturado,			\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join product_product pp on			\n"\
					"		aml.product_id = pp.id		\n"\
					"	inner join product_template pt on			\n"\
					"		pt.id = pp.product_tmpl_id		\n"\
					"	where			\n"\
					"		pt.type not in ('service')		\n"\
					"		and aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false),		\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join product_product pp on			\n"\
					"		aml.product_id = pp.id		\n"\
					"	inner join product_template pt on			\n"\
					"		pt.id = pp.product_tmpl_id		\n"\
					"	where			\n"\
					"		pt.type not in ('service')		\n"\
					"		and aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false),		\n"\
					"	0)) as monto_bienes,			\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false),		\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = false),		\n"\
					"	0)) as monto_facturado_aitbis,			\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and aml.name like '"+str('%')+str('ITBIS')+str('%')+"' and aml.name not like '"+str('%')+str('Reten')+str('%')+"'),				\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and aml.name like '"+str('%')+str('ITBIS')+str('%')+"' and aml.name not like '"+str('%')+str('Reten')+str('%')+"'),				\n"\
					"	0)) as monto_facturado_itbis,			\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join account_payment ap on			\n"\
					"		ap.id = aml.payment_id		\n"\
					"	inner join account_account aa on			\n"\
					"		aa.id = aml.account_id		\n"\
					"	where			\n"\
					"		aml.ref = am.ref		\n"\
					"		and (aa.name like '"+str('%')+str('Reten')+str('%')+"'		\n"\
					"		and aa.name like '"+str('%')+str('ITBIS')+str('%')+"')		\n"\
					"		and ap.id = (		\n"\
					"		select		\n"\
					"			ap.id	\n"\
					"		from		\n"\
					"			account_payment ap	\n"\
					"		where		\n"\
					"			ap.communication = am.ref	\n"\
					"		order by		\n"\
					"			ap.id desc	\n"\
					"		limit 1)),		\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join account_payment ap on			\n"\
					"		ap.id = aml.payment_id		\n"\
					"	inner join account_account aa on			\n"\
					"		aa.id = aml.account_id		\n"\
					"	where			\n"\
					"		aml.ref = am.ref		\n"\
					"		and (aa.name like '"+str('%')+str('Reten')+str('%')+"'		\n"\
					"		and aa.name like '"+str('%')+str('ITBIS')+str('%')+"')		\n"\
					"		and ap.id = (		\n"\
					"		select		\n"\
					"			ap.id	\n"\
					"		from		\n"\
					"			account_payment ap	\n"\
					"		where		\n"\
					"			ap.communication = am.ref	\n"\
					"		order by		\n"\
					"			ap.id desc	\n"\
					"		limit 1)),		\n"\
					"	0)) as itbis_retenido,			\n"\
					"	case			\n"\
					"		when coalesce ((		\n"\
					"		select		\n"\
					"			count(aml3.id)	\n"\
					"		from		\n"\
					"			account_move_line aml3	\n"\
					"		inner join account_move am3 on		\n"\
					"			am3.id = aml3.move_id	\n"\
					"		where		\n"\
					"			am3.type in ('out_invoice',	\n"\
					"			'out_refund')	\n"\
					"			and am3.state = 'posted'	\n"\
					"			and (am3.ref like 'B01"+str('%')+"'	\n"\
					"			or am3.ref like 'B02"+str('%')+"')	\n"\
					"			and to_char(am3.invoice_date , 'MM-YYYY') = to_char(am.invoice_date , 'MM-YYYY')	\n"\
					"			and aml3.account_internal_type = 'other'	\n"\
					"			and aml3.exclude_from_invoice_tab = true	\n"\
					"			and aml3.name not like '"+str('%')+str('ITBIS')+str('%')+"'),	\n"\
					"		0) > 0 then (coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.credit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = true	\n"\
					"			and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),	\n"\
					"		0) + coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.debit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = true	\n"\
					"			and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),	\n"\
					"		0))		\n"\
					"		else 0		\n"\
					"	end as itbis_sujeto_proporcionalidad,			\n"\
					"	case			\n"\
					"		when am.itbis_to_cost = true then (coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.credit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = true	\n"\
					"			and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),	\n"\
					"		0) + coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.debit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = true	\n"\
					"			and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),	\n"\
					"		0))		\n"\
					"		else 0		\n"\
					"	end as itbis_llevado_costo,			\n"\
					"	case			\n"\
					"		when am.itbis_to_cost = true 		\n"\
					"		then 		\n"\
					"			case 	\n"\
					"			when am.itbis_to_cost_type = 'bienes_productores_exentos' then 'Bienes - Productores Exentos'	\n"\
					"			when am.itbis_to_cost_type = 'bienes_activos_cat_1' then 'Bienes - Activos Cat. 1'	\n"\
					"			when am.itbis_to_cost_type = 'bienes_otros' then 'Bienes - Otros'	\n"\
					"			when am.itbis_to_cost_type = 'servicios_productores_exentos' then 'Servicios - Productores Exentos'	\n"\
					"			else '' end	\n"\
					"		else ''		\n"\
					"	end as tipo_itbis_llevado_costo,			\n"\
					"	case			\n"\
					"		when coalesce ((		\n"\
					"		select		\n"\
					"			count(aml3.id)	\n"\
					"		from		\n"\
					"			account_move_line aml3	\n"\
					"		inner join account_move am3 on		\n"\
					"			am3.id = aml3.move_id	\n"\
					"		where		\n"\
					"			am3.type in ('out_invoice',	\n"\
					"			'out_refund')	\n"\
					"			and am3.state = 'posted'	\n"\
					"			and (am3.ref like 'B01"+str('%')+"'	\n"\
					"			or am3.ref like 'B02"+str('%')+"')	\n"\
					"			and to_char(am3.invoice_date , 'MM-YYYY') = to_char(am.invoice_date , 'MM-YYYY')	\n"\
					"			and aml3.account_internal_type = 'other'	\n"\
					"			and aml3.exclude_from_invoice_tab = true	\n"\
					"			and aml3.name not like '"+str('%')+str('ITBIS')+str('%')+"'),	\n"\
					"		0) = 0 then (coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.credit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = true	\n"\
					"			and (aml.name like '"+str('%')+str('ITBIS')+str('%')+"' and aml.name not like '"+str('%')+str('Reten')+str('%')+"')),				\n"\
					"		0) + coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.debit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = true	\n"\
					"			and (aml.name like '"+str('%')+str('ITBIS')+str('%')+"' and aml.name not like '"+str('%')+str('Reten')+str('%')+"')),				\n"\
					"		0))		\n"\
					"		else 0		\n"\
					"	end as itbis_adelantar,			\n"\
					"	case			\n"\
					"		when ((coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.credit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		inner join product_product pp on		\n"\
					"			aml.product_id = pp.id	\n"\
					"		inner join product_template pt on		\n"\
					"			pt.id = pp.product_tmpl_id	\n"\
					"		where		\n"\
					"			pt.type = 'servicio'	\n"\
					"			and aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = false	\n"\
					"			and aml.product_id is not null),	\n"\
					"		0)+ coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.credit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = false	\n"\
					"			and aml.product_id is null),	\n"\
					"		0)) + (coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.debit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		inner join product_product pp on		\n"\
					"			aml.product_id = pp.id	\n"\
					"		inner join product_template pt on		\n"\
					"			pt.id = pp.product_tmpl_id	\n"\
					"		where		\n"\
					"			pt.type = 'servicio'	\n"\
					"			and aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = false	\n"\
					"			and aml.product_id is not null),	\n"\
					"		0)+ coalesce ((		\n"\
					"		select		\n"\
					"			sum(aml.debit)	\n"\
					"		from		\n"\
					"			account_move_line aml	\n"\
					"		where		\n"\
					"			aml.move_id = am.id	\n"\
					"			and aml.account_internal_type = 'other'	\n"\
					"			and aml.exclude_from_invoice_tab = false	\n"\
					"			and aml.product_id is null),	\n"\
					"		0))) >= 0 then 'Servicios gravados'		\n"\
					"		else 'Bienes gravados'		\n"\
					"	end as tipo_itbis_por_adelantar,			\n"\
					"	coalesce (null,			\n"\
					"	'') as itbis_percibido_compras,			\n"\
					"	case 				\n"\
					"		when coalesce ((			\n"\
					"		select			\n"\
					"			aa.isr_retencion_type		\n"\
					"		from			\n"\
					"			account_move_line aml		\n"\
					"		inner join account_payment ap on			\n"\
					"			ap.id = aml.payment_id		\n"\
					"		inner join account_account aa on			\n"\
					"			aa.id = aml.account_id		\n"\
					"		where			\n"\
					"			aml.ref = am.ref		\n"\
					"			and (aa.name like '%Reten%'		\n"\
					"			and aa.name like '%ISR%')		\n"\
					"			and ap.id = (		\n"\
					"			select		\n"\
					"				ap.id	\n"\
					"			from		\n"\
					"				account_payment ap	\n"\
					"			where		\n"\
					"				ap.communication = am.ref	\n"\
					"			order by		\n"\
					"				ap.id desc	\n"\
					"			limit 1)),		\n"\
					"		'') = '' then ''			\n"\
					"		when coalesce ((			\n"\
					"		select			\n"\
					"			aa.isr_retencion_type		\n"\
					"		from			\n"\
					"			account_move_line aml		\n"\
					"		inner join account_payment ap on			\n"\
					"			ap.id = aml.payment_id		\n"\
					"		inner join account_account aa on			\n"\
					"			aa.id = aml.account_id		\n"\
					"		where			\n"\
					"			aml.ref = am.ref		\n"\
					"			and (aa.name like '%Reten%'		\n"\
					"			and aa.name like '%ISR%')		\n"\
					"			and ap.id = (		\n"\
					"			select		\n"\
					"				ap.id	\n"\
					"			from		\n"\
					"				account_payment ap	\n"\
					"			where		\n"\
					"				ap.communication = am.ref	\n"\
					"			order by		\n"\
					"				ap.id desc	\n"\
					"			limit 1)),		\n"\
					"		'') = '01' then '01 - Alquileres'			\n"\
					"		when coalesce ((			\n"\
					"		select			\n"\
					"			aa.isr_retencion_type		\n"\
					"		from			\n"\
					"			account_move_line aml		\n"\
					"		inner join account_payment ap on			\n"\
					"			ap.id = aml.payment_id		\n"\
					"		inner join account_account aa on			\n"\
					"			aa.id = aml.account_id		\n"\
					"		where			\n"\
					"			aml.ref = am.ref		\n"\
					"			and (aa.name like '%Reten%'		\n"\
					"			and aa.name like '%ISR%')		\n"\
					"			and ap.id = (		\n"\
					"			select		\n"\
					"				ap.id	\n"\
					"			from		\n"\
					"				account_payment ap	\n"\
					"			where		\n"\
					"				ap.communication = am.ref	\n"\
					"			order by		\n"\
					"				ap.id desc	\n"\
					"			limit 1)),		\n"\
					"		'') = '02' then '02 - Honorarios Por Servicios'			\n"\
					"		when coalesce ((			\n"\
					"		select			\n"\
					"			aa.isr_retencion_type		\n"\
					"		from			\n"\
					"			account_move_line aml		\n"\
					"		inner join account_payment ap on			\n"\
					"			ap.id = aml.payment_id		\n"\
					"		inner join account_account aa on			\n"\
					"			aa.id = aml.account_id		\n"\
					"		where			\n"\
					"			aml.ref = am.ref		\n"\
					"			and (aa.name like '%Reten%'		\n"\
					"			and aa.name like '%ISR%')		\n"\
					"			and ap.id = (		\n"\
					"			select		\n"\
					"				ap.id	\n"\
					"			from		\n"\
					"				account_payment ap	\n"\
					"			where		\n"\
					"				ap.communication = am.ref	\n"\
					"			order by		\n"\
					"				ap.id desc	\n"\
					"			limit 1)),		\n"\
					"		'03') = '' then '03 - Otras Rentas'			\n"\
					"		when coalesce ((			\n"\
					"		select			\n"\
					"			aa.isr_retencion_type		\n"\
					"		from			\n"\
					"			account_move_line aml		\n"\
					"		inner join account_payment ap on			\n"\
					"			ap.id = aml.payment_id		\n"\
					"		inner join account_account aa on			\n"\
					"			aa.id = aml.account_id		\n"\
					"		where			\n"\
					"			aml.ref = am.ref		\n"\
					"			and (aa.name like '%Reten%'		\n"\
					"			and aa.name like '%ISR%')		\n"\
					"			and ap.id = (		\n"\
					"			select		\n"\
					"				ap.id	\n"\
					"			from		\n"\
					"				account_payment ap	\n"\
					"			where		\n"\
					"				ap.communication = am.ref	\n"\
					"			order by		\n"\
					"				ap.id desc	\n"\
					"			limit 1)),		\n"\
					"		'') = '04' then '04 - Otras Rentas (Rentas Presuntas)' end			\n"\
					"	as tipo_isr_retenido,				\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join account_payment ap on			\n"\
					"		ap.id = aml.payment_id		\n"\
					"	inner join account_account aa on			\n"\
					"		aa.id = aml.account_id		\n"\
					"	where			\n"\
					"		aml.ref = am.ref		\n"\
					"		and aa.name like '"+str('%')+str('Reten')+str('%')+"'		\n"\
					"		and aa.name like '"+str('%')+str('ISR')+str('%')+"'		\n"\
					"		and ap.id = (		\n"\
					"		select		\n"\
					"			ap.id	\n"\
					"		from		\n"\
					"			account_payment ap	\n"\
					"		where		\n"\
					"			ap.communication = am.ref	\n"\
					"		order by		\n"\
					"			ap.id desc	\n"\
					"		limit 1)),		\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	inner join account_payment ap on			\n"\
					"		ap.id = aml.payment_id		\n"\
					"	inner join account_account aa on			\n"\
					"		aa.id = aml.account_id		\n"\
					"	where			\n"\
					"		aml.ref = am.ref		\n"\
					"		and aa.name like '"+str('%')+str('Reten')+str('%')+"'		\n"\
					"		and aa.name like '"+str('%')+str('ISR')+str('%')+"'		\n"\
					"		and ap.id = (		\n"\
					"		select		\n"\
					"			ap.id	\n"\
					"		from		\n"\
					"			account_payment ap	\n"\
					"		where		\n"\
					"			ap.communication = am.ref	\n"\
					"		order by		\n"\
					"			ap.id desc	\n"\
					"		limit 1)),		\n"\
					"	0)) as isr_retenido,			\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and aml.name like '"+str('%')+str('ISC')+str('%')+"'),		\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and aml.name like '"+str('%')+str('ISC')+str('%')+"'),		\n"\
					"	0)) as monto_facturado_isc,			\n"\
					"	( coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and (aml.name not like '"+str('%')+str('Propina Legal')+str('%')+"'		\n"\
					"		or aml.name not like '"+str('%')+str('ISC')+str('%')+"'		\n"\
					"		or aml.name not like '"+str('%')+str('ITBIS')+str('%')+"'		\n"\
					"		or aml.name not like '"+str('%')+str('ISR')+str('%')+"')),		\n"\
					"	0) - coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and (aml.name like '"+str('%')+str('Propina Legal')+str('%')+"'		\n"\
					"		or aml.name like '"+str('%')+str('ISC')+str('%')+"'		\n"\
					"		or aml.name like '"+str('%')+str('ITBIS')+str('%')+"'		\n"\
					"		or aml.name like '"+str('%')+str('ISR')+str('%')+"')),		\n"\
					"	0)) + ( coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and (aml.name not like '"+str('%')+str('Propina Legal')+str('%')+"'		\n"\
					"		or aml.name not like '"+str('%')+str('ISC')+str('%')+"'		\n"\
					"		or aml.name not like '"+str('%')+str('ITBIS')+str('%')+"'		\n"\
					"		or aml.name not like '"+str('%')+str('ISR')+str('%')+"')),		\n"\
					"	0) - coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and (aml.name like '"+str('%')+str('Propina Legal')+str('%')+"'		\n"\
					"		or aml.name like '"+str('%')+str('ISC')+str('%')+"'		\n"\
					"		or aml.name like '"+str('%')+str('ITBIS')+str('%')+"'		\n"\
					"		or aml.name like '"+str('%')+str('ISR')+str('%')+"')),		\n"\
					"	0)) as monto_otros_imp,			\n"\
					"	(coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.credit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and aml.name like '"+str('%')+str('Propina Legal')+str('%')+"'),		\n"\
					"	0) + coalesce ((			\n"\
					"	select			\n"\
					"		sum(aml.debit)		\n"\
					"	from			\n"\
					"		account_move_line aml		\n"\
					"	where			\n"\
					"		aml.move_id = am.id		\n"\
					"		and aml.account_internal_type = 'other'		\n"\
					"		and aml.exclude_from_invoice_tab = true		\n"\
					"		and aml.name like '"+str('%')+str('Propina Legal')+str('%')+"'),		\n"\
					"	0)) as monto_facturado_propina,			\n"\
					"	coalesce (null,			\n"\
					"	'') as isr_percibido_compras,			\n"\
					"	(					\n"\
					"	case					\n"\
					"		when (				\n"\
					"		select				\n"\
					"			aj.l10n_do_payment_form			\n"\
					"		from				\n"\
					"			account_payment ap			\n"\
					"		inner join account_journal aj on				\n"\
					"			ap.journal_id = aj.id			\n"\
					"		where				\n"\
					"			ap.communication = am.ref			\n"\
					"		order by				\n"\
					"			ap.id desc			\n"\
					"		limit 1) is null then '04 - Credito'				\n"\
					"		else 				\n"\
					"			case			\n"\
					"				when 		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'cash' then '01 - Efectivo' 		\n"\
					"				when		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'bank' then '02 - Cheque / Transferencia' 		\n"\
					"				when		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'card' then '03 - Tarjeta de Credito / Debito' 		\n"\
					"				when		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'credit' then '04 - Credito' 		\n"\
					"				when		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'swap' then '05 - Permuta' 		\n"\
					"				when		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'bond' then '06 - Bonos o Certificados de Regalo' 		\n"\
					"				when		\n"\
					"				(select		\n"\
					"					aj.l10n_do_payment_form	\n"\
					"				from		\n"\
					"					account_payment ap	\n"\
					"				inner join account_journal aj on		\n"\
					"					ap.journal_id = aj.id	\n"\
					"				where		\n"\
					"					ap.communication = am.ref	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'others' then '07 - Otras Formas de Venta' 		\n"\
					"				end		\n"\
					"	end) as forma_pago					"



        from_ = """account_move am
					inner join res_partner rp on
					rp.id = am.partner_id"""
        where_ = """am.type in ('in_invoice',
					'in_refund')
					and am.ref != ''
					and am.state = 'posted'"""
        groupby_ = "am.id, rp.vat, rp.name"
        for field in fields.values():
            select_ += field
        print("QUERY :::::::::::::::::::::::::: \n",'%s (SELECT %s FROM %s WHERE %s)' % (with_, select_, from_, where_))
        return '%s (SELECT %s FROM %s WHERE %s)' % (with_, select_, from_, where_)



    def action_generate_txt(self):

        self.env.cr.execute(self._query())
        #rec_cursor = self.env['report.606']#.browse(self.env.context['active_ids'])
        self.file_name = 'txt_generacion.txt'
        with open("/home/odoo/txt.txt", "w") as file:

            #for rec in self:
                #file.write(rec.invoice_id.id + "\t")
                #file.write(rec.moneda.id + "\t")
                #file.write(rec.rnc + "\t")
                #file.write(rec.provider_name + "\t")
                #file.write(rec.tipo_bien_servicio + "\t")
                #file.write(rec.ncf + "\t")
                #file.write(rec.ncf_modificado + "\t")
                #file.write(rec.invoice_date + "\t")
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
