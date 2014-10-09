from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from sorl.thumbnail.fields import ImageWithThumbnailsField
from south.modelsinspector import add_introspection_rules
import re
import os.path
from django.template.defaultfilters import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save


add_introspection_rules(
    [],
    ["sorl.thumbnail.fields.ImageWithThumbnailsField"])


class Item(models.Model):
    title = models.CharField(max_length=256)
    body = models.TextField(blank=True, default=u"")
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    image = ImageWithThumbnailsField(
        upload_to="convoimages/%Y/%m/%d",
        thumbnail={
            'size': (400, 200)
            },
        null=True,
        )

    class Meta:
        ordering = ['-added', ]

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "/item/%04d/%02d/%02d/%d/" % (
            self.added.year, self.added.month,
            self.added.day, self.id)

    def touch(self):
        self.modified = datetime.now()
        self.save()

    def add_reply(self, author, body, url='', title=''):
        if not author:
            return
        if body.strip() == '' and url.strip() == '':
            return
        if (url.strip() != '' and
                not (url.startswith('http://') or url.startswith('https://'))):
            url = "http://" + url
        r = Reply.objects.create(
            item=self,
            author=author,
            body=body,
            url=url.strip(), title=title.strip())
        self.touch()
        return r

    def reply_pairs(self):
        a = list(self.reply_set.all())
        pairs = zip(a[0::2], a[1::2])
        if (len(a) % 2) == 1:
            pairs.append((a[-1],))
        return pairs


@receiver(post_save, sender=Item)
def new_item_emails(sender, **kwargs):
    if not kwargs.get('created', False):
        # only send it on creation
        return
    for u in User.objects.all():
        if u.is_anonymous() or u.username == 'AnonymousUser':
            continue
        i = kwargs['instance']
        u.email_user(
            "[spokehub] new conversation: " + i.title,
            i.body + "\n\n---\nhttp://spokehub.org/\n",
            'hello@spokehub.org')


class Reply(models.Model):
    item = models.ForeignKey(Item)
    author = models.ForeignKey(User)
    body = models.TextField(blank=True, default=u"")
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    image = ImageWithThumbnailsField(
        upload_to="replyimages/%Y/%m/%d",
        thumbnail={
            'size': (400, 200)
            },
        null=True,
        )
    url = models.TextField(blank=True, default=u"")
    title = models.TextField(blank=True, default=u"")

    class Meta:
        order_with_respect_to = 'item'
        ordering = ['added']

    def __unicode__(self):
        return "Reply to [%s] by %s at %s" % (
            str(self.item),
            self.author.username,
            self.added.isoformat())

    def save_image(self, f):
        ext = f.name.split(".")[-1].lower()
        basename = slugify(f.name.split(".")[-2].lower())[:20]
        if ext not in ['jpg', 'jpeg', 'gif', 'png']:
            # unsupported image format
            return None
        now = datetime.now()
        path = "replyimages/%04d/%02d/%02d/" % (now.year, now.month, now.day)
        try:
            os.makedirs(settings.MEDIA_ROOT + "/" + path)
        except:
            pass
        full_filename = path + "%s.%s" % (basename, ext)
        fd = open(settings.MEDIA_ROOT + "/" + full_filename, 'wb')
        for chunk in f.chunks():
            fd.write(chunk)
        fd.close()
        self.image = full_filename
        self.save()

    def mentioned_users(self):
        pattern = re.compile('\@(\w+)', re.MULTILINE)
        usernames = [u.lower() for u in pattern.findall(self.body)]
        usernames = list(set(usernames))
        users = []
        for u in usernames:
            if u == self.author.username:
                continue
            r = User.objects.filter(username__iexact=u)
            if not r.exists():
                continue
            users.append(r[0])
        return users

    def conversation_users(self):
        users = []
        for r in self.item.reply_set.all():
            if r.author.username == self.author.username:
                continue
            users.append(r.author)
        return list(set(users))

    def email_mentions(self):
        conv_users = self.conversation_users()
        mentioned = self.mentioned_users()
        unmentioned = set(conv_users) - set(mentioned)
        for user in mentioned:
            user.email_user(
                "[spokehub] someone mentioned you on spokehub",
                """%s mentioned you in a reply:

%s
""" % (self.author.username, self.body),
                'hello@spokehub.org',
                )
        for user in unmentioned:
            user.email_user(
                "[spokehub] conversation reply",
                """%s replied to a spokehub conversation that you
are participating in:

%s
""" % (self.author.username, self.body))


class WorkSample(models.Model):
    user = models.ForeignKey(User)
    image = ImageWithThumbnailsField(
        upload_to="images/%Y/%m/%d",
        thumbnail={
            'size': (400, 200)
            },
        )
    title = models.TextField(default="", blank=True)
    youtube_id = models.TextField(default="", blank=True)

    def __unicode__(self):
        return self.user.username + " - " + self.title

    def save_image(self, f):
        ext = f.name.split(".")[-1].lower()
        basename = slugify(f.name.split(".")[-2].lower())[:20]
        if ext not in ['jpg', 'jpeg', 'gif', 'png']:
            # unsupported image format
            return None
        now = datetime.now()
        path = "images/%04d/%02d/%02d/" % (now.year, now.month, now.day)
        try:
            os.makedirs(settings.MEDIA_ROOT + "/" + path)
        except:
            pass
        full_filename = path + "%s.%s" % (basename, ext)
        fd = open(settings.MEDIA_ROOT + "/" + full_filename, 'wb')
        for chunk in f.chunks():
            fd.write(chunk)
        fd.close()
        self.image = full_filename
        self.save()


class NowPost(models.Model):
    user = models.ForeignKey(User)
    created = models.DateTimeField()
    service = models.TextField(default="", blank=True)
    service_id = models.TextField(default="", blank=True)
    text = models.TextField(default="", blank=True)
    original = models.TextField(default="", blank=True)

    image_url = models.TextField(default="", blank=True)
    image_width = models.IntegerField(default=0)
    image_height = models.IntegerField(default=0)

    def __unicode__(self):
        return "[%s] by %s at %s" % (self.service, self.user.username,
                                     self.created.isoformat())

    def twitter_handle(self):
        return self.user.get_profile().twitter().screen_name

    def external_link(self):
        # expand for other services later
        if self.service == 'twitter':
            return ("https://twitter.com/" + self.twitter_handle()
                    + "/status/" + self.service_id)
        elif self.service == 'instagram':
            return self.service_id
        else:
            return None
