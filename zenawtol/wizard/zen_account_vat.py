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
from openerp.osv import fields, osv

class report_tax_return_by_account(osv.osv): 
    _name = 'zenawtol.reporttax' 
    _auto = False
    _columns = {
                'id' : fields.integer('id'),
                'ref' : fields.char('ref'),
                'mydate' : fields.date('mydate'),
                'code' : fields.char('code'),
                'name' : fields.char('name'),
                'tax' : fields.char('tax'),
                'tax_amount' : fields.float('tax_amount'),
                'debit': fields.float('debit'),
                'credit' : fields.float('credit'),
                'fiscalyear_id' : fields.integer('fiscalyear'),
                'chart_tax_id' : fields.integer('chart_tax_id'),

                
                }
    _order = 'name,mydate'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'zenawtol_reporttax')
        cr.execute("""
        CREATE OR REPLACE VIEW zenawtol_reporttax AS
            SELECT  account_move_line.id, 
                account_move_line.ref, 
                account_move_line.date as mydate, 
                account_account.code as code, 
                account_account.name as name, 
                account_tax_code.name as tax, 
                account_move_line.tax_amount,
                account_move_line2.debit,
                account_move_line2.credit,
                account_period.fiscalyear_id,
                account_tax_code.id as chart_tax_id
                --, tax.debit, tax.credit 
            FROM account_move_line, 
                account_tax_code,
                account_tax,
                account_account,
                account_move_line as account_move_line2,
                account_period 
            WHERE account_tax_code.id = account_move_line.tax_code_id
                AND account_move_line.tax_code_id > 0
                AND account_tax_code.name ilike 'Base%'
                AND account_account.id = account_move_line.account_id
                and account_tax.base_code_id = account_move_line.tax_code_id
                AND account_move_line2.move_id = account_move_line.move_id
                AND account_move_line2.tax_code_id = account_tax.tax_code_id
            ORDER BY code
        """)




class zen_account_vat_declaration(osv.osv_memory):
    _name = 'zen.account.vat.declaration'
    _description = 'Account Vat Declaration'
    _inherit = "account.common.report"
    _columns = {
        'based_on': fields.selection([('invoices', 'Invoices'),
                                      ('payments', 'Payments'),],
                                      'Based on', required=True),
        'chart_tax_id': fields.many2one('account.tax.code', 'Chart of Tax', help='Select Charts of Taxes', required=False, domain = [('parent_id','=', False)]),
        'display_detail': fields.boolean('Display Detail'),
    }

    def _get_tax(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        taxes = self.pool.get('account.tax.code').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
        return taxes and taxes[0] or False

    _defaults = {
        'based_on': 'invoices',
        'chart_tax_id': _get_tax
    }

    def create_vat(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'zenawtol.reporttax'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        domain = []
        if datas['form']['fiscalyear_id']:
            domain.append(('fiscalyear_id','=',datas['form']['fiscalyear_id']))
        if datas['form']['chart_tax_id']:
            domain.append(('chart_tax_id','=',datas['form']['chart_tax_id']))
        print "ARGARGARG domain ", domain
        taxcode_ids = self.pool.get('zenawtol.reporttax').search(cr,uid,domain)
        print "argargarg : ids ", taxcode_ids
        datas['ids'] = taxcode_ids
        A = self.pool.get('zenawtol.reporttax').read(cr,uid,taxcode_ids)
        print "argargarg obj)", A
        datas['form']['zenvatlines'] = self.pool.get('zenawtol.reporttax').read(cr,uid,taxcode_ids, context=context)

        return self.pool['report'].get_action(cr, uid, [], 'zenawtol.zen_report_vat3', data=datas, context=context)