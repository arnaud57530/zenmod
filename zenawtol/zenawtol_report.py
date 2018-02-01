
from openerp import tools
from openerp.osv import fields,osv

class report_alltax(osv.osv): 
    _name = 'zenawtol.report.alltax' 
    _description = 'To-do Report'
    _auto = False
    _columns = {
                'id' : fields.integer('id'),
                'name' : fields.char('name'),
                'mydate' : fields.date('mydate'),
                'journal_entry' : fields.char('journal_entry'),
                'partner_name' : fields.char('partner_name'),
                'partner_vat' : fields.char('partner_vat'),
                'account_code' : fields.char('account_code'),
                'account_name' : fields.char('account_name'),
                
                'mycredit': fields.float('mycredit'),
                'mydebit' : fields.float('mydebit'),
                'tax_amount' : fields.float('tax_amount'),
                'sumcredit' : fields.float('sumcredit'),
                'sumdebit' : fields.float('sumdebit'),
                
                }
    _order = 'name,mydate'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'zenawtol_report_alltax')
        cr.execute("""
        CREATE OR REPLACE VIEW zenawtol_report_alltax AS
        SELECT  account_move_line.id as id , 
                account_tax_code.name as name, 
                account_move_line.date as mydate, 
                account_move.name || ' -- ' || account_move_line.name as "journal_entry", 
                res_partner.name as partner_name, 
                res_partner.vat as partner_vat, 
                account_account.code as account_code, 
                account_account.name as account_name, 
                credit as mycredit, 
                debit as mydebit,
                tax_amount as tax_amount, 
                sumcredit, 
                sumdebit
        FROM account_move_line left join res_partner on (account_move_line.partner_id=res_partner.id), account_tax_code, account_move, account_account,
            (select tax_code_id as id, sum(credit) as sumcredit, sum(debit) as sumdebit 
            from account_move_line where tax_code_id >0
            group by tax_code_id) as sum
        WHERE 
            account_tax_code.id = account_move_line.tax_code_id 
            AND account_move.id = account_move_line.move_id
            AND account_account.id = account_move_line.account_id
            AND sum.id = account_move_line.tax_code_id
            AND tax_code_id > 0
        order by account_tax_code.name;
        """)


class report_base_return(osv.osv): 
    _name = 'zenawtol.report.base_return' 
    _description = 'To-do Report'
    _auto = False
    _columns = {
                'id' : fields.integer('id'),
                'name' : fields.char('name'),
                'mydate' : fields.date('mydate'),
                'journal_entry' : fields.char('journal_entry'),
                'partner_name' : fields.char('partner_name'),
                'partner_vat' : fields.char('partner_vat'),
                'account_code' : fields.char('account_code'),
                'account_name' : fields.char('account_name'),
                
                'mycredit': fields.float('mycredit'),
                'mydebit' : fields.float('mydebit'),
                'tax_amount' : fields.float('tax_amount'),
                'sumcredit' : fields.float('sumcredit'),
                'sumdebit' : fields.float('sumdebit'),
                
                }
    _order = 'name,mydate'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'zenawtol_report_base_return')
        cr.execute("""
        CREATE OR REPLACE VIEW zenawtol_report_base_return AS
        SELECT  account_move_line.id as id , 
                account_tax_code.name as name, 
                account_move_line.date as mydate, 
                account_move.name || ' -- ' || account_move_line.name as "journal_entry", 
                res_partner.name as partner_name, 
                res_partner.vat as partner_vat, 
                account_account.code as account_code, 
                account_account.name as account_name, 
                credit as mycredit, 
                debit as mydebit,
                tax_amount as tax_amount, 
                sumcredit, 
                sumdebit
        FROM account_move_line left join res_partner on (account_move_line.partner_id=res_partner.id), account_tax_code, account_move, account_account,
            (select tax_code_id as id, sum(credit) as sumcredit, sum(debit) as sumdebit 
            from account_move_line where tax_code_id >0
            group by tax_code_id) as sum
        WHERE 
            account_tax_code.id = account_move_line.tax_code_id 
            AND account_move.id = account_move_line.move_id
            AND account_account.id = account_move_line.account_id
            AND sum.id = account_move_line.tax_code_id
            AND tax_code_id > 0
            AND account_tax_code.name NOT ilike 'Taxe%' 
        order by account_tax_code.name;
        """)
        
        
