/** @odoo-module */

import { registry} from '@web/core/registry';
import { loadJS} from '@web/core/assets';
import { getColor } from "@web/core/colors/colors";
const { Component, xml, onWillStart, useRef, onMounted, useState } = owl

export class DynamicDashboardChart extends Component {
    setup() {
        this.doAction = this.props.doAction.doAction
        this.chartRef = useRef("chart");
        this.chartInstance = null;
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
        })
        onMounted(()=> this.renderChart())
    }

    renderChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const widgetType = this.props.widget.graph_type;

        if (widgetType === 'list') {
            this.renderListView();
        } else if (this.props.widget.x_axis && this.props.widget.x_axis.length > 0) {
            const x_axis = this.props.widget.x_axis;
            const y_axis = this.props.widget.y_axis;
            const data = [];
            for (let i = 0; i < x_axis.length; i++) {
                const value = { key: x_axis[i], value: y_axis[i] };
                data.push(value);
            }
            this.chartInstance = new Chart(
                this.chartRef.el,
                {
                    type: widgetType || 'bar',
                    data: {
                        labels: data.map(row => row.key),
                        datasets: [
                            {
                                label: this.props.widget.measured_field,
                                data: data.map(row => row.value),
                                backgroundColor: data.map((_, index) => getColor(index)),
                                hoverOffset: 4
                            }
                        ]
                    }
                }
            );
        }
    }

    renderListView() {
        const x_axis = this.props.widget.x_axis;
        const y_axis = this.props.widget.y_axis;
        const operationType = (this.props.widget.operation || '').toUpperCase();
        const measured_field = (this.props.widget.measured_field || '').toUpperCase();
        const group_by = (this.props.widget.x_field || '').toUpperCase();
        const listContainer = document.createElement('div');
        listContainer.style.maxHeight = '500px';
        listContainer.style.overflowY = 'auto'

        const table = document.createElement('table');
        table.className = 'table table-bordered';
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        const headerRow = document.createElement('tr');
        const keyHeader = document.createElement('th');
        keyHeader.innerText = `${group_by}`;
        const valueHeader = document.createElement('th');
        valueHeader.innerText = `${operationType} VALUE OF ${measured_field}`;
        headerRow.appendChild(keyHeader);
        headerRow.appendChild(valueHeader);
        thead.appendChild(headerRow);

        const combinedData = x_axis.map((value, index) => [value || '', y_axis[index]]);
        combinedData.sort((a, b) => {
            const aValue = a[0] || '';
            const bValue = b[0] || '';

        });

        const sortedX = combinedData.map(item => item[0]);
        const sortedY = combinedData.map(item => item[1]);

        for (let i = 0; i < sortedX.length; i++) {
            const row = document.createElement('tr');
            
            if (i % 2 === 0) {
                row.style.backgroundColor = 'white';
            } else {
                row.style.backgroundColor = '#f0f0f0';
            }

            const keyCell = document.createElement('td');
            keyCell.innerText = sortedX[i];
            
            const valueCell = document.createElement('td');
            valueCell.innerText = sortedY[i];
            
            row.appendChild(keyCell);
            row.appendChild(valueCell);
            tbody.appendChild(row);
        }

        table.appendChild(thead);
        table.appendChild(tbody);
        listContainer.appendChild(table);

        this.chartRef.el.innerHTML = '';
        this.chartRef.el.appendChild(listContainer);
    }


    async getConfiguration(){
        var id = this.props.widget.id
        await this.doAction({
              type: 'ir.actions.act_window',
              res_model: 'dashboard.block',
              res_id: id,
              view_mode: 'form',
              views: [[false, "form"]]
          });
    }

    async getRemove(ev) {
        var id = this.props.widget.id;
        this.props.rpc('/remove/record', { 'id': id }).then((response) => {
            if (response.success) {
                const columnElement = ev.target.closest(`[data-id="${id}"]`);
                if (columnElement) {
                    columnElement.remove();
                }
            }
        });
    }

    getDuplicate(ev){
        var id = this.props.widget.id;
        this.props.rpc('/duplicate/record', { 'id': id }).then((response) => {
            if (response.success) {
                window.location.reload();
            }
        });
    }
}
DynamicDashboardChart.template = xml `
<div style="padding-bottom:30px" t-att-class="this.props.widget.cols +' col-4 block'" t-att-data-id="this.props.widget.id">
    <div class="card">
        <div class="card-header">
            <div class="row">
                <div class="col">
                        <h3><t t-esc="this.props.widget.name"/></h3>
                </div>
                <div class="col custom-button-container">
                    <div>
                        <i title="Duplicate" class="fa fa-files-o  fa-2x cursor-pointer icon" t-on-click="getDuplicate"></i>
                    </div>
                    <div>
                        <i title="Remove" class="fa fa-times fa-2x cursor-pointer icon" t-on-click="getRemove"></i>
                    </div>
                    <div>
                        <i title="Configuration" class="fa fa-cog block_setting fa-2x cursor-pointer icon" t-on-click="getConfiguration"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-body" id="in_ex_body_hide">
            <div class="row">
                <div class="col-md-12 chart_canvas">
                    <div id="chart_canvas">
                        <t t-if="this.props.widget.graph_type === 'list'">
                            <div t-ref="chart"/>
                        </t>
                        <t t-else="">
                            <canvas t-ref="chart"/>
                        </t>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
`


