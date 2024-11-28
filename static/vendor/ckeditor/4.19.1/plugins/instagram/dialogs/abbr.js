CKEDITOR.dialog.add( 'abbr2Dialog', function( editor ) {
    return {
        title: 'Instagram 貼文網址(不包含現實動態)',
        minWidth: 400,
        minHeight: 200,

        contents: [
            {
                elements: [
                    {
                        type: 'text',
                        id: 'abbr2',
                        label: 'Instagram 貼文網址',
                        validate: CKEDITOR.dialog.validate.notEmpty( "Instagram 貼文網址(不包含現實動態)" ),

                        setup: function( element ) {
                            this.setValue( element.getText() );
                        },

                        commit: function( element ) {
                            element.setHtml('<iframe height="460" src="' +  this.getValue() + 'embed" frameBorder="0"></iframe>');
                        }
                    }
                ]
            }
        ],

        onShow: function() {
            var selection = editor.getSelection();
            var element = selection.getStartElement();

            if ( element )
                element = element.getAscendant( 'abbr2', true );

            if ( !element || element.getName() != 'abbr2' ) {
                element = editor.document.createElement( 'abbr2' );
                this.insertMode = true;
            }
            else
                this.insertMode = false;

            this.element = element;
            if ( !this.insertMode )
                this.setupContent( this.element );
        },

        onOk: function() {
            var dialog = this;
            var abbr = this.element;
            this.commitContent( abbr );

            if ( this.insertMode )
                editor.insertElement( abbr );
        }
    };
});