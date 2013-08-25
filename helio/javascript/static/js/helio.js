var helioSetup = function(){
    window.g_helioLoader = new DynamicLoader();
    window.g_helioNotificationCentre = new NotificationCentre();
    window.g_helioSettings = {};

    if(typeof(sessionStorage)!=="undefined"){
        window.g_helioSettings.viewstate_id = sessionStorage.getItem('helioViewStateID');
    }

    g_helioLoader.postViewStateSetup = function(){
        var page = new Controller('page', 'body');
        page.load();
    };

    g_helioLoader.getViewState();
}