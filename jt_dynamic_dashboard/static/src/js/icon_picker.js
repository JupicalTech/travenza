/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadCSS,loadJS } from "@web/core/assets";
import { useAutofocus } from "@web/core/utils/hooks"
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useInputField } from "@web/views/fields/input_field_hook";
const { Component,useState,onWillUpdateProps,onMounted} = owl;



export class JtIconPicker extends Component {
    static template = "jt_dynamic_dashboard.JtIconPicker";

    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({ selectedIcon: 'fa fa-star' });

        onMounted(() => {
            this.initIconSelection();
        });
    }

    initIconSelection() {
        document.querySelectorAll('.icon-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();

                const iconClass = event.target.dataset.icon || event.target.parentElement.dataset.icon;
                this.props.record.update({ fa_icon: iconClass });
                this.state.selectedIcon = iconClass;
            });
        });
    }
}

registry.category("fields").add("jticonpicker", {
    component: JtIconPicker,
    supportedTypes: ["char"],
});


export class JtCustomIcon extends Component {
    static template = "jt_dynamic_dashboard.JtCustomIcon";

    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            imgSrc: this.getImgSrc(),
        });

        onMounted(() => {
            this.updateImgSrc();
        });
    }

    getImgSrc() {
        return this.props.record.data.file_name 
            ? `data:image/png;base64,${this.props.record.data.file_name}`
            : "http://placehold.it/180";
    }

    onInputChange(event) {
        const input = event.target;
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const base64String = e.target.result.split(',')[1];
                this.state.imgSrc = e.target.result;
                this.props.record.update({ icon_image: base64String });
                this.updateImgSrc();
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    updateImgSrc() {
        const imgElement = document.getElementById("custom_icon");
        if (imgElement) {
            imgElement.src = this.state.imgSrc;
        }
    }
}


registry.category("fields").add("jtcustomicon", {
    component: JtCustomIcon,
    supportedTypes: ["binary"],
});