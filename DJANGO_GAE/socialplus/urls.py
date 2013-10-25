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
    # ACTIVITY
    url(r'^activities', 'socialplus.views.search_activities'),
    # PERSON
    url(r'^people/(?P<id_>[^/]+)$', 'socialplus.views.get_person'),
    url(r'^people$', 'socialplus.views.get_people'),
    # COMMUNITY
    url(r'^communities$', 'socialplus.views.get_communities'),
    # TASKS
    url(r'^tasks$', 'socialplus.views.get_post_tasks'),
    url(r'^tasks/completed$', 'socialplus.views.get_delete_tasks_completed'),
    url(r'^tasks/active$', 'socialplus.views.get_tasks_active'),
    url(r'^tasks/(?P<id_>[^/]+)$', 'socialplus.views.get_task'),
    # REPORTS
    url(r'^reports/(?P<reportId>[^/]+)$', 'socialplus.views.get_delete_report'),
    url(r'^reports$', 'socialplus.views.get_post_reports'),
    # CIRLCES
    url(r'^circle/create$', 'socialplus.circles.create_circle'), # needs to provide "name" in request body
    url(r'^circle/delete/(?P<circleId>[^/]+)$', 'socialplus.circles.delete_circle'),
    url(r'^circle/udpate/(?P<circleId>[^/]+)$', 'socialplus.circles.update_circle'),
    url(r'^circle/get/(?P<circleId>[^/]+)$', 'socialplus.circles.get_circle'),
    url(r'^circle/publish/(?P<circleId>[^/]+)$', socialplus.circles.publish_circle),
    url(r'^circle/inadd/(?P<circleId>[^/]+)$', 'socialplus.circles.add_to_in_circle'),
    url(r'^circle/wadd/(?P<circleId>[^/]+)$', 'socialplus.circles.add_to_with_circle'),
    url(r'^circle/get/all$', 'socialplus.circles.get_all_circles'),
    url(r'^circle/sync/circles$', 'socialplus.circles.sync_all_circles'),
    url(r'^circle/sync/domain$', 'socialplus.circles.sync_domain'),
    
    ####
    # OLD STUFF
    url(r'^tag/create$', 'socialplus.views.create_tag'),
    url(r'^tag/update/(?P<tagId>[^/]+)$', 'socialplus.views.update_tag'),
    url(r'^tag/delete/(?P<tagId>[^/]+)$', 'socialplus.views.delete_tag'),
    url(r'^tag/experts/(?P<tagId>[^/]+)$', 'socialplus.views.get_experts'),
    url(r'^tags$', 'socialplus.views.get_tags'),
    
    url(r'^task/sync/(?P<taskName>[^/]+)$', 'socialplus.views.start_sync'),
    url(r'^task/progress/(?P<taskId>[^/]+)$', 'socialplus.views.get_task_progress'),
    url(r'^tasks/delete_completed$', 'socialplus.views.delete_completed_tasks'),
    
    url(r'^sync/(?P<taskId>[^/]+)$', 'socialplus.views.sync_task'),    

    )
