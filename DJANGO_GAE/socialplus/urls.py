from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^get_cookie$', 'socialplus.views.get_cookie'),
    # OTHER STUFF..
    url(r'^test/(?P<test_name>[^/]+)$', 'socialplus.tests.run_test'),
    url(r'^delete_all/reports$', 'socialplus.views.delete_reports'),
    url(r'^delete_all/people$', 'socialplus.views.delete_people'),
    url(r'^delete_all/users$', 'socialplus.views.delete_users'),
    url(r'^delete_all/activities$', 'socialplus.views.delete_activities'),
    url(r'^delete_all/tasks$', 'socialplus.views.delete_tasks'),
    url(r'^delete_all/activities_search_index$', 'socialplus.views.delete_activities_search_index'),
    url(r'^reset_domain$', 'socialplus.views.reset_domain'),
    url(r'^start_task/(?P<id_>[^/]+)$', 'socialplus.views.start_task'),
    url(r'^login$', 'socialplus.views.login'),
    url(r'^logout$', 'socialplus.views.logout'),
    # ACTIVITY
    url(r'^activities', 'socialplus.views.search_activities'),
    # PERSON
    url(r'^people/(?P<id_>[^/]+)$', 'socialplus.views.get_person'),
    url(r'^people$', 'socialplus.views.get_people'),
    # COMMUNITY
    url(r'^communities$', 'socialplus.views.get_communities'),
    # PROVIDERDS
    url(r'^providers$', 'socialplus.views.get_providers'),
    # TASKS
    url(r'^tasks$', 'socialplus.views.get_post_tasks'),
    url(r'^cron/start_task/(?P<name>[^/]+)$', 'socialplus.views.create_task_cron_shortcut'),
    url(r'^tasks/completed$', 'socialplus.views.get_delete_tasks_completed'),
    url(r'^tasks/active$', 'socialplus.views.get_tasks_active'),
    url(r'^tasks/(?P<id_>[^/]+)$', 'socialplus.views.get_task'),
    # REPORTS
    url(r'^reports/(?P<reportId>[^/]+)$', 'socialplus.views.get_delete_report'),
    url(r'^reports$', 'socialplus.views.get_post_reports'),
    # OLD STUFF
    url(r'^tag/create$', 'socialplus.views.create_tag'),
    url(r'^tag/update/(?P<tagId>[^/]+)$', 'socialplus.views.update_tag'),
    url(r'^tag/delete/(?P<tagId>[^/]+)$', 'socialplus.views.delete_tag'),
    url(r'^tag/experts/(?P<tagId>[^/]+)$', 'socialplus.views.get_experts'),
    url(r'^tags$', 'socialplus.views.get_tags'),

    url(r'^autocircle/create$', 'socialplus.circles.create_autocircle'),
    url(r'^autocircle/update/(?P<autocircleId>[^/]+)$', 'socialplus.circles.update_autocircle'),
    url(r'^autocircle/delete/(?P<autocircleId>[^/]+)$', 'socialplus.circles.delete_autocircle'),
    url(r'^autocircles$', 'socialplus.circles.get_autocircles'),
    url(r'^autocircles/sync_all$', 'socialplus.circles.sync_all_circles'),
    
    url(r'^task/sync/(?P<taskName>[^/]+)$', 'socialplus.views.start_sync'),
    url(r'^task/progress/(?P<taskId>[^/]+)$', 'socialplus.views.get_task_progress'),
    url(r'^tasks/delete_completed$', 'socialplus.views.delete_completed_tasks'),
    
    url(r'^sync/(?P<taskId>[^/]+)$', 'socialplus.views.sync_task'),    

    )
