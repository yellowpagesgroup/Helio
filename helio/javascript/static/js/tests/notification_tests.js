describe("NotifcationCentre helpers", function(){
    it("buildNotificationURL should use /notification/<path>/<type> as the default format", function(){
        window.g_helioSettings = {};
        expect(buildNotificationURL('the.path', 'thetype')).toBe('/notification/the.path/thetype');
    });

    it("buildNotificationURL should use g_helioSettings.notification_base if set", function(){
        window.g_helioSettings = {'notification_base': '/mock-notification/'};
        expect(buildNotificationURL('the.path', 'thetype')).toBe('/mock-notification/the.path/thetype');
    });

    it("buildNotificationURL should use g_helioSettings.notification_url_builder function if set", function(){
        var mockNotificationURLBuilder = jasmine.createSpy();
        window.g_helioSettings = {'notification_url_builder': mockNotificationURLBuilder};
        buildNotificationURL('the.path', 'thetype');
        expect(mockNotificationURLBuilder).toHaveBeenCalledWith('the.path', 'thetype');
    });

    it("postNotification shortcut should call postNotification on the shared notificationCentre (g_helioNotificationCentre)", function(){
        window.g_helioNotificationCentre = {
            postNotification: jasmine.createSpy()
        };

        postNotification('targetPath', 'notificationName', 'notificationData', 'force', 'uncritical');
        expect(window.g_helioNotificationCentre.postNotification).toHaveBeenCalledWith('targetPath', 'notificationName', 'notificationData', 'force', 'uncritical');
    });
});

