const _descriptor = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, "font");

Object.defineProperty(CanvasRenderingContext2D.prototype, "font", {
    get() {
        return _descriptor.get.call(this);
    },
    set(value) {
        _descriptor.set.call(this, value.replace(/'Roboto',\s*arial/g, "Calibri, 'Trebuchet MS', sans-serif"));
    },
    configurable: true,
});