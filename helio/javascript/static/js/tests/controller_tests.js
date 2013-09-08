describe("Controller helpers", function(){
   it("should escape .s and :s in selectors", function(){
        expect(escapeSelector('selector.with.dots:and.colons')).toBe('selector\\.with\\.dots\\:and\\.colons');
   });

   it("controllerDepthSorter should sort the controller by path depth", function(){
       var unsorted = [
           {'path': 'one.two.three', 'depth': 2},
           {'path': 'one.two.three.four.five.six', 'depth': 5},
           {'path': 'one.two.three.four.five', 'depth': 4},
           {'path': 'one.two', 'depth': 1},
           {'path': 'one.two.three.four', 'depth': 3},
           {'path': 'one', 'depth': 0}
       ];

       var sorted = unsorted.sort(controllerDepthSorter);
       expect(sorted[0].path).toBe('one');
       expect(sorted[1].path).toBe('one.two');
       expect(sorted[2].path).toBe('one.two.three');
       expect(sorted[3].path).toBe('one.two.three.four');
       expect(sorted[4].path).toBe('one.two.three.four.five');
       expect(sorted[5].path).toBe('one.two.three.four.five.six');
   });

    it("controllerClassMapTransform should process the class map into an array objects with the path, depth and assets", function(){
        var classMap = {
            'page.one': ['asset_one', 'asset_two'],
            'page.one.two': ['asset_three']
        };

        var transformedClassMap = controllerClassMapTransform(classMap);

        expect(transformedClassMap[0]).toEqual({'depth': 1, 'path': 'page.one', 'assets': ['asset_one', 'asset_two']});
        expect(transformedClassMap[1]).toEqual({'depth': 2, 'path': 'page.one.two', 'assets': ['asset_three']});
    });

    it("componentNameToAssetPath should transform a component name and extension to a path string", function(){
       expect(componentNameToAssetPath('a.component.name', 'css')).toBe('a/component/name/name.css');
    });

    it("attachCSS should attach a <link> element to the head with the CSS path and controller path", function(){
        window.g_helioSettings = {
            controller_url_base: '/mock/controller/',
            viewstate_id: 'viewstate_id',
            static_base: '/mock-static/'

        };

        var mockJQResult = {
            append: jasmine.createSpy()
        };

        var mockJQ = spyOn(window, '$').andReturn(mockJQResult);
        var mockAssetPathGen = spyOn(window, 'componentNameToAssetPath').andReturn('mock-assetpath');
        attachCSS('the.controller.path', 'mock-asset');
        expect(mockAssetPathGen).toHaveBeenCalledWith('mock-asset', 'css');
        expect(mockJQ).toHaveBeenCalledWith('head');
        expect(mockJQResult.append).toHaveBeenCalledWith('<link rel="stylesheet" type="text/css" href="/mock-static/mock-assetpath" id="css_the.controller.path">');
    });

    it("cssIsAttached should escape the selector before using it in the query", function(){
        var controllerPath = 'this.is.my.path';
        var mockJQ = spyOn(window, '$');
        mockJQ.andReturn([]);
        var mockSelectorEscaper = spyOn(window, 'escapeSelector').andCallThrough();
        expect(cssIsAttached(controllerPath)).toBe(false);
        expect(mockSelectorEscaper).toHaveBeenCalledWith(controllerPath);
        expect(mockJQ).toHaveBeenCalledWith('#css_this\\.is\\.my\\.path');

        mockJQ.andReturn(['result']);
        expect(cssIsAttached(controllerPath)).toBe(true);
    });

    it("detachCSS should locate the css <link> and remove it, escaping the selector first", function(){
        var mockJQResult = {
            remove: jasmine.createSpy()
        };
        var mockPath = 'this.is.my.path';
        var mockJQ = spyOn(window, '$').andReturn(mockJQResult);
        var mockSelectorEscape = spyOn(window, 'escapeSelector').andReturn('mock-selector');
        detachCSS(mockPath);
        expect(mockSelectorEscape).toHaveBeenCalledWith(mockPath);
        expect(mockJQ).toHaveBeenCalledWith('#css_mock-selector');
        expect(mockJQResult.remove).toHaveBeenCalled();
    });
});

