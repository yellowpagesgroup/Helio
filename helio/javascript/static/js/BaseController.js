var escapeSelector = function(selector){
    return selector.replace(/\./g, '\\.').replace(/:/g, '\\:');
}

var controllerDepthSorter = function(a, b){
    return a.depth - b.depth;
}

var componentNameToAssetPath = function(componentName, assetType){
    var splitPathComponents = componentName.split('.');
    var finalPathComponent = splitPathComponents[splitPathComponents.length - 1];
    var assetPath = componentName.replace(/\./g, '/');
    assetPath += '/' + finalPathComponent + '.' + assetType;
    return assetPath;
}

var controllerClassMapTransform = function(controllerClassMap){
    var newControllerClassMap = [];
    $.each(controllerClassMap, function(controllerPath, controllerAssets) {
        var componentDepth = controllerPath.split('.').length - 1;
        newControllerClassMap.push({
            depth: componentDepth,
            path: controllerPath,
            assets: controllerAssets
        });
    });
    newControllerClassMap.sort(controllerDepthSorter);
    return newControllerClassMap;
}

var cssIsAttached = function(controllerPath){
    return $('#css_' + escapeSelector(controllerPath)).length != 0;
};

var attachCSS = function(controllerPath, componentCSS){
    var staticBase = g_helioSettings.static_base || '/static/';
    var cssPath = staticBase + componentNameToAssetPath(componentCSS, 'css');
    $('head').append('<link rel="stylesheet" type="text/css" href="' + cssPath +'" id="css_' + controllerPath+ '">');
}

var detachCSS = function(controllerPath){
    var cssSelector = escapeSelector(controllerPath);
    $('#css_' + cssSelector).remove();
}

var Controller = klass(function(controllerPath, selector, extraData){
    this.controllerPath = controllerPath;
    if(selector == undefined)
        selector = '#' + controllerPath;
    this.setSelector(selector);
    this.extraData = extraData;
}).methods({
    setSelector: function(selector){
        this.containerSelector = escapeSelector(selector);
        this.$container = $(this.containerSelector);
    },
    buildURL: function(){
        var controllerBase = g_helioSettings.controller_url_base || '/controller/';

        var controllerURL = controllerBase + this.controllerPath;
        if(g_helioSettings.viewstate_id)
            controllerURL += (controllerURL.indexOf('?') == -1 ? '?' : '&')  + 'vs_id=' + g_helioSettings.viewstate_id;

        return controllerURL;
    },
    load: function(controllerData){
        this.$container.data('attached', false);

        if(controllerData)
            this.loadCallback(controllerData);
        else {
            var _parent = this;

            $.get(this.buildURL(), function(data){
                _parent.loadCallback(data);
            }, 'json');
        }
    },
    setContent: function(content){
        this.$container.html(content);
    },
    loadCallback: function(controllerData){
        this.setContent(controllerData.html);

        if(controllerData.class_map == undefined)
            return;

        g_helioLoader.removeChildrenOfController(this.controllerPath);

        var sortedControllerMap = controllerClassMapTransform(controllerData.class_map);

        for(var controllerIndex=0; controllerIndex < sortedControllerMap.length; ++controllerIndex)
            this._setupController(sortedControllerMap[controllerIndex]);
    },
    _setupController: function(controllerData){
        var controllerPath = controllerData.path;
        var controllerAssets = controllerData.assets;
        var attached = false;
        var controllerClassID = controllerAssets['script'];

        if(controllerClassID == undefined){
            g_helioLoader.controllerTypeNameRegistry[controllerPath] = undefined;

            var controller = new Controller(controllerPath);
            detachCSS(controllerPath);
            controller.attach();

            g_helioLoader.controllerRegistry[controllerPath] = controller;

            attached = true;
        } else if(g_helioLoader.controllerRegistry[controllerPath] && (g_helioLoader.controllerTypeNameRegistry[controllerPath] == controllerClassID)){
            if(!g_helioLoader.controllerRegistry[controllerPath].isAttached())
                g_helioLoader.controllerRegistry[controllerPath].attach();

            attached = true;
        }

        if(!attached) {
            detachCSS(controllerPath);
            g_helioLoader.controllerTypeNameRegistry[controllerPath] = controllerClassID;
            g_helioLoader.initializeController(controllerPath, controllerClassID);
        }

        var componentCSS = controllerAssets['css'];

        if(componentCSS != undefined && !cssIsAttached(controllerPath))
            attachCSS(controllerPath, componentCSS);
    },
    attach: function(){
        this.$container.data('attached', true);
    },
    detach: function(){
        this.$container.data('attached', false);
    },
    isAttached: function(){
        return this.$container.data('attached');
    },
    processNotification: function(notificationName, data){
        var splitNotification = notificationName.split(':'), notificationArgs = '';

        if(splitNotification.length > 1){
            notificationName = splitNotification[0];
            notificationArgs = splitNotification[1];
        }

        if(notificationArgs == 'scroll_top')
            g_helioNotificationCentre.scrollTopOnFinish = true;

        if(notificationName == 'load')
            this.load(data);
    }
});
