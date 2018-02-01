# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Vincent Renaville. Copyright 2013-2014 Camptocamp SA
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
from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'
    trigram = fields.Char("Trigram") 

class zen_document_type(models.Model):
    _name = 'zen.document_type'
    name = fields.Char('Document Type')


class zen_histo(models.Model):
    _name = 'zen.histo'
    zen_version = fields.Char('Version') 
    zen_initiateur_modifications = fields.Many2one('res.partner','Initiateur des modifications')
    zen_modifications = fields.Char('Modification')
    zen_date = fields.Date('Date')
    zen_auteurs = fields.Many2many('res.partner', 'zen_histo_autorrel','histo_id','autor_id', 'Auteurs')
    zen_sales_id = fields.Many2one('sale.order','Offre')
    
    
class zen_implication_sales(models.Model):
    _name = 'zen.sale.implication'
    zen_sale_id = fields.Many2one('sale.order','Offre')
    zen_parner_id = fields.Many2one('res.partner','Collaborateur')
    zen_fonction = fields.Char('Fonctions')
    zen_mail = fields.Char('Mail')
    zen_gsm = fields.Char('GSM')
    zen_trigramme  = fields.Char('Trigramme')
    is_supplier = fields.Boolean('Is supplier')
    zen_societe = fields.Many2one('res.partner','Societe', domain="[('is_company','=',True)]")

    @api.onchange('zen_parner_id') 
    def _check_change(self):
        print "mise a jour du partnair"
        self.zen_fonction = self.zen_parner_id.function
        self.zen_gsm = self.zen_parner_id.mobile
        self.zen_trigramme = self.zen_parner_id.trigram
        self.zen_societe = self.zen_parner_id.parent_id.id
        self.zen_mail = self.zen_parner_id.email
        
        
class zen_tag_contract(models.Model):
    _name = 'zen.tag.contract'
    name = fields.Char('Tags')

class zen_model_chapter(models.Model):
    _name = 'zen.model.chapter'
    name = fields.Char('Title')
    zen_model_title = fields.Char('Model Title')
    zen_content = fields.Html('Content')
    zen_sequence = fields.Integer('Sequence')
    zen_tags = fields.Many2many('zen.tag.contract','zen_tag_contract_model_chapter',string= 'Tags')
    #models_ids = fields.Many2many('zen.order.model','zen_order_model2','id_model','id_order', string='Order Model')


class zen_chapter(models.Model):
    _name = 'zen.chapter'
    name = fields.Char('Title')
    zen_number = fields.Integer('Number')
    zen_content = fields.Html('Content')
    zen_model_chapter = fields.Many2one('zen.model.chapter','Chapter model')
    zen_tags = fields.Many2many('zen.tag.contract','zen_tag_contract_chapter', string=  'Tags')
    id_order = fields.Many2one('sale.order', 'Order')
    display_order = fields.Boolean('Display Lines Order')
    display_contract = fields.Boolean('Display Contract')
    
    _order = 'zen_number'
    
    @api.onchange('zen_model_chapter') 
    def _check_change(self):
        self.zen_content = self.zen_model_chapter.zen_content
        self.name = self.zen_model_chapter.zen_model_title
        self.tags = self.zen_model_chapter.zen_tags


class zen_order_model4(models.Model):
    _name = 'zen.order.model4'
    name = fields.Char('Name')
    test_other_field = fields.Char('Tests') 
    chapter_ids = fields.Many2many('zen.model.chapter','zen_order_model3','id_order','id_model', string='Chapters')

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    identifier = fields.Char('Line Ref')


class sale_order(models.Model):
    _inherit = 'sale.order'
    
    zen_document_type = fields.Many2one('zen.document_type', 'Document type')
    zen_model_order = fields.Many2one('zen.order.model4','Order Model')
    zen_object = fields.Char('Objet')
    zen_ourref = fields.Char('Notre ref')
    zen_presentation = fields.Html('Presentation')
    
    zen_mail = fields.Char('Mail')
    zen_gsm = fields.Char('GSM')
    zen_ref = fields.Char('Référence')
    zen_validation = fields.Char('Validation')
    zen_doc_ref = fields.Char('Document de référence')
    zen_annexes = fields.Char('Annexes')
    zen_resume = fields.Text('Resumé')
    zen_histo = fields.One2many('zen.histo', 'zen_sales_id', 'Histo')
    
    zen_implications = fields.One2many('zen.sale.implication', 'zen_sale_id', 'Implications')
    
    zen_table_matiere = fields.Html('Tables de matiere')
    
    zen_sales_text1 = fields.Html('Partie 1')
    zen_sales_text2 = fields.Html('Partie 2')
    
    zen_contents = fields.One2many('zen.chapter','id_order','Contenu')

    @api.onchange('zen_model_order') 
    def _check_change_model(self):
        print "tata"
        self.zen_contents = [(0,0,{'name' : 'toto'})] 


    @api.onchange('user_id') 
    def _check_change_salesperson(self):
        self.zen_mail = self.user_id.login
        self.zen_gsm = self.user_id.phone
         