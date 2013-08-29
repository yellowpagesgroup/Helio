describe("DynamicLoader", function(){
    var dynamicLoader;

    beforeEach(function(){
        dynamicLoader = new DynamicLoader();
    });

    it("should remove all children of a controller from the controllerRegistry on removeChildrenOfController", function(){
        dynamicLoader.controllerRegistry = {
            'page.document': 'pd.controller',
            'page.document-one': 'pdo-controller',
            'page.document.one': 'pdo.controller',
            'page.document.two': 'pdt.controller'
        };

        dynamicLoader.removeChildrenOfController('page.document');

        expect(dynamicLoader.controllerRegistry['page.document']).toBe('pd.controller');
        expect(dynamicLoader.controllerRegistry['page.document-one']).toBe('pdo-controller');
        expect(dynamicLoader.controllerRegistry['page.document.one']).toBe(undefined);
        expect(dynamicLoader.controllerRegistry['page.document.two']).toBe(undefined);
    });

    it("should immediately call _doAttach on initializeController if the type is undefined, null, or exists in the typeRegistry", function(){
        var mockAttach = spyOn(dynamicLoader, '_doAttach');
        dynamicLoader.initializeController('controller.path', null);
        expect(mockAttach.mostRecentCall.args[0]).toBe('controller.path');
        expect(mockAttach.mostRecentCall.args[1]).toBe(null);

        dynamicLoader.initializeController('controller.path', undefined);
        expect(mockAttach.mostRecentCall.args[0]).toBe('controller.path');
        expect(mockAttach.mostRecentCall.args[1]).toBe(undefined);

        dynamicLoader.typeRegistry['type.identifier'] = 'the.type';
        dynamicLoader.initializeController('controller.path', 'type.identifier');
        expect(mockAttach.mostRecentCall.args[0]).toBe('controller.path');
        expect(mockAttach.mostRecentCall.args[1]).toBe('type.identifier');

        expect(dynamicLoader.attachCallbacks['type.identifier']).toBe(undefined);
    });

    it("should queue a callback to _doAttach with the args given if the type is not yet loaded, then attempt to retrieve the class", function(){
        var loadData = {typeIdentifier: 'type.identifier', controllerPath: 'controller.path'};
        dynamicLoader.retrieveClass = jasmine.createSpy();
        dynamicLoader._doAttach = jasmine.createSpy();
        dynamicLoader.initializeController('controller.path', 'type.identifier');

        expect(dynamicLoader.attachCallbacks['type.identifier'].length).toBe(1);
        expect(dynamicLoader.attachCallbacks['type.identifier'][0].data).toEqual(loadData);
        expect(dynamicLoader.retrieveClass).toHaveBeenCalledWith('type.identifier');
        dynamicLoader.attachCallbacks['type.identifier'][0].callback(loadData);
        expect(dynamicLoader._doAttach).toHaveBeenCalledWith('controller.path', 'type.identifier');
    });

    it("should not call .getScript in retrieveClass, if the class is already queued for load", function(){
        dynamicLoader.pendingSetup['type.identifier'] = true;
        var mockGetScript = spyOn($, 'getScript');
        dynamicLoader.retrieveClass('type.identifier');
        expect(mockGetScript).not.toHaveBeenCalled();
    });

    it("should calls .getScript in retrieveClass, converting the type to a js path", function(){
        var mockGetScript = spyOn($, 'getScript');
        dynamicLoader.retrieveClass('type.identifier');
        expect(mockGetScript).toHaveBeenCalledWith('/mock-static/type/identifier/identifier.js');
    });

    it("should immediately call setupAndRegisterAfterDependenciesComplete on queueClassRegister if dependencies are null or [] or ''", function(){
        var mockSARDC = spyOn(dynamicLoader, 'setupAndRegisterAfterDependenciesComplete');
        dynamicLoader.queueClassRegister('type.one', null, 'callback1');
        dynamicLoader.queueClassRegister('type.two', [], 'callback2');
        dynamicLoader.queueClassRegister('type.three', '', 'callback3');

        expect(mockSARDC).toHaveBeenCalledWith('type.one', 'callback1');
        expect(mockSARDC).toHaveBeenCalledWith('type.two', 'callback2');
        expect(mockSARDC).toHaveBeenCalledWith('type.three', 'callback3');
    });

    it("should register currentRequestDependencies, classLoadCallbacks and dependentOn lists, and retrieve missing classes on queueClassRegister", function(){
        var mockRetriever = spyOn(dynamicLoader, 'retrieveClass');
        var mockSARDC = spyOn(dynamicLoader, 'setupAndRegisterAfterDependenciesComplete');
        dynamicLoader.queueClassRegister('type.one', ['dependency1', 'dependency2'], 'callback');
        expect(dynamicLoader.classLoadCallbacks['type.one'].length).toBe(1);
        expect(dynamicLoader.currentRequestDependencies['type.one']).toEqual(['dependency1', 'dependency2']);
        expect(dynamicLoader.dependentOn['dependency1']).toEqual(['type.one']);
        expect(dynamicLoader.dependentOn['dependency2']).toEqual(['type.one']);
        expect(mockRetriever).toHaveBeenCalledWith('dependency1');
        expect(mockRetriever).toHaveBeenCalledWith('dependency2');
        expect(mockSARDC).not.toHaveBeenCalled();
    });

    it("should call setupAndRegisterAfterDependenciesComplete on queueClassRegister if all dependencies are loaded", function(){
        var mockSARDC = spyOn(dynamicLoader, 'setupAndRegisterAfterDependenciesComplete');
        var mockRetriever = spyOn(dynamicLoader, 'retrieveClass');
        dynamicLoader.typeRegistry = {
            'dependency1': true,
            'dependency2': true
        };

        dynamicLoader.queueClassRegister('type.one', ['dependency1', null, 'dependency2'], 'callback');
        expect(mockSARDC).toHaveBeenCalledWith('type.one', 'callback');
        expect(mockRetriever).not.toHaveBeenCalled();
    });

    it("should (on setupAndRegisterAfterDependenciesComplete) register the class (to typeRegistry) as the result of the setupCallback, then remove the ID from pending setup, and process the load", function(){
        var mockProcessLoadNotification = spyOn(dynamicLoader, 'processLoadNotification');
        dynamicLoader.setupAndRegisterAfterDependenciesComplete('type.identifier', function(){ return 'mockClass'});
        expect(dynamicLoader.pendingSetup['type.identifier']).toBe(undefined);
        expect(dynamicLoader.typeRegistry['type.identifier']).toBe('mockClass');
        expect(mockProcessLoadNotification).toHaveBeenCalledWith('type.identifier');
    });

    it("should (on processLoadNotification) call each classLoadCallbacks for the type, call each attachCallbacks for the type, and notify all dependent components", function(){
        var mockCLC = jasmine.createSpy();
        var mockAC = jasmine.createSpy();

        var classLoadCallback = {
            'data': 'mockData',
            'callback': mockCLC
        };

        var attachCallback = {
            'data': 'mockData',
            'callback': mockAC
        };

        var dependentOn = {
            'type.identifier': ['dependent.class']
        };

        var currentRequestDependencies = {
            'dependent.class': ['type.identifier']
        };

        var processLoadNotification = spyOn(dynamicLoader, 'processLoadNotification').andCallThrough();

        dynamicLoader.classLoadCallbacks = {'type.identifier': [classLoadCallback]};
        dynamicLoader.attachCallbacks = {'type.identifier': [attachCallback]};
        dynamicLoader.dependentOn = dependentOn;
        dynamicLoader.currentRequestDependencies = currentRequestDependencies;

        dynamicLoader.processLoadNotification('type.identifier');

        expect(mockCLC).toHaveBeenCalled();
        expect(mockAC).toHaveBeenCalled();
        expect(dynamicLoader.classLoadCallbacks['type.identifier']).toBe(undefined);
        expect(dynamicLoader.attachCallbacks['type.identifier']).toBe(undefined);
        expect(dynamicLoader.dependentOn['type.identifier']).toBe(undefined);
        expect(dynamicLoader.currentRequestDependencies['dependent.class']).toBe(undefined);
        expect(processLoadNotification).toHaveBeenCalledWith('dependent.class');
    });

    it("should (on processLoadNotification) not call processLoadNotification if currentRequestDependencies is not empty for the dependent class", function(){
         var dependentOn = {
            'type.identifier': ['dependent.class', 'single.dependent.class']
        };

        var currentRequestDependencies = {
            'dependent.class': ['type.identifier', 'another.class'],
            'single.dependent.class': ['type.identifier']
        };

        var processLoadNotification = spyOn(dynamicLoader, 'processLoadNotification').andCallThrough();

        dynamicLoader.dependentOn = dependentOn;
        dynamicLoader.currentRequestDependencies = currentRequestDependencies;
        dynamicLoader.processLoadNotification('type.identifier');

        expect(processLoadNotification).toHaveBeenCalledWith('single.dependent.class');
        expect(processLoadNotification).not.toHaveBeenCalledWith('dependent.class');
    });

    it("should instantiate a new controller from the class retrieved from the type registry", function(){
        var mockClassOne = jasmine.createSpy().andReturn({
            attach: jasmine.createSpy()
        });
        var mockClassTwo = jasmine.createSpy().andReturn({
            attach: jasmine.createSpy()
        });

        dynamicLoader.typeRegistry = {
            'class.one': mockClassOne,
            'class.two': mockClassTwo
        };

        dynamicLoader._doAttach('controller.path.one', 'class.one');
        dynamicLoader._doAttach('controller.path.two', 'class.two');

        expect(mockClassOne).toHaveBeenCalledWith('controller.path.one');
        expect(mockClassTwo).toHaveBeenCalledWith('controller.path.two');
    });

    it("should create a new Controller on _doAttach if typeIdentifier is null", function(){
        var mockAttach = jasmine.createSpy();
        var mockController = spyOn(window, 'Controller').andReturn({
            attach: mockAttach
        });

        dynamicLoader._doAttach('controller.path', null);
        expect(mockAttach).toHaveBeenCalled();
        expect(mockController).toHaveBeenCalledWith('controller.path');
    });

    it("should use the view_state_path setting to get the view state ID, otherwise use 'get-view-state", function(){
        window.g_helioSettings = {};
        var mockGet = spyOn($, 'get');

        dynamicLoader.getViewState();
        expect(mockGet).toHaveBeenCalledWith('/get-view-state/?vs_id=-1', jasmine.any(Function));

        window.g_helioSettings['view_state_path'] = '?mock-vs-url';
        window.g_helioSettings['viewstate_id'] = '2'
        dynamicLoader.getViewState();
        expect(mockGet).toHaveBeenCalledWith('?mock-vs-url&vs_id=2', jasmine.any(Function));
    });
});

