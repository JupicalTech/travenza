/** @odoo-module */

import { registry} from '@web/core/registry';
const { Component, xml } = owl
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";


export class DemoDashboardTile extends Component {

    setup() {
        super.setup(...arguments);
        this.action = this.props.doAction
        this.rpc = rpc
    }

    async getRecord() {
        var model_name = this.props.widget.model_name
        if (model_name){
            await this.action.doAction({
            name: this.props.widget.name,
              type: 'ir.actions.act_window',
              res_model: model_name,
              view_mode: 'list',
              views: [[false, "list"]]
          });
        }
    }
    
    async getConfiguration() {
        var id = this.props.widget.id
        await this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'dashboard.block',
            res_id: id,
            view_mode: 'form',
            views: [[false, "form"]]
        });
    }

    async gettileRemove(ev) {
        var id = this.props.widget.id;
        return await rpc('/remove/record', { 'id': id }).then((response) => {
            if (response.success) {
                const tileContainer = ev.target.closest('.tile');
                if (tileContainer) {
                    tileContainer.remove();
                }
            }
        });
    }

    async getDuplicate(ev) {
        var id = this.props.widget.id;        
        return await rpc(
            '/duplicate/record',
            {
                'id': id ,
            }
        ).then((response) => {
            if (response.success) {
                window.location.reload();
            }
        })
    }

}
DemoDashboardTile.template = xml`
<div t-if="this.props.widget.tiles_type === '1'" class="col-sm-12 col-md-12 col-lg-3 tile block">
    <div draggable="true" t-att-style="'background: ' + this.props.widget.tile_color" class="tile-container d-flex justify-content-around align-items-center position-relative w-100 h-auto my-3">
        <a t-on-click="getDuplicate" class="block_setting position-absolute tile-container__duplicate-icon cursor-pointer">
            <i class="fa fa-files-o" style="color: white;"></i>
        </a>
        <a t-on-click="gettileRemove" class="block_setting position-absolute tile-container__remove-icon cursor-pointer">
            <i class="fa fa-times" style="color: white;"></i>
        </a>
        <a t-on-click="getConfiguration" class="block_setting position-absolute tile-container__setting-icon cursor-pointer">
            <i class="fa fa-cog" style="color: white;"></i>
        </a>
        <div t-on-click="getRecord" class="d-flex cursor-pointer">
            <div t-att-style="'color: ' + this.props.widget.icon_color" class="tile-container__icon-container bg-white d-flex justify-content-center align-items-center">
                <i t-if="this.props.widget.icon_type === 'default'" t-att-class="this.props.widget.icon" aria-hidden="true"></i>
                <t t-if="this.props.widget.icon_type === 'custom' and this.props.widget.file_name">
                    <img t-att-src="'data:image/png;base64,' + this.props.widget.file_name" id="custom_icon" style="max-width: 60px; max-height: 60px; border-radius: 100%;" alt="Icon"/>
                </t>
            </div>
            <div class="tile-container__status-container" t-att-style="'color: ' + this.props.widget.text_color">
                <h2 class="status-container__title" t-att-style="'color: ' + this.props.widget.text_color"><t t-esc="this.props.widget.name" /></h2>
                <div class="status-container__figures d-flex flex-wrap align-items-baseline">
                    <h3 class="mb-0 mb-md-1 mb-lg-0 mr-1" t-att-style="'color: ' + this.props.widget.text_color"><t t-esc="this.props.widget.value" /></h3>
                </div>
            </div>
        </div>
    </div>
</div>
<div t-if="this.props.widget.tiles_type === '3'" class="col-sm-12 col-md-12 col-lg-3 tile block">
    <div class="tile-container2 d-flex position-relative w-100 h-auto my-3">
        <div class="tile-left-half d-flex justify-content-around align-items-center" t-att-style="'background: ' + this.props.widget.tile_color">
            <div t-att-style="'color: ' + this.props.widget.icon_color" class="tile-container__icon-container bg-white d-flex justify-content-center align-items-center">
                <i t-if="this.props.widget.icon_type === 'default'" t-att-class="this.props.widget.icon" aria-hidden="true"></i>
                <t t-if="this.props.widget.icon_type === 'custom' and this.props.widget.file_name">
                    <img t-att-src="'data:image/png;base64,' + this.props.widget.file_name" id="custom_icon" style="max-width: 60px; max-height: 60px; border-radius: 100%;" alt="Icon"/>
                </t>
            </div>
            <a t-on-click="getDuplicate" class="block_setting position-absolute tile-container2__duplicate-icon cursor-pointer">
                <i class="fa fa-files-o" style="color: black;"></i>
            </a>
            <a t-on-click="gettileRemove" class="block_setting position-absolute tile-container2__remove-icon cursor-pointer">
                <i class="fa fa-times" style="color: black;"></i>
            </a>
            <a t-on-click="getConfiguration" class="block_setting position-absolute tile-container2__setting-icon cursor-pointer">
                <i class="fa fa-cog" style="color: black;"></i>
            </a>
        </div>
        <div class="tile-right-half d-flex cursor-pointer" t-on-click="getRecord">
            <div class="tile-container__status-container" t-att-style="'color: ' + this.props.widget.text_color">
                <h2 class="status-container__title" t-att-style="'color: ' + this.props.widget.text_color"><t t-esc="this.props.widget.name" /></h2>
                <div class="status-container__figures d-flex flex-wrap align-items-baseline">
                    <h3 class="mb-0 mb-md-1 mb-lg-0 mr-1" t-att-style="'color: ' + this.props.widget.text_color"><t t-esc="this.props.widget.value" /></h3>
                </div>
            </div>
        </div>
    </div>
</div>
<div t-if="this.props.widget.tiles_type === '4'" class="col-sm-12 col-md-12 col-lg-3 tile block">
    <div class="tile-container2 d-flex position-relative w-100 h-auto my-3" t-att-style="'background: ' + this.props.widget.optional_tile_color">
        <div class="tile-left-half d-flex justify-content-around align-items-center" t-att-style="'background: ' + this.props.widget.tile_color">
            <div t-att-style="'color: ' + this.props.widget.icon_color" class="tile-container__icon-container bg-white d-flex justify-content-center align-items-center">
                <i t-if="this.props.widget.icon_type === 'default'" t-att-class="this.props.widget.icon" aria-hidden="true"></i>
                <t t-if="this.props.widget.icon_type === 'custom' and this.props.widget.file_name">
                    <img t-att-src="'data:image/png;base64,' + this.props.widget.file_name" id="custom_icon" style="max-width: 60px; max-height: 60px; border-radius: 100%;" alt="Icon"/>
                </t>
            </div>
            <a t-on-click="getDuplicate" class="block_setting position-absolute tile-container2__duplicate-icon cursor-pointer">
                <i class="fa fa-files-o" style="color: black;"></i>
            </a>
            <a t-on-click="gettileRemove" class="block_setting position-absolute tile-container2__remove-icon cursor-pointer">
                <i class="fa fa-times" style="color: black;"></i>
            </a>
            <a t-on-click="getConfiguration" class="block_setting position-absolute tile-container2__setting-icon cursor-pointer">
                <i class="fa fa-cog" style="color: black;"></i>
            </a>
        </div>
        <div class="tile-right-half d-flex cursor-pointer" t-on-click="getRecord">
            <div class="tile-container__status-container" t-att-style="'color: ' + this.props.widget.text_color">
                <h2 class="status-container__title" t-att-style="'color: ' + this.props.widget.text_color"><t t-esc="this.props.widget.name" /></h2>
                <div class="status-container__figures d-flex flex-wrap align-items-baseline">
                    <h3 class="mb-0 mb-md-1 mb-lg-0 mr-1" t-att-style="'color: ' + this.props.widget.text_color"><t t-esc="this.props.widget.value" /></h3>
                </div>
            </div>
        </div>
    </div>
</div>
`

