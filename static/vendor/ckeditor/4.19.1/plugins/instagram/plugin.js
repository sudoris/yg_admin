CKEDITOR.plugins.add( 'instagram', {
    icons: 'instagram',
    init: function( editor ) {

        editor.addCommand( 'abbr2', new CKEDITOR.dialogCommand( 'abbr2Dialog' ) );

        editor.ui.addButton('Instagram', {
            label: 'Instagram',
            command: 'abbr2',
            toolbar: 'insert'
        });

        if ( editor.contextMenu ) {
            editor.addMenuGroup( 'abbr2Group' );
            editor.addMenuItem( 'abbr2Item', {
                label: 'Edit Abbreviation',
                icon: this.path + 'icons/abbr.png',
                command: 'abbr2',
                group: 'abbr2Group'
            });

            editor.contextMenu.addListener( function( element ) {
                if ( element.getAscendant( 'abbr2', true ) ) {
                    return { abbrItem: CKEDITOR.TRISTATE_OFF };
                }
            });
        }

        CKEDITOR.dialog.add( 'abbr2Dialog', this.path + 'dialogs/abbr.js' );
    }
});