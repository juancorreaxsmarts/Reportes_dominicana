# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _

# class AccountPayment(models.Model):
# 	_name = 'account.payment'
# 	_inherit = 'account.payment'

	# company_currency_amount = fields.Monetary(compute="compute_company_currency_amount", store=True)

	# currency_amount_local = fields.Float(compute="compute_currency_amount_local", store=True)

	# @api.depends('amount', 'move_line_ids')
	# def compute_currency_amount_local(self):
	# 	for rec in self:
	# 		total = 0
	# 		for x in rec.move_line_ids:
	# 			total += x.credit
	# 		rec.currency_amount_local = total

	# @api.depends('amount')
	# def compute_company_currency_amount(self):
	# 	for rec in self:
	# 		rec.company_currency_amount = self.env['res.currency']._compute(rec.currency_id,rec.company_id.currency_id,rec.amount)

class AccountMove(models.Model):
	_name = "account.move"
	_inherit = 'account.move'


	def _get_itbis_to_cost_type(self):
		""" Return the list of expense types required by DGII. """
		# TODO: use self.env["res.partner"]._fields['l10n_do_expense_type'].selection
		return [
			("bienes_productores_exentos", _("Bienes - Productores Exentos")),
			("bienes_activos_cat_1", _("Bienes - Activos Cat. 1")),
			("bienes_otros", _("Bienes - Otros")),
			("servicios_productores_exentos", _("Servicios - Productores Exentos")),
		]


	itbis_to_cost = fields.Boolean(default=False)
	itbis_to_cost_type = fields.Selection(selection="_get_itbis_to_cost_type")


class AccountAccount(models.Model):
	_name = "account.account"
	_inherit = 'account.account'


	def _get_isr_ret_type(self):
		""" Return the list of expense types required by DGII. """
		# TODO: use self.env["res.partner"]._fields['l10n_do_expense_type'].selection
		return [
			("01", _("01 - Alquileres")),
			("02", _("02 - Honorarios Por Servicios")),
			("03", _("03 - Otras Rentas")),
			("04", _("04 - Otras Rentas (Rentas Presuntas)")),
		]

	isr_retencion_type = fields.Selection(selection="_get_isr_ret_type")


class Reporte608(models.Model):
	_name = 'report.608'
	_auto = False

	invoice_id = fields.Many2one('account.move')
	ncf = fields.Char()
	rnc = fields.Char()
	cliente = fields.Char()
	invoice_date = fields.Date()
	fecha_comprobante = fields.Char()
	fecha_dgii = fields.Char()
	tipo_cancelacion = fields.Char()


	def _query(self, with_clause='', fields={}, where='', groupby='',from_clause=''):
		with_ = ("WITH %s" % with_clause) if with_clause else ""

		select_ = 	"	am.id,		\n"\
					"	am.id as invoice_id,		\n"\
					"	am.ref as ncf,		\n"\
					"	rp.vat as rnc,		\n"\
					"	rp.name as cliente,		\n"\
					"	am.invoice_date as invoice_date,		\n"\
					"	to_char(am.invoice_date, 'DD/MM/YYYY') as fecha_comprobante,		\n"\
					"	to_char(am.invoice_date, 'YYYYMMDD') as fecha_dgii,		\n"\
					"	case 		\n"\
					"		when am.cancellation_type = '01' then '01 - Deterioro de Factura Pre-impresa'	\n"\
					"		when am.cancellation_type = '02' then '02 - Errores de Impresion (Factura Pre-impresa)'	\n"\
					"		when am.cancellation_type = '03' then '03 - Impresion Defectuosa'	\n"\
					"		when am.cancellation_type = '04' then '04 - Correccion de la Informacion'	\n"\
					"		when am.cancellation_type = '05' then '05 - Cambio de Productos'	\n"\
					"		when am.cancellation_type = '06' then '06 - Devolucion de Productos'	\n"\
					"		when am.cancellation_type = '07' then '07 - Omision de Productos'	\n"\
					"		when am.cancellation_type = '08' then '08 - Errores en Secuencia de NCF'	\n"\
					"		when am.cancellation_type = '09' then '09 - Por Cese de Operaciones'	\n"\
					"		when am.cancellation_type = '10' then '10 - Perdida o Hurto de Talonarios'	\n"\
					"	else '' end as tipo_cancelacion		"




		from_ = "account_move am	\n"\
				"inner join res_partner rp on		\n"\
				"rp.id = am.partner_id	"

		where_ = 	"am.type in ('out_invoice',	\n"\
					"'out_refund')	\n"\
					"and am.state = 'cancel'	"

		groupby_ = "rp.vat, am.id, rp.name"
		for field in fields.values():
			select_ += field
		print("QUERY :::::::::::::::::::::::::: \n",'%s (SELECT %s FROM %s WHERE %s)' % (with_, select_, from_, where_))
		return '%s (SELECT %s FROM %s WHERE %s)' % (with_, select_, from_, where_)

	# @api.model_cr
	def init(self):
		self._table = 'report_608'
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))


	file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)
	file_data = fields.Binary('Archivo TXT', filters=None, help="")
	def action_generate_txt(self):

		self.file_name = 'txt_generacion.txt'
		with open("C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/xmarts_dgii_reports/wizard/txt_generacion.txt", "w") as file:
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




		self.write({'file_data': base64.encodestring(open("C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/xmarts_dgii_reports/wizard/txt_generacion.txt", "rb").read()),
				'file_name': "606.txt",
				})

		#return self.show_view('Archivo Generado', self._name, 'xmarts_dgii_reports.Reporte606', self.id)