describe("registerClass", function(){
    beforeEach(function(){
        window.g_helioLoader = {
            queueClassRegister: function(){}
        };
    });

    it("should call the loader's queueClassRegister ", function(){
        var mockQCR = spyOn(g_helioLoader, 'queueClassRegister');
        registerClass('type.identifier', ['list', 'of', 'dependencies'], 'callback');
        expect(mockQCR).toHaveBeenCalledWith('type.identifier', ['list', 'of', 'dependencies'], 'callback');
    });

    it("should convert a single dependency into an array, for consistency", function(){
        var mockQCR = spyOn(g_helioLoader, 'queueClassRegister');
        registerClass('type.identifier', 'singledependency', 'callback');
        expect(mockQCR).toHaveBeenCalledWith('type.identifier', ['singledependency'], 'callback');
    });

    it("should not convert a null dependency to an array", function(){
        var mockQCR = spyOn(g_helioLoader, 'queueClassRegister');
        registerClass('type.identifier', null, 'callback');
        expect(mockQCR).toHaveBeenCalledWith('type.identifier', null, 'callback');
    });
});

describe("setViewStateID", function(){
    it("should set view state ID into the Helio settings and the session storage", function(){
        window.g_helioSettings = {};

        setViewStateID('mock-vs-id');
        expect(window.g_helioSettings['viewstate_id']).toBe('mock-vs-id');
        expect(sessionStorage.helioViewStateID).toBe('mock-vs-id');
    });
});