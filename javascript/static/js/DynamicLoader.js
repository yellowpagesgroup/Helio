var DynamicLoader = klass(function(){
    this.controllerRegistry = {}; // map the controller path to the current instance
    this.classLoadCallbacks = {};
    this.currentRequestDependencies = {};
    this.dependentOn = {};
    this.pendingSetup = {};
    this.attachCallbacks = {};
    this.typeRegistry = {}; // map controller type name to js class
    this.controllerTypeNameRegistry = {}; // map controller path to class name
}).methods({
    initializeController: function(controllerPath, typeIdentifier){
        if(typeIdentifier == null || typeIdentifier == undefined || this.typeRegistry[typeIdentifier]){
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
    processLoadNotification: function(typeIdentifier){

    },
    setupAndRegisterAfterDependenciesComplete: function(typeIdentifier, setupCallback){
        this.typeRegistry[typeIdentifier] = setupCallback();
        delete this.pendingSetup[typeIdentifier];
        this.processLoadNotification(typeIdentifier);
    },
    queueClassRegister: function(typeIdentifier, dependencies, setupCallback){
        if(dependencies == null || dependencies.length == 0) {
            this.setupAndRegisterAfterDependenciesComplete(typeIdentifier, setupCallback);
            return;
        } else {
            this.currentRequestDependencies[typeIdentifier] = dependencies;

            if(this.classLoadCallbacks[typeIdentifier] == undefined)
                this.classLoadCallbacks[typeIdentifier] = [];

            var _this = this;
            this.classLoadCallbacks[typeIdentifier].push({
                callback: function(){ // after the component is loaded, call its setup and push it into type registry
                    _this.typeRegistry[typeIdentifier] = setupCallback();
                    delete _this.pendingSetup[typeIdentifier];
                }
            });
        }

        var unloadedDependenciesCount = 0;

        for(var dependencyIndex = 0; dependencyIndex < dependencies.length; ++dependencyIndex){
            var dependency = dependencies[dependencyIndex];

            if(dependency == null || this.typeRegistry[dependency] != undefined) // dependency already loaded
                continue;

            ++unloadedDependenciesCount;

            if(this.dependentOn[dependency] == undefined)
                this.dependentOn[dependency] = [];

            this.dependentOn[dependency].push(typeIdentifier);
            this.retrieveClass(dependency); // load each dependency
        }

        if(unloadedDependenciesCount == 0)
           this.setupAndRegisterAfterDependenciesComplete(typeIdentifier, setupCallback);
    }
});

var registerClass = function(typeIdentifer, dependencies, setupCallback){
    if(typeof(dependencies) == 'string')
        dependencies = [dependencies];

    g_helioLoader.queueClassRegister(typeIdentifer, dependencies, setupCallback);
}
