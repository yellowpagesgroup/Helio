var DynamicLoader = klass(function(){
    this.controllerRegistry = {}; // map the controller path to the current instance
    this.controllerLoadCallbacks = {};
    this.currentRequestDependencies = {};
    this.dependentOn = {};
    this.pendingSetup = {};
    this.attachCallbacks = {};
    this.controllerTypeRegistry = {}; // map controller type name to js class
    this.controllerTypeNameRegistry = {}; // map controller path to class name
}).methods({
    initializeController: function(controllerPath, typeIdentifier){
        if(typeIdentifier == null || typeIdentifier == undefined || this.controllerTypeRegistry[typeIdentifier]){
            this._doAttach(controllerPath, typeIdentifier);
            return;
        }

        var _this = this;

        if(this.attachCallbacks[typeIdentifier] == undefined)
            this.attachCallbacks[typeIdentifier] = [];

         this.attachCallbacks[typeIdentifier].push({ // the actual class init happens on callback after the class is available
            callback: function(data){
                _this._doAttach(data.controllerPath, data.typeIdentifier);
            },
            data: {typeIdentifier: typeIdentifier, controllerPath: controllerPath}
        });

        this.retrieveClass(typeIdentifier); // initiate the retrieval of the component code
    },
    removeChildrenOfController: function(rootControllerPath){
        var _this = this;
         $.each(this.controllerRegistry, function(controllerPath, controllerInstance){
            if(controllerPath.indexOf(rootControllerPath + '.') === 0 && rootControllerPath != controllerPath)
                delete _this.controllerRegistry[controllerPath];
        });
    },
    retrieveClass: function(typeIdentifier){
        if(this.pendingSetup[typeIdentifier] != undefined) // this is already queued
            return;

        this.pendingSetup[typeIdentifier] = true;

        var staticBase = g_helioSettings.static_base || '/static/';
        var scriptPath = staticBase + componentNameToAssetPath(typeIdentifier, 'js');

        $.getScript(scriptPath);
    },
    _doAttach: function(controllerPath, typeIdentifier){

    },
    queueClassRegister: function(typeIdentifier, dependencies, setupCallback){

    }
});

var registerClass = function(typeIdentifer, dependencies, setupCallback){
    if(typeof(dependencies) == 'string')
        dependencies = [dependencies];

    g_helioLoader.queueClassRegister(typeIdentifer, dependencies, setupCallback);
}
