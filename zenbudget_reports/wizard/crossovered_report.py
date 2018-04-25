# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import tools
from openerp import api
from openerp.osv import fields, osv
from openerp.report import report_sxw
from common_report_header import common_report_header

class easy_crossovered_report_datas(report_sxw.rml_parse, common_report_header):
    _name = 'easy.crossovered.report.datas' 
    _description = 'To-do Report'
    _auto = False
    _columns = {
                'id' : fields.integer('id'),
                'ana' : fields.char('ana'),
                'poste' : fields.date('poste'),
                'res1' : fields.char('res1'),
                'res2' : fields.char('res2'),
                'res3' : fields.char('res3'),
                
                }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'easy_crossovered_report_datas')
        cr.execute("""
        CREATE OR REPLACE VIEW easy_crossovered_report_datas AS
        select account_analytic_account.name as "Analytique" ,account_budget_post.name as "Poste", b1.res1, b2.res2

from (
select distinct crossovered_budget_lines.analytic_account_id, crossovered_budget_lines.general_budget_id
from crossovered_budget_lines
where crossovered_budget_lines.crossovered_budget_id =1 or crossovered_budget_lines.crossovered_budget_id=2

) as res1

left join account_analytic_account on (res1.analytic_account_id = account_analytic_account.id)
left join account_budget_post on (res1.general_budget_id = account_budget_post.id)

left join (select analytic_account_id, general_budget_id, sum(planned_amount) as res1  
           from crossovered_budget_lines where crossovered_budget_lines.crossovered_budget_id =1
           group by analytic_account_id, general_budget_id ) as b1  
     on (res1.analytic_account_id = b1.analytic_account_id and res1.general_budget_id = b1.general_budget_id)


left join (select analytic_account_id, general_budget_id, sum(planned_amount) as res2  
           from crossovered_budget_lines where crossovered_budget_lines.crossovered_budget_id =2
           group by analytic_account_id, general_budget_id ) as b2  
     on (res1.analytic_account_id = b2.analytic_account_id and res1.general_budget_id = b2.general_budget_id)
        """)
    


class easy_crossovered_report(osv.osv_memory):
    _name = 'easy.crossovered.report'

    _columns = {
        'company' : fields.many2one('res.company', 'Company'),
        'crossovered1' : fields.many2one('crossovered.budget','Budget 1'),
        'crossovered2' : fields.many2one('crossovered.budget','Budget 2'),
        'acount_analytics' : fields.many2many('account.analytic.account', string='Compte analytique'),
        'account_budget_post' : fields.many2many('account.budget.post',string='Postes Budgetaires'),
    }
    
    
    
    
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'easy.crossovered.report.datas'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        #domain = []
        #if datas['form']['fiscalyear_id']:
        #    domain.append(('fiscalyear_id','=',datas['form']['fiscalyear_id']))
        #if datas['form']['chart_tax_id']:
        #    domain.append(('chart_tax_id','=',datas['form']['chart_tax_id']))
        
        #taxcode_ids = self.pool.get('zenawtol.reporttax').search(cr,uid,domain, context=context)
        #datas['ids'] = taxcode_ids
        #print "domain : ", domain, taxcode_ids
        #A = self.pool.get('zenawtol.reporttax').read(cr,uid,taxcode_ids, context=context)
        #print "ARGARGARGARG 11111", A
        #datas['form']['zenvatlines'] = self.pool.get('zenawtol.reporttax').read(cr,uid,taxcode_ids, context=context)
        return self.pool['report'].get_action(cr, uid, [], 'zenbudget_reports.rep_crossovered', data=datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


class report_crossoveredbudget_easy(osv.AbstractModel):
    _name = 'report.zenbudget_reports.rep_crossovered'
    _inherit = 'report.abstract_report'
    _template = 'zenbudget_reports.easy_crossovered2'
    _wrapped_report_class = easy_crossovered_report_datas

