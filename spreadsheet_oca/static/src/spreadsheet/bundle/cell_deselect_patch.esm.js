// import {components} from "@odoo/o-spreadsheet";
// import {patch} from "@web/core/utils/patch";

// const {Grid} = components;

// patch(Grid.prototype, {
//     onCellClicked(col, row, modifiers, ev) {
//         if (modifiers.addZone) {
//             const model = this.env.model;
//             const zones = model.getters.getSelectedZones();
//             const matchIndex = zones.findIndex(
//                 (z) => z.left === col && z.right === col && z.top === row && z.bottom === row
//             );
//             if (matchIndex !== -1 && zones.length > 1) {
//                 const remaining = zones.filter((_, i) => i !== matchIndex);
//                 const anchor = remaining[remaining.length - 1];
//                 model.selection.selectZone(
//                     {zone: anchor, cell: {col: anchor.left, row: anchor.top}},
//                     {scrollIntoView: false}
//                 );
//                 for (let i = 0; i < remaining.length - 1; i++) {
//                     const z = remaining[i];
//                     model.selection.addCellToSelection(z.left, z.top);
//                 }
//                 ev.preventDefault();
//                 return;
//             }
//         }
//         super.onCellClicked(col, row, modifiers, ev);
//     },
// });
import {components} from "@odoo/o-spreadsheet";
import {patch} from "@web/core/utils/patch";

const {Grid} = components;

function splitZoneExcludingCell(zone, col, row) {
    const result = [];
    if (row > zone.top) {
        result.push({left: zone.left, right: zone.right, top: zone.top, bottom: row - 1});
    }
    if (row < zone.bottom) {
        result.push({left: zone.left, right: zone.right, top: row + 1, bottom: zone.bottom});
    }
    if (col > zone.left) {
        result.push({left: zone.left, right: col - 1, top: row, bottom: row});
    }
    if (col < zone.right) {
        result.push({left: col + 1, right: zone.right, top: row, bottom: row});
    }
    return result;
}

function addZoneToSelection(selection, zone) {
    const result = selection.processEvent({
        anchor: {
            zone: zone,
            cell: {col: zone.left, row: zone.top},
        },
        mode: "newAnchor",
        options: {scrollIntoView: false},
    });
}

function setZoneAsSelection(selection, zone) {
    const result = selection.processEvent({
        anchor: {
            zone: zone,
            cell: {col: zone.left, row: zone.top},
        },
        mode: "overrideSelection",
        options: {scrollIntoView: false},
    });
    // console.log("[deselect] setZoneAsSelection result:", result);
}

patch(Grid.prototype, {
    onCellClicked(col, row, modifiers, ev) {
        if (modifiers.addZone) {
            const model = this.env.model;
            const zones = model.getters.getSelectedZones();

            const matchIndex = zones.findIndex(
                (z) => col >= z.left && col <= z.right && row >= z.top && row <= z.bottom
            );

            if (matchIndex !== -1) {
                const matchedZone = zones[matchIndex];
                const isSingleCell = matchedZone.left === matchedZone.right &&
                                     matchedZone.top === matchedZone.bottom;

                if (zones.length > 1 || !isSingleCell) {
                    const otherZones = zones.filter((_, i) => i !== matchIndex);
                    const splitZones = splitZoneExcludingCell(matchedZone, col, row);
                    const remaining = [...otherZones, ...splitZones];

                    // console.log("[deselect] splitZones:", JSON.stringify(splitZones));
                    // console.log("[deselect] remaining zones to rebuild:", JSON.stringify(remaining));

                    if (remaining.length === 0) {
                        return;
                    }

                    setZoneAsSelection(model.selection, remaining[0]);
                    for (let i = 1; i < remaining.length; i++) {
                        addZoneToSelection(model.selection, remaining[i]);
                    }

                    ev.preventDefault();
                    return;
                }
            }
        }
        super.onCellClicked(col, row, modifiers, ev);
    },
});