class report_tax_return(osv.osv): 
    _name = 'zenawtol.report.tax_return' 
    _description = 'To-do Report'
    _auto = False
    _columns = {
                'id' : fields.integer('id'),
                'name' : fields.char('name'),
                'mydate' : fields.date('mydate'),
                'journal_entry' : fields.char('journal_entry'),
                'partner_name' : fields.char('partner_name'),
                'partner_vat' : fields.char('partner_vat'),
                'account_code' : fields.char('account_code'),
                'account_name' : fields.char('account_name'),
                
                'mycredit': fields.float('mycredit'),
                'mydebit' : fields.float('mydebit'),
                'tax_amount' : fields.float('tax_amount'),
                'sumcredit' : fields.float('sumcredit'),
                'sumdebit' : fields.float('sumdebit'),
                
                }
    _order = 'name,mydate'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'zenawtol_report_tax_return')
        cr.execute("""
        CREATE OR REPLACE VIEW zenawtol_report_tax_return AS
        SELECT  account_move_line.id as id , 
                account_tax_code.name as name, 
                account_move_line.date as mydate, 
                account_move.name || ' -- ' || account_move_line.name as "journal_entry", 
                res_partner.name as partner_name, 
                res_partner.vat as partner_vat, 
                account_account.code as account_code, 
                account_account.name as account_name, 
                credit as mycredit, 
                debit as mydebit,
                tax_amount as tax_amount, 
                sumcredit, 
                sumdebit
        FROM account_move_line left join res_partner on (account_move_line.partner_id=res_partner.id), account_tax_code, account_move, account_account,
            (select tax_code_id as id, sum(credit) as sumcredit, sum(debit) as sumdebit 
            from account_move_line where tax_code_id >0
            group by tax_code_id) as sum
        WHERE 
            account_tax_code.id = account_move_line.tax_code_id 
            AND account_move.id = account_move_line.move_id
            AND account_account.id = account_move_line.account_id
            AND sum.id = account_move_line.tax_code_id
            AND tax_code_id > 0
            AND account_tax_code.name ilike 'Taxe%'
        order by account_tax_code.name;
        """)
        
        
class report_tax_return_by_account(osv.osv): 
    _name = 'zenawtol.report.tax_return.by.account' 
    _description = 'To-do Report'
    _auto = False
    _columns = {
                'id' : fields.integer('id'),
                'name' : fields.char('name'),
                'mydate' : fields.date('mydate'),
                'journal_entry' : fields.char('journal_entry'),
                'partner_name' : fields.char('partner_name'),
                'partner_vat' : fields.char('partner_vat'),
                'account_code' : fields.char('account_code'),
                'account_name' : fields.char('account_name'),
                
                'mycredit': fields.float('mycredit'),
                'mydebit' : fields.float('mydebit'),
                'tax_amount' : fields.float('tax_amount'),
                'sumcredit' : fields.float('sumcredit'),
                'sumdebit' : fields.float('sumdebit'),
                'code_account_parent' : fields.char('code_parent'),
                'name_account_parent' : fields.char('name_parent'),
                
                }
    _order = 'account_code,name,mydate'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'zenawtol_report_tax_return_by_account')
        cr.execute("""
        CREATE OR REPLACE VIEW zenawtol_report_tax_return_by_account AS
        SELECT  account_move_line.id as id , 
                account_tax_code.name as name, 
                account_move_line.date as mydate, 
                account_move.name || ' -- ' || account_move_line.name as "journal_entry", 
                res_partner.name as partner_name, 
                res_partner.vat as partner_vat, 
                account_account.code as account_code, 
                account_account.name as account_name, 
                credit as mycredit, 
                debit as mydebit,
                tax_amount as tax_amount, 
                sumcredit, 
                sumdebit,
                account_parent.code as code_account_parent,
                account_parent.name as name_account_parent
        FROM account_move_line left join res_partner on (account_move_line.partner_id=res_partner.id), account_tax_code, account_move, account_account,account_account as account_parent,
            (select account_id as id, sum(credit) as sumcredit, sum(debit) as sumdebit 
            from account_move_line where tax_code_id >0
            group by account_move_line.account_id) as sum
        WHERE 
            account_tax_code.id = account_move_line.tax_code_id 
            AND account_move.id = account_move_line.move_id
            AND account_account.id = account_move_line.account_id
            AND sum.id = account_move_line.account_id
            AND tax_code_id > 0
            AND account_parent.id = account_account.parent_id 
            AND account_tax_code.name ilike 'Taxe%'
        order by account_account.code;
        """)
        
        
    