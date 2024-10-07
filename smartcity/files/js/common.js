(function (window, $, undefined) {
    "use strict";

    $(function () {

        $('.jsRowService').change(function () {
            if ($("#service1").prop("checked") == true) {
                $('.jsRowInputNo').show();
                $('.jsRowAgree4').hide();
                $('.jsTextService1').show();
                $('.jsTextService2').hide();
            } else {
                $('.jsRowInputNo').hide();
                $('.jsRowAgree4').show();
                $('.jsTextService1').hide();
                $('.jsTextService2').show();
            }

        });



    });


})(this, jQuery);
