from odoo import tools
from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar


class ReportWizarddgii(models.TransientModel):
	_name = 'report.dgii.wizard'

	year = fields.Char(required=True)
	month = fields.Char(required=True)

	def report_tree_606(self):
		self.ensure_one()
		print("FECHAS \n",self.year,self.month,calendar.monthrange(int(self.year),int(self.month))[1])
		view_view_id = self.env.ref('xmarts_dgii_reports.view_report_606_tree').id
		action = {
			'type': 'ir.actions.act_window',
			'views': [(view_view_id, 'tree')],
			'view_mode': 'tree',
			'name':'Reporte 606 '+str(self.month)+'/'+str(self.year),
			'res_model': 'report.606',
			# 'context':{'year': self.year, 'month': self.month},
			'domain': [('fecha_emision','>=',date.today().strftime(str(self.year)+'-'+str(self.month)+'-01')),('fecha_emision','<=',date.today().strftime(str(self.year)+'-'+str(self.month)+'-'+str(calendar.monthrange(int(self.year),int(self.month))[1])))],
		}
		return action