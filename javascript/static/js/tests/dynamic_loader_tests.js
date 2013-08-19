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
    })
});