from django.conf.urls.defaults import *
import mango.views as mango_views

urlpatterns = patterns('',
    url(r'(?P<tape_slug>[\w-]{5,50})/xspf.xml/$', mango_views.track_list, {'xspf':True,}, name="track-list-xspf"),
    url(r'(?P<tape_slug>[\w-]{5,50})/$', mango_views.track_list, name="track-list"),
    url(r'$',                            mango_views.tape_list, name="tape-list"),
)

