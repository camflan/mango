import os

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import pluralize

from MP3Info import MP3Info

# get user settings, if they have anything specified, or use our defaults
DEFAULT_SUBTITLE_FSTRING = getattr(settings, 
                                    'MANGO_DEFAULT_SUBTITLE_FSTRING', 
                                    "%(track_count)s %(track_string)s. %(duration_string)s")
TIME_SEPARATOR = getattr(settings, 
                                    'MANGO_TIME_SEPARATOR', 
                                    ':')
TAPE_DIRECTORY = getattr(settings,
                                    'MANGO_TAPE_STORAGE_ROOT',
                                    settings.MEDIA_URL)

fs = FileSystemStorage(location=TAPE_DIRECTORY)

def build_upload_path(instance, filename):
    import os.path
    return os.path.join(instance.tape.path, filename)

class MangoBase(models.Model):
    """
    This is our base class, for now there is only a duration field and it's
    pretty output method. I had put more here, but I needed more control over
    the title field per model.

    """
    duration = models.PositiveIntegerField(help_text="Run time of track, or total runtime of tape.", default=0, editable=False, blank=True)

    class Meta:
        abstract = True

    def _split_into_parts(self, seconds=None):
        if not seconds:
            seconds = self.duration
        seconds = self.duration%60
        minutes = self.duration/60
        if seconds < 10:
            seconds = "0%s" % seconds
        return minutes, seconds

    @property
    def duration_pretty(self):
        minutes, seconds = self._split_into_parts()
        return u"%s%s%s" % (minutes, TIME_SEPARATOR, seconds)

    @property
    def duration_string(self):
        minutes, seconds = self._split_into_parts()
        return "%s mins, %s secs" % (minutes, seconds)

class Tape(MangoBase):
    """
    This is our tape model, these are the playlists for your mixtapes. Adding tracks
    to a tape increments it's duration for you, and deleting a track decrements it.

    """
    title = models.CharField(help_text="Give it an awesome name.", max_length=200)
    subtitle = models.CharField(help_text="Leave this blank and we'll put some informative stuff here.", max_length=200, blank=True)
    banner_color = models.CharField(help_text="This is the background color of the mixtape banner.", max_length=200, default="#000")
    slug = models.SlugField(help_text="This will be filled in automagically, but you can change it.", blank=True,)

    class Meta:
        ordering = ['title',] 

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('track-list', (), {'tape_slug':self.slug})

    @models.permalink
    def get_absolute_xspf_url(self):
        return ('track-list-xspf', (), {'tape_slug':self.slug})

    @property
    def path(self):
        return '%s/%s' % (TAPE_DIRECTORY, self.slug)

    def force_recalculate_duration(self):
        """
        This is provided as an easy way to recalculate the duration of your
        mixtape if you think it's out of whack.

        """
        return sum(self.track_set.values('duration', flat=True))


class Track(MangoBase):
    """
    Here is the track model. You add a file to the track, and we fill in
    the artist/title/duration information from the ID3 tag and file size/bitrate.

    """
    tape = models.ForeignKey(Tape, help_text="What tape are you adding this to?")
    artist = models.CharField(help_text="Leave this blank and we will fill it in for you with the ID3 information.", max_length=200, blank=True,)
    title = models.CharField(help_text="Leave this blank and we will fill it in for you with the ID3 information.", max_length=200, blank=True,)
    track_num = models.IntegerField(help_text="We populate this initially and it can be edited properly with our js mixtape editor.", blank=True,)
    file = models.FileField(help_text="Give us the song!", storage=fs, upload_to=build_upload_path)

    class Meta:
        ordering = ['tape', 'track_num',]

    def save(self, *args, **kwargs):
        m = MP3Info(file(self.file.name))
        if not self.artist:
            self.artist = m.artist[1:]
        if not self.title:
            self.title = m.title[1:]
        if not self.duration:
            self.duration = (int(m.mpeg.length_minutes) * 60) + int(m.mpeg.length_seconds)
            self.tape.duration += self.duration
            self.tape.save()
        if not self.track_num:
            self.track_num = self.tape.track_set.count() + 1
        super(Track, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s - %s' % (self.artist, self.title)

    def get_absolute_url(self):
        return '%s/%s/%s' % (TAPE_DIRECTORY, self.tape.slug, os.path.basename(self.file.name))

def _increment_tape_duration(sender, instance, **kwargs):
    if not instance.id:
        instance.tape.duration += instance.duration
        instance.tape.save()

def _decrement_tape_duration(sender, instance, signal, **kwargs):
    instance.tape.duration -= instance.duration
    instance.tape.save()

def _update_subtitle(sender, instance, signal, **kwargs):
    """
    This is used to add a informative subtitle to our tape if no subtitle
    is given.

    """
    import re
    if re.search('\d{1,3}\stracks?.', instance.subtitle) or not instance.subtitle:
        """ 
        This should be either our subtitle or it's blank. Either way,
        we are going to update it with the newest information.

        """
        track_count = instance.track_set.count() + 1 # we cheat on this, it's a pre-save signal and the count is one less than we want.
        track_string = "track%s" % pluralize(track_count, 's')
        instance.subtitle = DEFAULT_SUBTITLE_FSTRING % {'track_count':track_count, 'track_string':track_string, 'duration_string':instance.duration_string,}

#models.signals.pre_save.connect(_increment_tape_duration, sender=Track)
models.signals.pre_delete.connect(_decrement_tape_duration, sender=Track)
models.signals.pre_save.connect(_update_subtitle, sender=Tape)
