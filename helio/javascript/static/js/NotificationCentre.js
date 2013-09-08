var buildNotificationURL = function(targetPath, notificationName){
    if(g_helioSettings.notification_url_builder){
        var notificationURL = g_helioSettings.notification_url_builder(targetPath, notificationName);
    } else {
        var notificationBase = g_helioSettings.notification_base || '/notification/';
        var notificationURL = notificationBase + targetPath + '/' + notificationName;
    }

    if(g_helioSettings.viewstate_id)
        notificationURL += (notificationURL.indexOf('?') == -1 ? '?' : '&')  + 'vs_id=' + g_helioSettings.viewstate_id;

    return notificationURL;
}

var postNotification = function(targetPath, notificationName, notificationData, force, uncritical){
    window.g_helioNotificationCentre.postNotification(targetPath, notificationName, notificationData, force, uncritical);
}

var NotificationCentre = klass(function(){
    this.notifications = [];
    this.notificationActive = false;
    this.postActive = false;
}).methods({
    postNotification: function(targetPath, notificationName, notificationData, force, uncritical){
        if(!force && (this.postActive || this.notificationActive))
            return false;

        var notificationURL = buildNotificationURL(targetPath, notificationName);

        var _this = this;
        if(!uncritical) {
            this.postActive = true;
            this.activityStatusChanged();
        }
        $.post(notificationURL, notificationData, function(callbackData){
            _this.notificationPostCallback(callbackData);
        }, 'json').fail(function(){
            _this.notificationPostFailure();
        });
        return true;
    },
    notificationPostFailure: function(){
        this.postActive = false;
        this.activityStatusChanged();
    },
    notificationPostCallback: function(notificationData){
        if (notificationData == 'refresh') {
            if(g_helioSettings.viewstate_id)
                g_helioSettings.viewstate_id = 0;
            window.location = '/';
            return;
        }

        for(var notificationIndex = 0; notificationIndex < notificationData.length; ++notificationIndex)
            this.queueNotificationDelegation(notificationData[notificationIndex]);

        this.postActive = false;
        this.activityStatusChanged();
        this.processQueue();
    },
    activityStatusChanged: function(){
        // show/hide activity spinners in these callbacks
        if(this.notificationActive || this.postActive){
            if(g_helioSettings && g_helioSettings.activity_activate_callback)
                g_helioSettings.activity_activate_callback();
        } else {
            if(g_helioSettings && g_helioSettings.activity_deactivate_callback)
                g_helioSettings.activity_deactivate_callback();
        }
    },
    queueNotificationDelegation: function(notification){
        this.notifications.push(notification);
    },
    processQueue: function(){
        if(this.notificationActive || this.notifications.length == 0) {
            this.activityStatusChanged();
            if(this.notifications.length == 0 && this.scrollTopOnFinish){
                window.scrollTo(0, 0);
                this.scrollTopOnFinish = false;
            }
            return;
        }

        this.notificationActive = true;
        this.activityStatusChanged();
        var notification = this.notifications.shift();

        this.delegateNotification(notification.target, notification.name, notification.data);
    },
    delegateNotification: function(target, notificationName, data){
        if(notificationName == 'update-vs-id'){
            g_helioSettings.viewstate_id = data;
            sessionStorage.helioViewStateID = data;
            this.notificationComplete();
            return;
        } else if(notificationName == 'change-url') {
            window.location = data;
            return;
        }

        var targetController = g_helioLoader.controllerRegistry[target];

        if(!targetController){
            this.notificationComplete();
            return;
        }

        targetController.processNotification(notificationName, data);
        this.notificationComplete();
    },
    notificationComplete: function(){
        this.notificationActive = false;
        this.processQueue();
    }
});