describe("Controller", function() {
    var testController;
    beforeEach(function(){
        window.g_helioSettings = {
            controller_url_base: '/mock/controller/',
            viewstate_id: 'viewstate_id',
            static_base: '/mock-static/'

        };
        testController = new Controller('this.is.my.path', 'my_selector', {'extra_data': 'somedata'});
    });

    it("should set its path, selector and extra data on initialisation", function() {
        expect(testController.controllerPath).toBe('this.is.my.path');
        expect(testController.containerSelector).toBe('my_selector');
        expect(testController.extraData).toEqual({'extra_data': 'somedata'});
    });

    it("should call escapeSelector on setSelector", function(){
        var mockEscapeSelector = spyOn(window, 'escapeSelector');
        testController.setSelector('selector.with.dots:and.colons');
        expect(mockEscapeSelector).toHaveBeenCalledWith('selector.with.dots:and.colons');
    });

    it("should use the controller path as the selector (with id #) if no selector is defined", function(){
        testController = new Controller('controller.the.path');
        expect(testController.containerSelector).toBe('#controller\\.the\\.path');
    });

    it("should locate its container in the DOM and save the reference to its $container attribute", function(){
        var mockJQ = spyOn(window, '$').andReturn('mock-container-element');
        testController = new Controller('page.document.childone');
        expect(mockJQ).toHaveBeenCalledWith('#page\\.document\\.childone');
        expect(testController.$container).toBe('mock-container-element');
    });

    it("should build its data retrieval URL based on the controller path and viewstate_id", function(){
        expect(testController.buildURL()).toBe('/mock/controller/this.is.my.path?vs_id=viewstate_id');
    });

    it("should properly append the viewstate ID if the url already has a query string", function(){
        window.g_helioSettings.controller_url_base = '/controller?path=';
        expect(testController.buildURL()).toBe('/controller?path=this.is.my.path&vs_id=viewstate_id');
    });

    it("should not append a viewstate ID if the settings viewstate_id is not set", function(){
        delete window.g_helioSettings.viewstate_id;
        expect(testController.buildURL()).toBe('/mock/controller/this.is.my.path');
    });

    it("should default the URL base to /controller/", function(){
        delete window.g_helioSettings.controller_url_base;
        expect(testController.buildURL()).toBe('/controller/this.is.my.path?vs_id=viewstate_id');
    });

    it("should should immediately call the load callback if a data arg is given", function(){
        var mockLoadCallback = spyOn(testController, 'loadCallback');
        testController.load('mock-data');
        expect(mockLoadCallback).toHaveBeenCalledWith('mock-data');
    });

    it("should set the controller's container 'attached' data to false before loading", function(){
        var mock$Container = {
            data: jasmine.createSpy()
        };

        spyOn($, 'get'); // don't actually call get
        testController.$container = mock$Container;
        testController.load();
        expect(mock$Container.data).toHaveBeenCalledWith('attached', false);
    });

    it("should call get with the component URL and 'json' (type) arg", function(){
        var mockGet = spyOn($, 'get');

        testController.load();
        expect(mockGet.mostRecentCall.args[0]).toBe(testController.buildURL());
        expect(mockGet.mostRecentCall.args[1]).toEqual(jasmine.any(Function));
        expect(mockGet.mostRecentCall.args[2]).toBe('json');
    });

    it("setContent should use the .html() method to set the container content", function(){
        var mock$Container = {
            html: jasmine.createSpy()
        }

        testController.$container = mock$Container;
        testController.setContent('mock-content');
        expect(mock$Container.html).toHaveBeenCalledWith('mock-content');
    });

    it("should call removeChildrenOfController on the DynamicLoader with the new controller path on loadCallback", function(){
        window.g_helioLoader = {
            removeChildrenOfController: jasmine.createSpy()
        };

        testController.loadCallback({'class_map': {}});
        expect(window.g_helioLoader.removeChildrenOfController).toHaveBeenCalledWith('this.is.my.path');
    });

    it("should process the class map through controllerClassMapTransform", function(){
        window.g_helioLoader = {
            controllerTypeNameRegistry: {},
            controllerRegistry: {},
            removeChildrenOfController: jasmine.createSpy()
        }
        var mockCCMT = spyOn(window, 'controllerClassMapTransform').andCallThrough();
        var classMap = {'page.one': ['assets']};
        testController.loadCallback({'class_map': classMap});
        expect(mockCCMT).toHaveBeenCalledWith(classMap);
    });

    it("should call its _setupController method for each controller", function(){
        var classMap = {'page': {}, 'page.two': {'script': 'js.component', 'css': 'the.css'}};
        testController._setupController = jasmine.createSpy();
        testController.loadCallback({'class_map': classMap});
        expect(testController._setupController.calls[0].args[0]).toEqual({ depth: 0, path: 'page', assets: {}});
        expect(testController._setupController.calls[1].args[0]).toEqual({ depth: 1, path: 'page.two', assets: {script: 'js.component', css: 'the.css'}});
    });

    it("_setupController should set controllerTypeNameRegistry to undefined for an undefined class, and controllerRegistry should be a Controller instance", function(){
         window.g_helioLoader = {
            controllerTypeNameRegistry: {},
            controllerRegistry: {}
        };
        testController._setupController({path: 'page', assets: {}});
        expect(window.g_helioLoader.controllerTypeNameRegistry['page']).toBe(undefined);
        expect(window.g_helioLoader.controllerRegistry['page']).toEqual(jasmine.any(Controller));
    });

    it("_setupController should call isAttached() and then attach() on a controller if the typeName matches the new version", function(){
        var mockAttached = {
            isAttached: jasmine.createSpy().andCallFake(function(){return true}),
            attach: jasmine.createSpy()
        };

        var mockNotAttached = {
            isAttached: jasmine.createSpy().andCallFake(function(){return false}),
            attach: jasmine.createSpy()
        };

         window.g_helioLoader = {
            controllerTypeNameRegistry: {'attached': 'attached', 'unattached': 'unattached'},
            controllerRegistry: {
                'attached': mockAttached,
                'unattached': mockNotAttached
            }
        };

        testController._setupController({path: 'attached', assets: {'script': 'attached'}});
        expect(mockAttached.isAttached).toHaveBeenCalled();
        expect(mockAttached.attach).not.toHaveBeenCalled();

        testController._setupController({path: 'unattached', assets: {'script': 'unattached'}});
        expect(mockNotAttached.isAttached).toHaveBeenCalled();
        expect(mockNotAttached.attach).toHaveBeenCalled();

    });

    it("should attach css if CSS is defined and CSS is not already attached", function(){
        var mockNoCSS = {
            isAttached: jasmine.createSpy().andCallFake(function(){return true})
        };

        var mockCSSAttached = {
            isAttached: jasmine.createSpy().andCallFake(function(){return true})
        };

        var mockCSSNotAttached = {
            isAttached: jasmine.createSpy().andCallFake(function(){return true})
        };

        window.g_helioLoader = {
            controllerTypeNameRegistry: {'noCSS': 'noCSS', 'attachedCSS': 'attachedCSS', 'detachedCSS': 'detachedCSS'},
            controllerRegistry: {
                'noCSS': mockNoCSS,
                'attachedCSS': mockCSSAttached,
                'detachedCSS': mockCSSNotAttached
            }
        };

        window.cssIsAttached = jasmine.createSpy();
        window.attachCSS = jasmine.createSpy();
        testController._setupController({path: 'noCSS', assets: {'script': 'noCSS'}});
        expect(window.cssIsAttached).not.toHaveBeenCalled();
        expect(window.attachCSS).not.toHaveBeenCalled();

        window.cssIsAttached = jasmine.createSpy().andCallFake(function(){return true});
        window.attachCSS = jasmine.createSpy();
        testController._setupController({path: 'attachedCSS', assets: {'script': 'attachedCSS', 'css': 'attachedCSS'}});
        expect(window.cssIsAttached).toHaveBeenCalled();
        expect(window.attachCSS).not.toHaveBeenCalled();

        window.cssIsAttached = jasmine.createSpy().andCallFake(function(){return false});
        window.attachCSS = jasmine.createSpy();
        testController._setupController({path: 'detachedCSS', assets: {'script': 'detachedCSS', 'css': 'detachedCSS'}});
        expect(window.cssIsAttached).toHaveBeenCalled();
        expect(window.attachCSS).toHaveBeenCalled();
    });

    it("should call the dynamicLoader attachClass if the controller type has changed", function(){
        window.g_helioLoader = {
            controllerTypeNameRegistry: {'page': 'page'},
            controllerRegistry: {},
            initializeController: jasmine.createSpy()
        };

        testController._setupController({path: 'not-page', assets: {'script': 'new-script'}});

        expect(window.g_helioLoader.initializeController).toHaveBeenCalledWith('not-page', 'new-script');
    });

    it("should call its load() method on a load notification", function(){
        testController.load = jasmine.createSpy();
        testController.processNotification('load', {'some': 'data'});
        expect(testController.load).toHaveBeenCalledWith({'some': 'data'});
    });

    it("should set the notificationCentre.scrollTopOnFinish to true if there is a scroll_top arg", function(){
        window.g_helioNotificationCentre = {};
        testController.processNotification('fake-call:scroll_top');
        expect(window.g_helioNotificationCentre.scrollTopOnFinish).toBe(true);
    });

    it("should call its $container data() method to set attached data to true or false on attach and detach, respectively", function(){
        var mock$Container = {
            data: jasmine.createSpy()
        };

        testController.$container = mock$Container;
        testController.attach();
        expect(mock$Container.data.mostRecentCall.args[0]).toBe('attached');
        expect(mock$Container.data.mostRecentCall.args[1]).toBe(true);
        testController.detach();
        expect(mock$Container.data.mostRecentCall.args[0]).toBe('attached');
        expect(mock$Container.data.mostRecentCall.args[1]).toBe(false);
    });
});