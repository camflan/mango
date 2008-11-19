from django.conf.urls.defaults import *
import tango.views as tango_views

urlpatterns = patterns('',
    url(r'(?P<tape_slug>[\w-]{5,50})/xspf.xml/$', tango_views.track_list, {'xspf':True,}, name="track-list-xspf"),
    url(r'(?P<tape_slug>[\w-]{5,50})/$', tango_views.track_list, name="track-list"),
    url(r'$',                            tango_views.tape_list, name="tape-list"),
)

