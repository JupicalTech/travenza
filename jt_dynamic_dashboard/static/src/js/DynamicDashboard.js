/** @odoo-module */

import { registry} from '@web/core/registry';
import { DynamicDashboardTile} from './DynamicDashboardTile'
import { DynamicDashboardChart} from './DynamicDashboardChart'
import { useService } from "@web/core/utils/hooks";
const { Component, mount} = owl
import { onWillStart, onMounted, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";



export class DynamicDashboard extends Component {
    setup(){
        this.orm = useService('orm')
        this.action = useService("action");
        this.rpc = rpc
        const today = new Date().toISOString().split('T')[0];
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
            dateFrom: '', 
            dateTo: today, 
            todayDate: today,
            // financialResults: [],
        });
        this.renderDashboard()
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

    // ============================== ADDED ====================
    onDateChange(event) {
        const value = event.target.value;
        if (event.target.name === 'dateFrom') {
            this.state.dateFrom = value;
        } else if (event.target.name === 'dateTo') {
            this.state.dateTo = value;
        }
        
        // this.state.financialResults = []; 
        
        this.renderDashboard(); 
    }


    // async calculateFinancials(type) {
    //     console.log("Calculating for type:", type); 
        
    //     const params = {
    //         'action_id': this.props.actionId,
    //         'date_from': this.state.dateFrom || '',
    //         'date_to': this.state.dateTo || '',
    //         'calc_type': type,
    //     };
        
    //     try {
    //         const result = await this.rpc('/get/financials', params);
            
    //         if (result.error) {
    //             console.error("Server Error:", result.error);
    //             return;
    //         }

    //         const cardConfig = {
    //             'cost': { label: 'Total Estimated Cost', icon: 'fa-money', color: 'border-danger' },
    //             'revenue': { label: 'Total Revenue', icon: 'fa-line-chart', color: 'border-success' },
    //             'profit': { label: 'Net Profit', icon: 'fa-calculator', color: 'border-primary' }
    //         };

    //         this.state.financialResults = this.state.financialResults.filter(r => r.type !== type);

    //         this.state.financialResults.push({
    //             type: type,
    //             label: cardConfig[type].label,
    //             value: result.total.toLocaleString('en-IN', { minimumFractionDigits: 2 }),
    //             icon: cardConfig[type].icon,
    //             colorClass: cardConfig[type].color
    //         });
            
    //     } catch (err) {
    //         console.error("RPC Failed:", err);
    //     }
    // }

    // removeFinancialCard(type) {
    //     this.state.financialResults = this.state.financialResults.filter(r => r.type !== type);
    // }

     async renderDashboard() {
        const action = this.action;
        const rpc = this.rpc;
        const self = this; 
        const params = {
            'action_id': this.props.actionId,
            'date_from': this.state.dateFrom || '',
            'date_to': this.state.dateTo || '',
        };

        // Use 'self' or arrow functions to maintain context
        await this.rpc('/get/values', params).then((response) => {
        
            if ($('.o_dynamic_dashboard')[0]){
                $('.o_dynamic_dashboard').empty();
                for (let i = 0; i < response.length; i++) {
                    if (response[i].type === 'tile'){
                        mount(DynamicDashboardTile, $('.o_dynamic_dashboard')[0], { props: {
                            widget: response[i], doAction: action
                        }});
                    }
                    else{
                        mount(DynamicDashboardChart, $('.o_dynamic_dashboard')[0], { props: {
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
                    mount(DynamicDashboardTile, $('.o_dynamic_dashboard')[0], { props: {
                        widget: response, doAction: self.action
                    }});
                } else {
                    mount(DynamicDashboardChart, $('.o_dynamic_dashboard')[0], { props: {
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
DynamicDashboard.template = "owl.dynamic_dashboard"
registry.category("actions").add("owl.dynamic_dashboard", DynamicDashboard)
