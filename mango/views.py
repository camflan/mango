from django.template import loader, Context, RequestContext
from django.shortcuts import *
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site

from mango.models import Tape, Track

def track_list(request, tape_slug=None, xspf=False, template_name="track_list.html"):
    site = Site.objects.get_current()

    tape = get_object_or_404(Tape, slug=tape_slug)
    tracks = tape.track_set.all()

    context = {'tape':tape, 'tracks':tracks, 'site':site,}

    if xspf:
        t = loader.get_template('xspf.txt')
        content = t.render(Context(context))
        return HttpResponse(content, mimetype="application/xspf+xml")

    return render_to_response(template_name, context , context_instance=RequestContext(request))

def tape_list(request, template_name="tape_list.html"):
    site = Site.objects.get_current()
    return render_to_response(template_name, {'tapes':Tape.objects.all(), 'site':site}, context_instance=RequestContext(request))
