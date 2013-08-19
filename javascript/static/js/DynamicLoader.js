var DynamicLoader = klass(function(){
    this.controllerRegistry = {}; // map the controller path to the current instance
    this.controllerLoadCallbacks = {};
    this.currentRequestDependencies = {};
    this.dependentOn = {};
    this.pendingSetup = {};
    this.attachCallbacks = {};
    this.controllerTypeRegistry = {}; // map controller path to class
    this.controllerTypeNameRegistry = {}; // map controller path to class name
}).methods({
    initializeController: function(controllerPath, typeIdentifier){

    },
    removeChildrenOfController: function(rootControllerPath){
        var _this = this;
         $.each(this.controllerRegistry, function(componentPath, controllerInstance){
            if(componentPath.indexOf(rootControllerPath + '.') === 0 && rootControllerPath != componentPath)
                delete _this.controllerRegistry[componentPath];
        });
    }
});