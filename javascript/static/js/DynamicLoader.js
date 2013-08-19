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
    setupAndRegisterAfterDependenciesComplete: function(typeIdentifier, setupCallback){

    },
    queueClassRegister: function(typeIdentifier, dependencies, setupCallback){
         if(dependencies == null || dependencies.length == 0) {
            this.setupAndRegisterAfterDependenciesComplete(typeIdentifier, setupCallback);
            return;
        } else {
            this.currentRequestDependencies[typeIdentifier] = dependencies;

            if(this.componentLoadCallbacks[componentClassID] == undefined)
                this.componentLoadCallbacks[componentClassID] = [];

            this.componentLoadCallbacks[componentClassID].push(
                {
                callback: function(){ // after the component is loaded, call its setup and push it into global namespace
                   _parent.componentRegistry[componentClassID] = setupFunction();
                   g_classRegistry[componentClassID] = _parent.componentRegistry[componentClassID];

                    delete _parent.pendingSetup[componentClassID];
                },
                data: null
                }
            );
        }

        var _parent = this;
        var unloadedDependenciesCount = 0;

        $.each(dependencies, function(index, value){
            if(value == null || _parent.componentRegistry[value] != undefined) // dependency already loaded
                return;

            ++unloadedDependenciesCount;

            if(_parent.dependentOn[value] == undefined)
                _parent.dependentOn[value] = [];

            _parent.dependentOn[value].push(componentClassID);

            _parent.retrieveComponent(value); // load each dependency
        });

        if(unloadedDependenciesCount == 0) {
           this.setupAndRegisterAfterDependenciesComplete(componentClassID, setupFunction);
           return;
        }
    }
});

var registerClass = function(typeIdentifer, dependencies, setupCallback){
    if(typeof(dependencies) == 'string')
        dependencies = [dependencies];

    g_helioLoader.queueClassRegister(typeIdentifer, dependencies, setupCallback);
}
