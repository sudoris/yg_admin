CKEDITOR.plugins.add( 'facebook', {
    icons: 'facebook',
    init: function( editor ) {

        editor.addCommand( 'abbr', new CKEDITOR.dialogCommand( 'abbrDialog' ) );

        editor.ui.addButton('Facebook', {
            label: 'FB粉絲團',
            command: 'abbr',
            toolbar: 'insert'
        });

        if ( editor.contextMenu ) {
            editor.addMenuGroup( 'abbrGroup' );
            editor.addMenuItem( 'abbrItem', {
                label: 'Edit Abbreviation',
                icon: this.path + 'icons/abbr.png',
                command: 'abbr',
                group: 'abbrGroup'
            });

            editor.contextMenu.addListener( function( element ) {
                if ( element.getAscendant( 'abbr', true ) ) {
                    return { abbrItem: CKEDITOR.TRISTATE_OFF };
                }
            });
        }

        CKEDITOR.dialog.add( 'abbrDialog', this.path + 'dialogs/abbr.js' );
    }
});