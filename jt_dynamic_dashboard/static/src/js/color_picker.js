/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadCSS,loadJS } from "@web/core/assets";
import { useAutofocus } from "@web/core/utils/hooks"
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useInputField } from "@web/views/fields/input_field_hook";
const { Component,useState,onWillUpdateProps,onMounted} = owl;

export class JtColorPicker extends Component {
    static template = "jt_dynamic_dashboard.JtColorPicker";

    static props = {
        ...standardFieldProps,
    };

    setup() {
        super.setup();
        this.state = useState({
           color_value: this.props.record.data.tile_color || "#000000",
        });
        onMounted(() => {
            this.updateTileColor();
        });

    }

    updateTileColor() {
        const tileContainer = document.querySelector('.tile-container');
        const statIcon2 = document.querySelector('.stat-icon2');
        const statIcon3 = document.querySelector('.stat-icon3');
        if (tileContainer) {
            tileContainer.style.backgroundColor = this.state.color_value;
        }
        if (statIcon2) {
            statIcon2.style.backgroundColor = this.state.color_value;
        }
        if (statIcon3) {
            statIcon3.style.backgroundColor = this.state.color_value;
        }
    }

    onColorChange(event) {
        const color = event.target.value;
        this.state.color_value = color;
        this.props.record.update({ tile_color:color });
        const tileContainer = document.querySelector('.tile-container');
        const statIcon2 = document.querySelector('.stat-icon2');
        const statIcon3 = document.querySelector('.stat-icon3');
        if (tileContainer) {
            tileContainer.style.backgroundColor = color;
        }
        if (statIcon2) {
            statIcon2.style.backgroundColor = color;
        }
        if (statIcon3) {
            statIcon3.style.backgroundColor = color;
        }
    }
}

registry.category("fields").add("jtcolor", {
    component: JtColorPicker,
    supportedTypes: ["char"],
});



export class JtTextColorPicker extends Component {
    static template = "jt_dynamic_dashboard.JttextColorPicker";

    static props = {
        ...standardFieldProps,
    };

    setup() {
        super.setup();
        this.state = useState({
           text_color_value: this.props.record.data.text_color || "#000000",
        });
        onMounted(() => {
            this.updateTextColor();
        });

    }

    updateTextColor() {
        const textContainer = document.querySelector('.status-container__figures h3');
        if (textContainer) {
            textContainer.style.color = this.state.text_color_value;
        }
    }

    onTextColorChange(event) {
        const color = event.target.value;
        this.state.text_color_value = color;
        this.props.record.update({ text_color: color });
        this.updateTextColor();
    }
}

registry.category("fields").add("jttextcolor", {
    component: JtTextColorPicker,
    supportedTypes: ["char"],
});


export class JtIconColorPicker extends Component {
    static template = "jt_dynamic_dashboard.JtIconColorPicker";

    static props = {
        ...standardFieldProps,
    };

    setup() {
        super.setup();
        this.state = useState({
           icon_color_value: this.props.record.data.fa_color || "#000000",
        });
        onMounted(() => {
            this.updateIconColor();
        });

    }

    updateIconColor() {
        const iconContainer = document.querySelector('.icon-color');
        if (iconContainer) {
            iconContainer.style.color = this.state.icon_color_value;
        }
    }

    onIconColorChange(event) {
        const color = event.target.value;
        this.state.icon_color_value = color;
        this.props.record.update({ fa_color: color });
        this.updateIconColor();
    }
}

registry.category("fields").add("jticoncolor", {
    component: JtIconColorPicker,
    supportedTypes: ["char"],
});