/**
 * @license Copyright (c) 2003-2022, CKSource Holding sp. z o.o. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_config.html

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbar = [
		{ name: 'styles', items: ['Format', 'Font', 'FontSize' ] },
		{ name: 'basicstyles', items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'CopyFormatting', 'RemoveFormat' ] },
		{ name: 'paragraph', items: [ 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language' ] },
		{ name: 'colors', items: [ 'TextColor', 'BGColor' ] },
		{ name: 'links', items: [ 'Link', 'Unlink'] },
		{ name: 'insert', items: [ 'Image', 'HorizontalRule', 'Smiley', 'PageBreak'] }
	];

	config.contentsCss = ["body {font-size: 12px;}"]
	config.fontSize_defaultLabel = '12px';
	config.allowedContent = true;
	config.extraPlugins = ['font', 'panel', 'panelbutton', 'floatpanel', 'colordialog', 'button','colorbutton', 'basicstyles', 'fakeobjects', 'dialogui', 'dialog'];
	config.colorButton_enableAutomatic = false;
	config.colorButton_enableMore = true;

	// 影像上傳
	config.filebrowserUploadMethod = 'form';
	config.image_previewText=' ';
	config.removeDialogTabs = 'image:advanced';
	config.filebrowserImageUploadUrl= "/dashboard/user/ckeditor-ajax-upload-image";
};
