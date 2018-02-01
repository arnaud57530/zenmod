openerp.GMAO = function(instance){

    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;


    instance.web_kanban.KanbanView.include({
        on_record_moved : function(record, old_group, old_index, new_group, new_index) {

            if ((old_group.value > new_group.value) && ((this.dataset.model == 'preventive') || (this.dataset.model == 'corrective') || (this.dataset.model == 'intervention')))
            {
                swal({title:"Désolé", text:"Il n'est pas autorisé de revenir à l'état précédent !"})
                this.do_reload();
            }
            else
            {
                this._super(record, old_group, old_index, new_group, new_index);
            }
        },
    });

}