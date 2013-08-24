var helioSetup = function(){
    window.g_helioLoader = DynamicLoader();
    window.g_helioNotificationCentre = NotificationCentre();
    window.g_helioSettings = {};

    g_helioLoader.postViewStateSetup = function(){
        var page = new DynamicLoader('page', 'body');
        page.load();
    };

    g_helioLoader.getViewState();
}