describe("NotificationCentre", function(){
    var notificationCentre, mockURLGEN, mockPost;

    beforeEach(function(){
        notificationCentre = new NotificationCentre();
        mockURLGEN = spyOn(window, 'buildNotificationURL').andReturn('mock-url');

        mockPost = spyOn($, 'post').andReturn({
            fail: jasmine.createSpy()
        });
    });

    it("should drop the notification if one is already in progress, unless forced", function(){
        notificationCentre.notificationActive = true;
        notificationCentre.postNotification('path', 'name', 'data');
        expect(mockURLGEN).not.toHaveBeenCalled();
        expect(mockPost).not.toHaveBeenCalled();
        notificationCentre.postNotification('path', 'name', 'data', true);
        expect(mockURLGEN).toHaveBeenCalledWith('path', 'name');
        expect(mockPost).toHaveBeenCalledWith('mock-url', 'data', jasmine.any(Function), 'json');
        mockURLGEN.reset();
        mockPost.reset();

        notificationCentre.notificationActive = false;
        notificationCentre.postActive = true;
        notificationCentre.postNotification('path', 'name', 'data');
        expect(mockURLGEN).not.toHaveBeenCalled();
        expect(mockPost).not.toHaveBeenCalled();
        notificationCentre.postNotification('path', 'name', 'data', true);
        expect(mockURLGEN).toHaveBeenCalledWith('path', 'name');
        expect(mockPost).toHaveBeenCalledWith('mock-url', 'data', jasmine.any(Function), 'json');
    });

    it("should not call activityStatusChanged on uncritical calls", function(){
        var mockASC = spyOn(notificationCentre, 'activityStatusChanged');
        notificationCentre.postNotification('path', 'name', 'data', null, true);
        expect(mockASC).not.toHaveBeenCalled();
    });

    it("should set postActive to false and update activity status on failure", function(){
        notificationCentre.postActive = true;
        var mockASC = spyOn(notificationCentre, 'activityStatusChanged');
        notificationCentre.notificationPostFailure();
        expect(mockASC).toHaveBeenCalled();
        expect(notificationCentre.postActive).toBe(false);
    });

    it("should set the window location to / on a refresh notification (can't test) and not delegate anything", function(){
        var mockDelegator = spyOn(notificationCentre, 'queueNotificationDelegation');
        notificationCentre.notificationPostCallback('refresh');
        expect(mockDelegator).not.toHaveBeenCalled();
    });

    it("should queue every notification for delegation, set postActive to false then call activityStatusChanged and processQueue", function(){
        notificationCentre.postActive = true;

        var mockQND = spyOn(notificationCentre, 'queueNotificationDelegation');
        var mockASC = spyOn(notificationCentre, 'activityStatusChanged');
        var mockProcessQueue = spyOn(notificationCentre, 'processQueue');

        notificationCentre.notificationPostCallback(['one', 'two', 'three']);
        expect(mockQND).toHaveBeenCalledWith('one');
        expect(mockQND).toHaveBeenCalledWith('two');
        expect(mockQND).toHaveBeenCalledWith('three');
        expect(mockASC).toHaveBeenCalled();
        expect(mockProcessQueue).toHaveBeenCalled();
        expect(notificationCentre.postActive).toBe(false);
    });

    it("should call the activity display update functions on activityStatusChanged", function(){
        var mockActivateFunction = jasmine.createSpy();
        var mockDeactivateFunction = jasmine.createSpy();

        window.g_helioSettings = {
            activity_activate_callback: mockActivateFunction,
            activity_deactivate_callback: mockDeactivateFunction
        };

        notificationCentre.notificationActive = false;
        notificationCentre.postActive = false;
        notificationCentre.activityStatusChanged();
        expect(mockActivateFunction).not.toHaveBeenCalled();
        expect(mockDeactivateFunction).toHaveBeenCalled();
        mockDeactivateFunction.reset();

        notificationCentre.notificationActive = true;
        notificationCentre.postActive = false;
        notificationCentre.activityStatusChanged();
        expect(mockActivateFunction).toHaveBeenCalled();
        expect(mockDeactivateFunction).not.toHaveBeenCalled();
        mockActivateFunction.reset();

        notificationCentre.notificationActive = false;
        notificationCentre.postActive = true;
        notificationCentre.activityStatusChanged();
        expect(mockActivateFunction).toHaveBeenCalled();
        expect(mockDeactivateFunction).not.toHaveBeenCalled();
        mockActivateFunction.reset();
    });

    it("should push the provided notification onto the notifications queue on every queueNotificationDelegation call", function(){
        notificationCentre.queueNotificationDelegation('notification1');
        expect(notificationCentre.notifications).toEqual(['notification1']);

        notificationCentre.queueNotificationDelegation('notification2');
        expect(notificationCentre.notifications).toEqual(['notification1', 'notification2']);

        notificationCentre.queueNotificationDelegation('notification3');
        expect(notificationCentre.notifications).toEqual(['notification1', 'notification2', 'notification3']);
    });

    it("should (on processQueue) scroll to the top of the page when all notifications are finished and scrollTopOnFinish is true, then scrollTopOnFinish should be false", function(){
        var mockASC = spyOn(notificationCentre, 'activityStatusChanged');
        var mockScrollTo = spyOn(window, 'scrollTo');
        notificationCentre.scrollTopOnFinish = true;
        notificationCentre.processQueue();

        expect(mockASC).toHaveBeenCalled();
        expect(mockScrollTo).toHaveBeenCalledWith(0, 0);
        expect(notificationCentre.scrollTopOnFinish).toBe(false);
    });

    it("should (on processQueue) delegate a notification with delegateNotification, then notifications should be one smaller", function(){
        var mockASC = spyOn(notificationCentre, 'activityStatusChanged');
        var mockNotificationDelegate = spyOn(notificationCentre, 'delegateNotification');
        notificationCentre.notifications = [
            {'target': 'path1', 'name': 'name1', 'data': 'data1'},
            {'target': 'path2', 'name': 'name2', 'data': 'data2'}
        ];

        notificationCentre.processQueue();
        expect(mockASC).toHaveBeenCalled();
        expect(notificationCentre.notifications.length).toBe(1);
        expect(mockNotificationDelegate.mostRecentCall.args).toEqual(['path1', 'name1', 'data1']);
        notificationCentre.notificationActive = false;
        notificationCentre.processQueue();
        expect(mockNotificationDelegate.mostRecentCall.args).toEqual(['path2', 'name2', 'data2']);
        expect(notificationCentre.notifications.length).toBe(0);
    });

    it("should (on processQueue) return without delegating any notifications (the length should stay the same) if notificationActive is true", function(){
        var mockASC = spyOn(notificationCentre, 'activityStatusChanged');
        var mockNotificationDelegate = spyOn(notificationCentre, 'delegateNotification');
        notificationCentre.notifications = [
            {'target': 'path1', 'name': 'name1', 'data': 'data1'}
        ];
        notificationCentre.notificationActive = true;
        notificationCentre.processQueue();
        expect(mockASC).toHaveBeenCalled();
        expect(mockNotificationDelegate).not.toHaveBeenCalled();
    });

    it("should (on delegateNotification) update the viewstate_id on update-vs-id, then call notificationComplete", function(){
        window.g_helioSettings = {
            'viewstate_id': 'unset'
        };

        var mockNotificationComplete = spyOn(notificationCentre, 'notificationComplete');

        notificationCentre.delegateNotification('', 'update-vs-id', 'new-vs-id');
        expect(window.g_helioSettings.viewstate_id).toBe('new-vs-id');
        expect(mockNotificationComplete).toHaveBeenCalled();
    });

    it("should (on delegateNotification) update window.location (not testable) on change-url, and then return", function(){
        spyOn(window, 'location');
        var mockNotificationComplete = spyOn(notificationCentre, 'notificationComplete');

        notificationCentre.delegateNotification('', 'change-url', 'http://www.example.com');
        expect(mockNotificationComplete).not.toHaveBeenCalled();
    });

    it("should (on delegateNotification) call notificationComplete immediately if no controller is registered at the path", function(){
        window.g_helioLoader = {
            'controllerRegistry': {}
        };

        var mockNotificationComplete = spyOn(notificationCentre, 'notificationComplete');

        notificationCentre.delegateNotification('controller.one', 'name1', 'data1');
        expect(mockNotificationComplete).toHaveBeenCalled();
    });

    it("should (on delegateNotification) call processNotification on the found controller", function(){
        var processorOne = jasmine.createSpy();
        var processorTwo = jasmine.createSpy();

        window.g_helioLoader = {
            'controllerRegistry': {
                'controller.one': {
                    'processNotification': processorOne
                },
                'controller.two': {
                    'processNotification': processorTwo
                }
            }
        };
        var mockNotificationComplete = spyOn(notificationCentre, 'notificationComplete');

        notificationCentre.delegateNotification('controller.one', 'name1', 'data1');
        expect(mockNotificationComplete).toHaveBeenCalled();
        mockNotificationComplete.reset();

        notificationCentre.delegateNotification('controller.two', 'name2', 'data2');
        expect(mockNotificationComplete).toHaveBeenCalled();

        expect(processorOne).toHaveBeenCalledWith('name1', 'data1');
        expect(processorTwo).toHaveBeenCalledWith('name2', 'data2');
    });

    it("should set notificationActive to false, and call processQueue, on notificationComplete", function(){
        var mockProcessQueue = spyOn(notificationCentre, 'processQueue');
        notificationCentre.notificationActive = true;
        notificationCentre.notificationComplete();
        expect(notificationCentre.notificationActive).toBe(false);
        expect(mockProcessQueue).toHaveBeenCalled();
    });
});