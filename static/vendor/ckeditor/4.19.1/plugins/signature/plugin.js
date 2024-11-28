CKEDITOR.plugins.add( 'signature', {
    icons: 'signature',
    init: function( editor ) {

        editor.addCommand('insertSignature', {
            exec: function (editor) {
                editor.insertHtml('簽名檔文字');
            }
        });

        editor.ui.addButton('Signature', {
            label: '輸入簽名檔',
            command: 'insertSignature',
            toolbar: 'insert'
        });
    }
});