class Reporte607(models.Model):
	_name = 'report.607'
	_auto = False
	_order = 'fecha_emision, ncf'

	def _get_l10n_do_income_type(self):
		""" Return the list of income types required by DGII. """
		return [
			("01", _("01 - Operational Incomes")),
			("02", _("02 - Financial Incomes")),
			("03", _("03 - Extraordinary Incomes")),
			("04", _("04 - Leasing Incomes")),
			("05", _("05 - Income for Selling Depreciable Assets")),
			("06", _("06 - Other Incomes")),
		]

	def _get_l10n_do_payment_form(self):
		""" Return the list of payment forms allowed by DGII. """
		return [
			("cash", _("Cash")),
			("bank", _("Check / Transfer")),
			("card", _("Credit Card")),
			("credit", _("Credit")),
			("swap", _("Swap")),
			("bond", _("Bonds or Gift Certificate")),
			("others", _("Other Sale Type")),
		]


	invoice_id = fields.Many2one('account.move')
	moneda = fields.Char()
	rnc = fields.Char()
	customer_name = fields.Char()
	tipo_id = fields.Char()
	codigo_id = fields.Char()
	ncf = fields.Char()
	ncf_modificado = fields.Char()
	tipo_ingreso = fields.Char()
	codigo_tipo_ingreso = fields.Char()
	tipo_ncf = fields.Many2one(
		comodel_name='l10n_latam.document.type'
	)
	clasif_ingresos = fields.Char()
	invoice_date = fields.Date()
	fecha_emision = fields.Char()
	fecha_pago = fields.Char()
	fecha_emision_amd = fields.Char()

	fecha_pago_retencion = fields.Char()
	monto_facturado_aitbis = fields.Float()
	monto_facturado_itbis = fields.Float()
	itbis_retenido = fields.Float()
	itbis_percibido = fields.Float()
	isr_retenido = fields.Float()
	isr_percibido = fields.Float()
	monto_facturado_isc = fields.Float()
	monto_otros_imp = fields.Float()
	monto_facturado_propina = fields.Float()
	forma_pago = fields.Char()
	efectivo = fields.Float()
	cheque_transferencia_deposito = fields.Float()
	tarjeta_credito_debito = fields.Float()
	credito = fields.Float()
	permuta = fields.Float()
	bonos_certificados = fields.Float()
	otros = fields.Float()


	def _query(self, with_clause='', fields={}, where='', groupby='',from_clause=''):
		with_ = ("WITH %s" % with_clause) if with_clause else ""

		select_ = 	"	am.id,					\n"\
					"	am.id as invoice_id,					\n"\
					"	(					\n"\
					"	select					\n"\
					"		rc2.name				\n"\
					"	from					\n"\
					"		res_currency rc2				\n"\
					"	where					\n"\
					"		rc2.id = am.currency_id) as moneda,				\n"\
					"	rp.vat as rnc,					\n"\
					"	rp.name as customer_name,					\n"\
					"	case					\n"\
					"		when char_length(rp.vat) = 0 then ''				\n"\
					"		when char_length(rp.vat) = 9 then 'RNC'				\n"\
					"		when char_length(rp.vat) >= 11 then 'Cedula'				\n"\
					"		else ''				\n"\
					"	end as tipo_id,					\n"\
					"	case					\n"\
					"		when char_length(rp.vat) = 0 then ''				\n"\
					"		when char_length(rp.vat) = 9 then '1'				\n"\
					"		when char_length(rp.vat) >= 11 then '2'				\n"\
					"		else ''				\n"\
					"	end as codigo_id,					\n"\
					"	am.ref as ncf,					\n"\
					"	am.l10n_do_origin_ncf as ncf_modificado,					\n"\
					"	case 		\n"\
					"		when am.l10n_do_income_type = '01' then '1 - Ingresos por Operaciones (No Financieros)'	\n"\
					"		when am.l10n_do_income_type = '02' then '2 - Ingresos Financieros'	\n"\
					"		when am.l10n_do_income_type = '03' then '3 - Ingresos Extraordinarios'	\n"\
					"		when am.l10n_do_income_type = '04' then '4 - Ingresos por Arrendamientos'	\n"\
					"		when am.l10n_do_income_type = '05' then '5 - Ingresos por Venta de Activo Depreciable'	\n"\
					"		when am.l10n_do_income_type = '06' then '6 - Otros Ingresos'	\n"\
					"		else '' end as tipo_ingreso,	\n"\
					"	case 		\n"\
					"		when am.l10n_do_income_type = '01' then '1'	\n"\
					"		when am.l10n_do_income_type = '02' then '2'	\n"\
					"		when am.l10n_do_income_type = '03' then '3'	\n"\
					"		when am.l10n_do_income_type = '04' then '4'	\n"\
					"		when am.l10n_do_income_type = '05' then '5'	\n"\
					"		when am.l10n_do_income_type = '06' then '6'	\n"\
					"		else '' end as codigo_tipo_ingreso,	\n"\
					"	am.l10n_latam_document_type_id as tipo_ncf,					\n"\
					"	case 								\n"\
					"		when 	(						\n"\
					"				coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.credit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0) + coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.debit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0)					\n"\
					"			) = 0 and (am.ref like 'B01"+str('%')+"'						\n"\
					"			or am.ref like 'B02"+str('%')+"') then 'Ventas Locales Excentas'						\n"\
					"		when 	(						\n"\
					"				coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.credit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0) + coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.debit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0)					\n"\
					"			) = 0 and am.ref like 'B16"+str('%')+"' then 'Ventas Excentas por Exportacion'						\n"\
					"		when 	(						\n"\
					"				coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.credit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0) + coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.debit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0)					\n"\
					"			) = 0 and (am.ref like 'B14"+str('%')+"'						\n"\
					"			or am.ref like 'B15"+str('%')+"') then 'Ventas Excentas por Destino'						\n"\
					"		when 	(						\n"\
					"				coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.credit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0) + coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.debit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0)					\n"\
					"			) > 0 and am.ref not like 'B04"+str('%')+"' then 'Ventas Gravadas'						\n"\
					"		when 	(						\n"\
					"				coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.credit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0) + coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.debit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0)					\n"\
					"			) > 0 and am.ref like 'B04"+str('%')+"' then 'Notas Credito Gravadas'						\n"\
					"		when 	(						\n"\
					"				coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.credit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0) + coalesce ((					\n"\
					"				select					\n"\
					"					sum(aml.debit)				\n"\
					"				from					\n"\
					"					account_move_line aml				\n"\
					"				where					\n"\
					"					aml.move_id = am.id				\n"\
					"					and aml.account_internal_type = 'other'				\n"\
					"					and aml.exclude_from_invoice_tab = true				\n"\
					"					and aml.name like '"+str('%')+str('ITBIS')+str('%')+"'),				\n"\
					"				0)					\n"\
					"			) = 0 and am.ref like 'B04"+str('%')+"' then 'Notas Credito Excentas'						\n"\
					"		else '' end as clasif_ingresos,							\n"\
					"	am.invoice_date as invoice_date,			\n"\
					"	to_char(am.invoice_date, 'DD/MM/YYYY') as fecha_emision,		\n"\
					"	coalesce ((			\n"\
					"	select			\n"\
					"		to_char(ap.payment_date, 'DD/MM/YYYY')		\n"\
					"	from			\n"\
					"		account_payment ap		\n"\
					"	where			\n"\
					"		ap.communication = am.name		\n"\
					"	order by			\n"\
					"		ap.id desc		\n"\
					"	limit 1),			\n"\
					"	'') as fecha_pago,			\n"\
					"	to_char(am.invoice_date, 'YYYYMMDD') as fecha_emision_amd,		\n"\
					"	coalesce ((			\n"\
					"	select			\n"\
					"		to_char(ap.payment_date, 'YYYYMMDD')		\n"\
					"	from			\n"\
					"		account_payment ap		\n"\
					"	where			\n"\
					"		ap.communication = am.name		\n"\
					"	order by			\n"\
					"		ap.id desc		\n"\
					"	limit 1),			\n"\
					"	'') as fecha_pago_retencion,			\n"\
					"	(coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = false),				\n"\
					"	0) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = false),				\n"\
					"	0)) as monto_facturado_aitbis,					\n"\
					"	(coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and aml.name like '"+str('%')+str('ITBIS')+str('%')+"' and aml.name not like '"+str('%')+str('Reten')+str('%')+"'),				\n"\
					"	0) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and aml.name like '"+str('%')+str('ITBIS')+str('%')+"' and aml.name not like '"+str('%')+str('Reten')+str('%')+"'),				\n"\
					"	0)) as monto_facturado_itbis,					\n"\
					"	(coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	inner join account_payment ap on					\n"\
					"		ap.id = aml.payment_id				\n"\
					"	inner join account_account aa on					\n"\
					"		aa.id = aml.account_id				\n"\
					"	where					\n"\
					"		aml.ref = am.name				\n"\
					"		and (aa.name like '"+str('%')+str('Reten')+str('%')+"'				\n"\
					"		and aa.name like '"+str('%')+str('ITBIS')+str('%')+"')				\n"\
					"		and ap.id = (				\n"\
					"		select				\n"\
					"			ap.id			\n"\
					"		from				\n"\
					"			account_payment ap			\n"\
					"		where				\n"\
					"			ap.communication = am.name			\n"\
					"		order by				\n"\
					"			ap.id desc			\n"\
					"		limit 1)),				\n"\
					"	0) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	inner join account_payment ap on					\n"\
					"		ap.id = aml.payment_id				\n"\
					"	inner join account_account aa on					\n"\
					"		aa.id = aml.account_id				\n"\
					"	where					\n"\
					"		aml.ref = am.name				\n"\
					"		and (aa.name like '"+str('%')+str('Reten')+str('%')+"'				\n"\
					"		and aa.name like '"+str('%')+str('ITBIS')+str('%')+"')				\n"\
					"		and ap.id = (				\n"\
					"		select				\n"\
					"			ap.id			\n"\
					"		from				\n"\
					"			account_payment ap			\n"\
					"		where				\n"\
					"			ap.communication = am.name			\n"\
					"		order by				\n"\
					"			ap.id desc			\n"\
					"		limit 1)),				\n"\
					"	0)) as itbis_retenido,					\n"\
					"	coalesce (null,					\n"\
					"	'') as itbis_percibido,					\n"\
					"	(coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	inner join account_payment ap on					\n"\
					"		ap.id = aml.payment_id				\n"\
					"	inner join account_account aa on					\n"\
					"		aa.id = aml.account_id				\n"\
					"	where					\n"\
					"		aml.ref = am.name				\n"\
					"		and aa.name like '"+str('%')+str('Reten')+str('%')+"'				\n"\
					"		and aa.name like '"+str('%')+str('ISR')+str('%')+"'				\n"\
					"		and ap.id = (				\n"\
					"		select				\n"\
					"			ap.id			\n"\
					"		from				\n"\
					"			account_payment ap			\n"\
					"		where				\n"\
					"			ap.communication = am.name			\n"\
					"		order by				\n"\
					"			ap.id desc			\n"\
					"		limit 1)),				\n"\
					"	0) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	inner join account_payment ap on					\n"\
					"		ap.id = aml.payment_id				\n"\
					"	inner join account_account aa on					\n"\
					"		aa.id = aml.account_id				\n"\
					"	where					\n"\
					"		aml.ref = am.name				\n"\
					"		and aa.name like '"+str('%')+str('Reten')+str('%')+"'				\n"\
					"		and aa.name like '"+str('%')+str('ISR')+str('%')+"'				\n"\
					"		and ap.id = (				\n"\
					"		select				\n"\
					"			ap.id			\n"\
					"		from				\n"\
					"			account_payment ap			\n"\
					"		where				\n"\
					"			ap.communication = am.name			\n"\
					"		order by				\n"\
					"			ap.id desc			\n"\
					"		limit 1)),				\n"\
					"	0)) as isr_retenido,					\n"\
					"	coalesce (null,					\n"\
					"	'') as isr_percibido,					\n"\
					"	(coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and aml.name like '"+str('%')+str('ISC')+str('%')+"'),				\n"\
					"	0) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and aml.name like '"+str('%')+str('ISC')+str('%')+"'),				\n"\
					"	0)) as monto_facturado_isc,					\n"\
					"	(( coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and (aml.name not like '"+str('%')+str('Propina Legal')+str('%')+"'				\n"\
					"		or aml.name not like '"+str('%')+str('ISC')+str('%')+"'				\n"\
					"		or aml.name not like '"+str('%')+str('ITBIS')+str('%')+"'				\n"\
					"		or aml.name not like '"+str('%')+str('ISR')+str('%')+"')),				\n"\
					"	0) - coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and (aml.name like '"+str('%')+str('ISR')+str('%')+"'				\n"\
					"		or aml.name like '"+str('%')+str('ISC')+str('%')+"'				\n"\
					"		or aml.name like '"+str('%')+str('ITBIS')+str('%')+"'				\n"\
					"		or aml.name like '"+str('%')+str('ISR')+str('%')+"')),				\n"\
					"	0)) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and (aml.name not like '"+str('%')+str('ISR')+str('%')+"'				\n"\
					"		or aml.name not like '"+str('%')+str('ISC')+str('%')+"'				\n"\
					"		or aml.name not like '"+str('%')+str('ITBIS')+str('%')+"'				\n"\
					"		or aml.name not like '"+str('%')+str('ISR')+str('%')+"')),				\n"\
					"	0) - coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and (aml.name like '"+str('%')+str('ISR')+str('%')+"'				\n"\
					"		or aml.name like '"+str('%')+str('ISC')+str('%')+"'				\n"\
					"		or aml.name like '"+str('%')+str('ITBIS')+str('%')+"'				\n"\
					"		or aml.name like '"+str('%')+str('ISR')+str('%')+"')),				\n"\
					"	0)) as monto_otros_imp,					\n"\
					"	(coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.credit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and aml.name like '"+str('%')+str('ISR')+str('%')+"'),				\n"\
					"	0) + coalesce ((					\n"\
					"	select					\n"\
					"		sum(aml.debit)				\n"\
					"	from					\n"\
					"		account_move_line aml				\n"\
					"	where					\n"\
					"		aml.move_id = am.id				\n"\
					"		and aml.account_internal_type = 'other'				\n"\
					"		and aml.exclude_from_invoice_tab = true				\n"\
					"		and aml.name like '"+str('%')+str('ISR')+str('%')+"'),				\n"\
					"	0)) as monto_facturado_propina,					\n"\
					""\
					""\
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
					"			ap.communication = am.name			\n"\
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
					"					ap.communication = am.name	\n"\
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
					"					ap.communication = am.name	\n"\
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
					"					ap.communication = am.name	\n"\
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
					"					ap.communication = am.name	\n"\
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
					"					ap.communication = am.name	\n"\
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
					"					ap.communication = am.name	\n"\
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
					"					ap.communication = am.name	\n"\
					"				order by		\n"\
					"					ap.id desc	\n"\
					"				limit 1		\n"\
					"				) = 'others' then '07 - Otras Formas de Venta' 		\n"\
					"				end		\n"\
					"	end) as forma_pago,  	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'cash'), 0) as efectivo,	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'bank'), 0) as cheque_transferencia_deposito,	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'card'), 0) as tarjeta_credito_debito,	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'credit'), 0) as credito,	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'swap'), 0) as permuta,	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'bond'), 0) as bonos_certificados,	\n"\
					"	coalesce ((select sum(aml.credit) from account_move_line aml 	\n"\
					"	inner join account_payment ap on aml.payment_id = ap.id 	\n"\
					"	inner join account_journal aj on ap.journal_id = aj.id	\n"\
					"	where ap.communication = am.name and aj.l10n_do_payment_form = 'others'), 0) as otros	"



		from_ = """account_move am
					inner join res_partner rp on
					rp.id = am.partner_id"""
		where_ = """am.type in ('out_invoice',
					'out_refund')
					and am.ref != ''
					and am.state = 'posted'"""
		groupby_ = "am.id, rp.vat, rp.name"
		for field in fields.values():
			select_ += field
		print("QUERY :::::::::::::::::::::::::: \n",'%s (SELECT %s FROM %s WHERE %s)' % (with_, select_, from_, where_))
		return '%s (SELECT %s FROM %s WHERE %s)' % (with_, select_, from_, where_)

	# @api.model_cr
	def init(self):
		self._table = 'report_607'
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))


	file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)
	file_data = fields.Binary('Archivo TXT', filters=None, help="")
	def action_generate_txt(self):

		self.file_name = 'txt_generacion.txt'
		with open("C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/xmarts_dgii_reports/wizard/txt_generacion.txt", "w") as file:
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




		self.write({'file_data': base64.encodestring(open("C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/xmarts_dgii_reports/wizard/txt_generacion.txt", "rb").read()),
				'file_name': "606.txt",
				})

		#return self.show_view('Archivo Generado', self._name, 'xmarts_dgii_reports.Reporte606', self.id)



