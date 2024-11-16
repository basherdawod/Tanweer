odoo.define("middel_system_manegment.binary_attachment_preview", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var field_registry = require("web.field_registry");
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    var BinaryAttachmentPreview = AbstractField.extend({
        template: "FieldBinaryFileUploader",
        supportedFieldTypes: ['binary'],

        events: {
            'click .o_attach': '_onAttach',
            'click .o_attachment_delete': '_onDelete',
            'change .o_input_file': '_onFileChanged',
            'click .o_image_box': '_onFilePDF',
            'click .pdc_close': '_onClosePreview',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.uploadedFiles = {};
            this.uploadingFiles = [];
            this.metadata = {};
            this.previewOpen = {};
        },

        _render: function () {
            this.$('.oe_placeholder_files, .o_attachments')
                .replaceWith($(qweb.render(this.template, {
                    widget: this,
                })));
        },

        _onAttach: function () {
            this.$('.o_input_file').click();
            },
            _onDelete: function (ev) {
                ev.preventDefault();
                ev.stopPropagation();

                // Clear the binary field value
                this._setValue(false); // Clear the value for binary
                this.uploadedFiles = {}; // Reset uploaded files tracker
                this.render(); // Re-render to update the UI
            },


        _onFileChanged: function (ev) {
            ev.stopPropagation();
            var files = ev.target.files;
            if (files.length === 0) return;

            this.uploadingFiles.push(files[0]);
            this._setValue(files[0]); // Set the binary value
            this.$('form.o_form_binary_form').submit();
            ev.target.value = "";
        },

        _onFilePDF: function (ev) {
            var recordId = $(ev.currentTarget).data('id');
            if (!this.previewOpen[recordId]) {
                this.previewOpen[recordId] = true;
                this.$el.append(`
                    <div class="zPDF_iframe" data-record-id="${recordId}">
                        <div class="pdc_close btn btn-primary">close</div>
                        <iframe class="zPDF" scrolling="no" frameborder="0" style="min-height:600px;width:900px;height:100%;" src="/web/content/${recordId}"></iframe>
                    </div>
                `);
            }
        },

        _onClosePreview: function (ev) {
            var recordId = $(ev.currentTarget).closest('.zPDF_iframe').data('record-id');
            delete this.previewOpen[recordId];
            $(ev.currentTarget).closest('.zPDF_iframe').remove();
        },
    });

    field_registry.add("binary_attachment_preview", BinaryAttachmentPreview);
    return BinaryAttachmentPreview;
});
