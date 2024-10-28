/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useRef, onMounted } from "@odoo/owl";
import { Field } from "@web/views/fields/field";

class DrawingField extends Component {
    setup() {
        this.canvasRef = useRef("canvas");
        this.isDrawing = false;
        this.ctx = null;

        onMounted(() => {
            const canvas = this.canvasRef.el;
            this.ctx = canvas.getContext("2d");
            canvas.width = 400;
            canvas.height = 400;
            this.ctx.strokeStyle = "#000000";
            this.ctx.lineWidth = 2;
            this.attachDrawingEvents(canvas);
        });
    }

    attachDrawingEvents(canvas) {
        canvas.addEventListener("mousedown", () => {
            this.isDrawing = true;
        });
        canvas.addEventListener("mouseup", () => {
            this.isDrawing = false;
            this.saveDrawing();
        });
        canvas.addEventListener("mousemove", (event) => {
            if (this.isDrawing) {
                this.draw(event);
            }
        });
    }

    draw(event) {
        const rect = this.canvasRef.el.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        if (!this.isDrawing) return;
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
    }

    saveDrawing() {
        const canvas = this.canvasRef.el;
        const imageData = canvas.toDataURL("image/png");
        this.trigger("field_changed", { imageData });
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvasRef.el.width, this.canvasRef.el.height);
    }
}

DrawingField.template = "middel_system_manegment.DrawingFieldTemplate";

// Register the field widget
registry.category("fields").add("drawing_field", DrawingField);