class Reporte606(models.Model):
	_name = 'report.606'
	_auto = False


	def _get_l10n_do_expense_type(self):
		""" Return the list of expense types required by DGII. """
		# TODO: use self.env["res.partner"]._fields['l10n_do_expense_type'].selection
		return [
			("01", _("01 - Personal")),
			("02", _("02 - Work, Supplies and Services")),
			("03", _("03 - Leasing")),
			("04", _("04 - Fixed Assets")),
			("05", _("05 - Representation")),
			("06", _("06 - Admitted Deductions")),
			("07", _("07 - Financial Expenses")),
			("08", _("08 - Extraordinary Expenses")),
			("09", _("09 - Cost & Expenses part of Sales")),
			("10", _("10 - Assets Acquisitions")),
			("11", _("11 - Insurance Expenses")),
		]

	def _get_itbis_to_cost_type(self):
		""" Return the list of expense types required by DGII. """
		# TODO: use self.env["res.partner"]._fields['l10n_do_expense_type'].selection
		return [
			("bienes_productores_exentos", _("Bienes - Productores Exentos")),
			("bienes_activos_cat_1", _("Bienes - Activos Cat. 1")),
			("bienes_otros", _("Bienes - Otros")),
			("servicios_productores_exentos", _("Servicios - Productores Exentos")),
		]

	def _get_l10n_do_payment_form(self):
		""" Return the list of payment forms allowed by DGII. """
		return [
			("cash", _("Cash")),
			("bank", _("Check / Transfer")),
			("card", _("Credit Card")),
			("credit", _("Credit")),
			("swap", _("Swap")),
			("bond", _("Bonds or Gift Certificate")),
			("others", _("Other Sale Type")),
		]

	def _get_isr_ret_type(self):
		""" Return the list of expense types required by DGII. """
		# TODO: use self.env["res.partner"]._fields['l10n_do_expense_type'].selection
		return [
			("01", _("01 - Alquileres")),
			("02", _("02 - Honorarios Por Servicios")),
			("03", _("03 - Otras Rentas")),
			("04", _("04 - Otras Rentas (Rentas Presuntas)")),
		]

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

	# @api.model_cr
	def init(self):
		self._table = 'report_606'
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

	file_name = fields.Char('txt_generacion.txt', size=256, required=False, help="",)
	file_data = fields.Binary('Archivo TXT', filters=None, help="")
	def action_generate_txt(self):

		self.file_name = 'txt_generacion.txt'
		with open("C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/xmarts_dgii_reports/wizard/txt_generacion.txt", "w") as file:
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




		self.write({'file_data': base64.encodestring(open("C:/Program Files (x86)/Odoo 13.0e/server/odoo/addons/xmarts_dgii_reports/wizard/txt_generacion.txt", "rb").read()),
				'file_name': "606.txt",
				})

		#return self.show_view('Archivo Generado', self._name, 'xmarts_dgii_reports.Reporte606', self.id)
