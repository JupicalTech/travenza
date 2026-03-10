/**@odoo-module **/
import { registry } from "@web/core/registry";
import { DemoDashboardTile2 } from './demo_tile2'
import { Component } from  "@odoo/owl";
import { DemoDashboardChart} from './demo_chart'
import { onWillStart, onMounted, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");
const { mount } = owl
import { rpc } from "@web/core/network/rpc";


class JtDashboard2 extends Component {
    setup(){
        this.orm = useService('orm')
        this.action = useService("action");
        this.rpc = rpc
        this.renderDashboard()
        this.state = useState({
            isChart: true,
            isTile: false,
            iconColor: '',
            textColor:'#f3eded',
            iconClass: '',
            models: [],
            fields: [],
            groupby_fields: [],
            isLoading: true,  
            operationType:'',
            tileColor: '#145e8d',

        });
        this.fetchModels();
        onMounted(() => {
            this.initIconSelection();
            this.initSelectColorChange();
        });


    }

    async fetchModels() {
        const models = await this.orm.call("dashboard.block", "get_models", [], {});
        this.state.models = models || [];

        this.state.isLoading = false;
    }

    async onModelChange(event) {
        const modelId = event.target.value;
        if (modelId) {
          this.state.fields = [];
          this.fetchFields(modelId);
          this.GroupbyfetchFields(modelId);
        } else {
          this.state.fields = [];
          this.state.groupby_fields = [];
        }
      }

    async fetchFields(modelId) {
        const fields = await this.orm.call("dashboard.block", "get_fields",[modelId], {});
        this.state.fields = fields || [];
      }

    async GroupbyfetchFields(modelId) {
        const groupby_fields = await this.orm.call("dashboard.block", "groupby_fields",[modelId], {});
        this.state.groupby_fields = groupby_fields || [];
      }

    changeColor(event) {
        this.state.tileColor = event.target.value;
    }
    
   changeIconColor(event) {
        this.state.iconColor = event.target.value;
    }

    changeTextColor(event) {
        this.state.textColor = event.target.value;
    }

    changeIconClass(event) {
        this.state.iconClass = event.target.value;
    }

    changeBlockType(event) {
        this.state.isChart = event.target.value === 'graph';
        this.state.isTile = event.target.value === 'tile';
    }

    operationType(event){
        this.state.operationType = event.target.value;
    }

     async renderDashboard() {
        const action = this.action;
        const rpc = this.rpc;
        await this.rpc('/get/values', {'action_id': this.props.actionId}).then(function(response){
            if ($('.o_dynamic_dashboard')[0]){
                $('.o_dynamic_dashboard').empty();
                for (let i = 0; i < response.length; i++) {
                    if (response[i].type === 'tile'){
                        mount(DemoDashboardTile2, $('.o_dynamic_dashboard')[0], { props: {
                            widget: response[i], doAction: action
                        }});
                    }
                    else{
                        mount(DemoDashboardChart, $('.o_dynamic_graph')[0], { props: {
                            widget: response[i], doAction: action, rpc: rpc
                        }});
                    }
                }
            }
        })
    }

    async _onClick_add_block(e) {
        var self = this;
        var type = document.getElementById("blockType").value;
        var requestData = {
            'type': type,
            'action_id': self.props.actionId,
        };

        var allFieldsFilled = true;
        var requiredFields = [];

        if (type === 'tile' || type === 'graph') {
            requestData['model_id'] = document.getElementById("modelId").value;
            requestData['operation_type'] = document.getElementById("operationType").value;
            requestData['field_id'] = document.getElementById("fieldId").value;

            if (type === 'tile') {
                requestData['color'] = this.state.tileColor;
                requestData['icon_color'] = document.getElementById("iconcolorPicker").value;
                requestData['text_color'] = this.state.textColor;
                requestData['icon'] = document.getElementById("iconClass").value;
                requiredFields = ['colorPicker', 'iconcolorPicker', 'textcolorPicker', 'modelId', 'operationType', 'fieldId'];
            } else if (type === 'graph') {
                requestData['chart_type'] = document.getElementById("chartType").value;
                requestData['graph_size'] = document.getElementById("graphSize").value;
                requestData['group_by_field_id'] = document.getElementById("groupByfieldId").value;
                requiredFields = ['chartType', 'graphSize', 'modelId', 'operationType', 'fieldId', 'groupByfieldId'];
            }

            for (var i = 0; i < requiredFields.length; i++) {
                var fieldElement = document.getElementById(requiredFields[i]);
                if (!fieldElement.value) {
                    allFieldsFilled = false;
                    fieldElement.classList.add("red-underline");
                    fieldElement.addEventListener('input', function() {
                        if (fieldElement.value) {
                            fieldElement.classList.remove("red-underline");
                        }
                    });
                } else {
                    fieldElement.classList.remove("red-underline");
                }
            }

            var operationType = document.getElementById("operationType").value;
            var fieldId = document.getElementById("fieldId").value;
            var fieldTypeResponse = await this.orm.call("dashboard.block", "get_field_type",[], {'field_id': fieldId});

            if ((operationType === 'sum' || operationType === 'avg') && fieldTypeResponse['field_type'] === 'selection') {
                allFieldsFilled = false;
                
                var operationTypeText = operationType === 'sum' ? 'Sum' : 'Average';
                
                var fieldName = fieldTypeResponse['field_name'];

                this.action.doAction({
                    type: "ir.actions.client",
                    tag: "display_notification",
                    params: {
                        "title": 'Input Error',
                        "message": `${operationTypeText} operation cannot be applied to the field "${fieldName}".`,
                        "sticky": false,
                        "type": 'danger'
                    }
                });

                document.getElementById("operationType").value = "";

                return;
            }
        }

        if (!allFieldsFilled) {
            this.action.doAction({
                type: "ir.actions.client",
                tag: "display_notification",
                params: {
                    "title": 'Warning',
                    "message": "Please fill all required fields.",
                    "sticky": false,
                    "type": 'danger'
                }
            });
        } else {
            await this.rpc('/create/tile', requestData).then(function(response) {
                if (response['type'] == 'tile') {
                    mount(DemoDashboardTile2, $('.o_dynamic_dashboard')[0], { props: {
                        widget: response, doAction: self.action
                    }});
                } else {
                    mount(DemoDashboardChart, $('.o_dynamic_dashboard')[0], { props: {
                        widget: response, doAction: self.action, rpc: self.rpc
                    }});
                }
                self.resetFields(requiredFields);
                self.renderDashboard();
            });
        }
    }

    resetFields(fields) {
        fields.forEach(function(fieldId) {
            var fieldElement = document.getElementById(fieldId);
            fieldElement.value = '';
            fieldElement.classList.remove("red-underline");
            if (fieldElement.tagName.toLowerCase() === 'select') {
                fieldElement.style.color = '#241f1e61';
            }
        });
    }


    initIconSelection() {
        const iconClassInput = document.getElementById('iconClass');
        const selectedIcon = document.getElementById('selectedIcon');
        document.querySelectorAll('.dropdown-item_custom.icon-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();

                const iconClass = event.target.dataset.icon || event.target.parentElement.dataset.icon;

                if (iconClass) {
                    iconClassInput.value = iconClass;
                    selectedIcon.className = iconClass;
                }
            });
        });
    }

    initSelectColorChange() {
        const selectElements = document.querySelectorAll('select.o-autocomplete--input');
        selectElements.forEach(select => {
            select.addEventListener('change', (event) => {
                if (event.target.value !== '') {
                    event.target.style.color = '#000000';
                }
            });
        });
    }
}
JtDashboard2.template = "owl.DashboardTemplate2";
actionRegistry.add("owl.jt_dashboard_tag2", JtDashboard2);