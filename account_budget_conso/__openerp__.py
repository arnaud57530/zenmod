# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#Consolidation du budget
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Budgets Consolidation',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
            Consolidation du Budget
        """,
    'author': 'CIERIA',
    'depends': ['account', 'report'],
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',

        'account_budget_conso_report.xml',

        'wizard/account_budget_conso_crossovered_summary_report_view.xml',

        'views/report_crossoveredbudgetconso.xml',
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: