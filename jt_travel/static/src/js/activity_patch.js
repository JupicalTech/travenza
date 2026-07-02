import { Activity } from "@mail/core/web/activity";
import { patch } from "@web/core/utils/patch";

patch(Activity.prototype, {
    onClickInProgress(ev) {},
});