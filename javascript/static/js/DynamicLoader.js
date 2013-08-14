var DynamicLoader = klass(function(){
    this.componentRegistry = {};
    this.componentLoadCallbacks = {};
    this.currentRequestDependencies = {};
    this.dependentOn = {};
    this.pendingSetup = {};
    this.attachCallbacks = {};
}).methods({

});