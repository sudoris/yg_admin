/* Add here all your JS customizations */
var stack_bar_bottom = {"dir1": "up", "dir2": "right", "spacing1": 0, "spacing2": 0};

function getNowFormatDate() {
    var date = new Date();
    var seperator1 = "-";
    var seperator2 = ":";
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    var hour = date.getHours();
    var minute = date.getMinutes();
    var second = date.getSeconds();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    if(hour >= 0 && hour <= 9) {
        hour = "0" + hour;
    }
    if(minute >= 0 && minute <= 9) {
        minute = "0" + minute;
    }
    if(second >= 0 && second <= 9) {
        second = "0" + second;
    }
    var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
        + " " + hour + seperator2 + minute
        + seperator2 + second;
    return currentdate;
}

function notify_success(success) {
    if(!success) return;
    if(Array.isArray(success)) {
        success.forEach(function (message) {
            make_success_notify(message);
        });
    } else {
        make_success_notify(success);
    }
}

function make_success_notify(message) {
    var notice = new PNotify({
        title: message,
        text: getNowFormatDate(),
        addclass: 'notification-primary stack-bar-bottom',
        icon: 'fa fa-check',
        stack: stack_bar_bottom,
        width: "70%",
        buttons: {
            closer: true,
            sticker: false
        }
    });
    notice.get().click(function() {
        notice.remove();
    });
}

function notify_error(error) {
    if(!error) return;
    if(Array.isArray(error)) {
        error.forEach(function (message) {
            make_error_notify(message);
        });
    } else {
        make_error_notify(error);
    }
}

function make_error_notify(message) {
    var date = new Date();
    var notice = new PNotify({
        title: message,
        text: getNowFormatDate(),
        type: 'error',
        addclass: 'stack-bar-bottom',
        stack: stack_bar_bottom,
        width: "70%",
        buttons: {
            closer: true,
            sticker: false
        }
    });
    notice.get().click(function() {
        notice.remove();
    });
}