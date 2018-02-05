# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'GMAO project new',
    'version': '0.0.1',
    'category': 'projets',
    "sequence": 3,
    'summary': '',
    'complexity': "easy",
    'description': """
        This module is module GMAO
    """,
    'author': 'Mazi Smart',
    'website': '',
    'depends': ['base', 'web', 'mail', 'email_template'],
    'data': [
        'security/gmao_security.xml',
        'security/ir.model.access.csv',
        'gmao_view.xml',
        'view/projet_view.xml',
             'view/site_view.xml',
             'view/machine_view.xml',
             'view/intervention_view.xml',
             # 'view/type_maintenance_view.xml',
             'view/preventive_views.xml',
             'view/corrective_views.xml',
             'view/client.xml',
             'view/technicien.xml',
             'view/produits.xml',
             'view/type_view.xml',
             'view/pieces_view.xml',
             'view/alternateur_view.xml',
             'gmao_menu.xml',
             'data/gmao_sequence.xml',
             'data/gmao_demo.xml',
             'data/states.xml',
             'view/bon2travail.xml',
             'report/board.xml',
             'data/alert_view.xml',
             'reports/report.xml',
             'reports/report_machine.xml',
             'reports/report_machine_notif.xml',
             'reports/report_machine_preventive.xml',
             'reports/report_machine_corrective.xml',
             'reports/report_bon_travail.xml',
             

             ],
    'images': [
    ],
    'qweb': ['static/src/xml/template.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



# vue machine
# mettre une alert (js c tu peut ) pour fin de garantie elle verifer d'abore si y'a sur garantie prolongie si y'a rien fin de garantie
# et sur la vue liste de machine la meme chose les affichiers en rouge
# pour les 2 vue interval de 10 jours
#
#
# demande d'intervention
# mettre le workflow  qui marche avec le workflow de maintenace corrective , si je cloture  corrective ca demande et sont bon de travail tous se ferme  auto .
# le workflow on met ceux que je t'es envoyer et les fixé et supprimer la ligne (ajouter une nouvelle colonne )
#
# quand on passe d'une vue a l'autre on recupere les infos de la 1er  exmple
# si je lance une demande d'intervention et je passe sur correctrive il prend tous et de corrective je passe sur bon de travail kif kif il prend tous .
#
# sur la partie bon de travail on ajoute les pieces avec un case vide ou on met le nombre
# on a deja la class pieces
