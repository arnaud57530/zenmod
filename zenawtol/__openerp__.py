# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authors: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
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
{
    'name': 'Awtol Specifics',
    'version': '8.0.1.2.0',
    'author': (
        "Denis Lemaire,"
        "Zenwork"
    ),
    'license': 'AGPL-3',
    'category': 'Finance',
    'website': 'http://www.awtol.lu',
    
    'depends': ['base','account','sale'],
    'demo': [],
    'data': ['security/ir.model.access.csv',
             'zenawtol_view.xml',
             'zenawtol_report_view.xml'],
    # tests order matter
    'test': [],
    # 'tests/account_move_line.yml'
    'active': False,
    'installable': True,
    'application': True,
    

    
    
}
