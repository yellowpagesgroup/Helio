from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^controller/(?P<controller_path>[\w\.:\d]+)/?$', 'helio.heliodjango.views.helio_get_controller_data'),
    url(r'^notification/(?P<controller_path>[\w\.:\d]+)/(?P<notification_name>[\w\.\-]+)/?$',
        'helio.heliodjango.views.helio_dispatch_notification'),
    url(r'^get-view-state/?$', 'helio.heliodjango.views.helio_get_view_state')
)