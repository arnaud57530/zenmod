from datetime import datetime, timedelta, date
import time
from openerp import models, fields, api, _
from openerp.osv import fields,  osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import workflow
from functools import total_ordering
import openerp.addons.decimal_precision as dp


class zen_description(osv.osv):
    _name = "zen.description"
    _columns = {
                'name': fields.char('Nom', translate=True),
                'description': fields.html("Model de descriptions", translate=True),
                }


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
                
                'mysequence' : fields.many2one('ir.sequence','Numero'),
                }

class model_description(osv.osv):
    _name = "esay.desciption"
    _columns = {
                'name' : fields.char('Nom', translate = True),
                'description' : fields.html("Model de descriptions", translate = True)
                }

class model_description_cgv(osv.osv):
    _name = "esay.desciption.cgv"
    _columns = {
                'name' : fields.char('Nom', translate = True),
                'description' : fields.html("Model de descriptions", translate = True)
                }


class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    _columns = {
        'zen_description_model' : fields.many2one('esay.desciption', translate = True),
        'zen_description': fields.html('Description'),
        'zen_description_model_cgv' : fields.many2one('esay.desciption.cgv', translate = True),
        'zen_description_cgv': fields.html('CGV'),
    }

    def model_description_change(self, cr, uid, ids, model_id, myfield, context=None):
        res = {}
        if model_id:
            model_obj = self.pool.get('esay.desciption').browse(cr, uid, model_id, context=context)
            res = None
            if myfield:
                if model_obj.description:
                    res = myfield + "\n" + model_obj.description
                else:
                    res = myfield
            else:
                res = model_obj.description

            res = {'value': {
                'zen_description': res,
                }
            }
        return res

    def model_description_change_cgv(self, cr, uid, ids, model_id, myfield, context=None):
        res = {}
        if model_id:
            model_obj = self.pool.get('esay.desciption.cgv').browse(cr, uid, model_id, context=context)
            res = None
            if myfield:
                if model_obj.description:
                    res = myfield + "\n" + model_obj.description
                else:
                    res = myfield
            else:
                res = model_obj.description
            res = {'value': {
                'zen_description_cgv': res,
                }
            }
        return res

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        print "2vals : ", vals.get('name', '/')
        if vals.get('name', '/') == '/':
	    print "3vals2 ", self.pool.get("res.users").browse(cr, uid, [uid])	    
            seq_user = self.pool.get("res.users").browse(cr, uid, [uid])[0].mysequence
            if seq_user :
                print "seq user : ", str(seq_user), seq_user.name
		
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_user.name, context=context) or '/'
            else:
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order', context=context) or '/'
        if vals.get('partner_id') and any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id', 'fiscal_position']):
            defaults = self.onchange_partner_id(cr, uid, [], vals['partner_id'], context=context)['value']
            if not vals.get('fiscal_position') and vals.get('partner_shipping_id'):
                delivery_onchange = self.onchange_delivery_id(cr, uid, [], vals.get('company_id'), None, vals['partner_id'], vals.get('partner_shipping_id'), context=context)
                defaults.update(delivery_onchange['value'])
            vals = dict(defaults, **vals)
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(sale_order, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("Quotation created"), context=ctx)
        return new_id
    
    def model_description_change(self, cr, uid, ids, model_id, myfield, context=None):
        res = {}
        if model_id:
            model_obj = self.pool.get('esay.desciption').browse(cr, uid, model_id, context=context)
            res = None
            if myfield:
                if model_obj.description:
                    res = myfield + "\n" + model_obj.description
                else:
                    res = myfield
            else:
                res = model_obj.description
                
            res = {'value': {
                'zen_description': res,
                }
            }
        return res
    
   
    def model_description_change_cgv(self, cr, uid, ids, model_id, myfield, context=None):
        res = {}
        if model_id:
            model_obj = self.pool.get('esay.desciption.cgv').browse(cr, uid, model_id, context=context)
            res = None
            if myfield:
                if model_obj.description:
                    res = myfield + "\n" + model_obj.description
                else:
                    res = myfield
            else:
                res = model_obj.description
            res = {'value': {
                'zen_description_cgv': res,
                }
            }
        return res
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """

        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'section_id' : order.section_id.id,
            'zen_description': order.zen_description,
            'zen_description_model': order.zen_description_model.id,
            'zen_description_cgv': order.zen_description_cgv,
            'zen_description_model_cgv': order.zen_description_model_cgv.id,
	        'partner_invoice_id' : order.partner_invoice_id.id,
	        'partner_shipping_id' : order.partner_shipping_id.id,
 
        }
        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals
    
    

    


        
    _columns = {
        'zen_description_model' : fields.many2one('esay.desciption', translate = False),
        'zen_description': fields.html('Description', translate = False),
        'zen_description_model_cgv' : fields.many2one('esay.desciption.cgv', translate = False),
        'zen_description_cgv': fields.html('CGV', translate = False),
        
        }
        
