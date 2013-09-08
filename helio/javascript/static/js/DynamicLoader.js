var DynamicLoader = klass(function(){
    this.controllerRegistry = {}; // map the controller path to the current instance
    this.classLoadCallbacks = {};
    this.currentRequestDependencies = {};
    this.dependentOn = {};
    this.pendingSetup = {};
    this.attachCallbacks = {};
    this.typeRegistry = {}; // map controller type name to js class
    this.controllerTypeNameRegistry = {}; // map controller path to class name
    this.postViewStateSetup = null // call this after the viewstate ID is retrieved
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
         // get the class from its identifier, then initialise, attach and store a reference to it
        // this is only called after the JS component for the particular class is available.
        if(typeIdentifier == null)
            var componentClass = Controller;
        else
            var componentClass = this.typeRegistry[typeIdentifier];

        this.controllerTypeNameRegistry = typeIdentifier;
        var classInstance = new componentClass(controllerPath);
        classInstance.attach();
        this.controllerRegistry[controllerPath] = classInstance;
    },
    processLoadNotification: function(typeIdentifier){
        var _this = this;

        if(this.classLoadCallbacks[typeIdentifier] != undefined) {
            $.each(this.classLoadCallbacks[typeIdentifier], function(index, value){
                value.callback(value.data); // load the component, usually  by calling function to create class and put in global namespace
            });

            delete this.classLoadCallbacks[typeIdentifier];
        }

        if(this.attachCallbacks[typeIdentifier] != undefined) {
            $.each(this.attachCallbacks[typeIdentifier], function(index, value){
                value.callback(value.data); // after the component is loaded, we can attach it to the dom
            });

            delete this.attachCallbacks[typeIdentifier];
        }

        if(this.dependentOn[typeIdentifier]){
            $.each(this.dependentOn[typeIdentifier], function(index, value){ // for each of the classes that are dependent on it, let them know it's finished
                _this.currentRequestDependencies[value] = $.grep(_this.currentRequestDependencies[value], function(innerValue, innerIndex){
                    return innerValue != typeIdentifier; // remove the class that has just been loaded from the list of dependencies
                });

                if(_this.currentRequestDependencies[value] != undefined && _this.currentRequestDependencies[value].length == 0){
                    _this.processLoadNotification(value); // if the class now has no dependencies it can be loaded
                    delete _this.currentRequestDependencies[value];
                }
            });

            delete this.dependentOn[typeIdentifier];
        }
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
    },
    getViewState: function(){
        var viewStatePath = g_helioSettings.view_state_path || '/get-view-state/';
        var currentVSID = (g_helioSettings.viewstate_id == undefined || g_helioSettings.viewstate_id == null) ? '-1' : g_helioSettings.viewstate_id;
        var viewStateURL = viewStatePath + (viewStatePath.indexOf('?') >= 0 ? '&' : '?') + 'vs_id=' + currentVSID;

        var _this = this;
        $.get(viewStateURL, function(data){
            setViewStateID(data);
            if(_this.postViewStateSetup)
                _this.postViewStateSetup();
        });
    }
});

var setViewStateID = function(viewStateID){
    g_helioSettings.viewstate_id = viewStateID;
    if(typeof(sessionStorage)!=="undefined"){
        sessionStorage.setItem('helioViewStateID', viewStateID);
    }
}

var registerClass = function(typeIdentifer, dependencies, setupCallback){
    if(typeof(dependencies) == 'string')
        dependencies = [dependencies];

    g_helioLoader.queueClassRegister(typeIdentifer, dependencies, setupCallback);
}

