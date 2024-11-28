CKEDITOR.dialog.add( 'abbrDialog', function( editor ) {
    return {
        title: 'Facebook粉絲頁嵌入',
        minWidth: 400,
        minHeight: 200,

        contents: [
            {
                elements: [
                    {
                        type: 'text',
                        id: 'abbr',
                        label: 'Facebook 粉絲專頁網址',
                        validate: CKEDITOR.dialog.validate.notEmpty( "請輸入Facebook 粉絲專頁網址" ),

                        setup: function( element ) {
                            this.setValue( element.getText() );
                        },

                        commit: function( element ) {
                            element.setHtml('<iframe src="https://www.facebook.com/plugins/page.php?href=' +  this.getValue() +'&tabs&width=340&height=70&small_header=true&adapt_container_width=true&hide_cover=false&show_facepile=true" width="340" height="70" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>');
                        }
                    }
                ]
            }
        ],

        onShow: function() {
            var selection = editor.getSelection();
            var element = selection.getStartElement();

            if ( element )
                element = element.getAscendant( 'abbr', true );

            if ( !element || element.getName() != 'abbr' ) {
                element = editor.document.createElement( 'abbr' );
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