# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from waffle.testutils import override_switch
from spokehub.profile.utils import get_user_profile
from .factories import (
    UserFactory, ConversationFactory, ReplyFactory,
    NowPostFactory)
from spokehub.main.models import Conversation, NowPost, Comment


class ConversationTest(TestCase):
    def test_get_absolute_url(self):
        i = ConversationFactory()
        self.assertTrue(i.get_absolute_url().startswith('/we/'))

    def test_unicode(self):
        i = ConversationFactory()
        self.assertEqual(str(i), "foo")

    def test_unicode_nonascii(self):
        i = ConversationFactory()
        i.body = u"DERRIÈRE"
        self.assertEqual(str(i), i.body)

    def test_edit_url(self):
        i = ConversationFactory()
        self.assertIsNotNone(i.get_edit_url())

    def test_delete_url(self):
        i = ConversationFactory()
        self.assertIsNotNone(i.get_delete_url())

    def test_touch(self):
        i = ConversationFactory()
        modified = i.modified
        i.touch()
        i2 = Conversation.objects.get(id=i.id)
        self.assertTrue(i2.modified > modified)

    def test_add_reply(self):
        u = UserFactory()
        i = ConversationFactory()
        i.add_reply(u, 'a body')
        self.assertEqual(i.reply_set.all().count(), 1)

    @override_switch('send_email', True)
    def test_add_reply_with_mention(self):
        u = UserFactory()
        p = get_user_profile(u)
        p.allow_email = True
        p.save()
        i = ConversationFactory(author=u)
        u2 = UserFactory()
        p = get_user_profile(u2)
        p.allow_email = True
        p.save()
        i.add_reply(u, "a body that mentions @%s" % u2.username)
        self.assertEqual(i.reply_set.all().count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    @override_switch('send_email', True)
    def test_add_reply_with_other_participants(self):
        u = UserFactory()
        p = get_user_profile(u)
        p.allow_email = True
        p.save()
        i = ConversationFactory(author=u)
        i.add_reply(u, "a body")
        self.assertEqual(i.reply_set.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        u2 = UserFactory()
        i.add_reply(u2, "another message")
        self.assertEqual(i.reply_set.all().count(), 2)
        self.assertEqual(len(mail.outbox), 2)

    def test_add_reply_no_author(self):
        i = ConversationFactory()
        i.add_reply(None, 'a body')
        self.assertEqual(i.reply_set.all().count(), 0)

    def test_add_reply_empty_body(self):
        i = ConversationFactory()
        u = UserFactory()
        i.add_reply(u, '')
        self.assertEqual(i.reply_set.all().count(), 0)

    def test_add_reply_fix_url(self):
        i = ConversationFactory()
        u = UserFactory()
        i.add_reply(u, 'a body', 'example.com')
        r = i.reply_set.all()[0]
        self.assertFalse(r.is_video())
        self.assertFalse(r.is_youtube())
        self.assertFalse(r.is_vimeo())
        self.assertEqual(r.url, "http://example.com")

    def test_add_reply_no_url(self):
        i = ConversationFactory()
        u = UserFactory()
        i.add_reply(u, 'a body', '')
        r = i.reply_set.all()[0]
        self.assertFalse(r.is_video())
        self.assertFalse(r.is_youtube())
        self.assertFalse(r.is_vimeo())
        self.assertEqual(r.url, "")

    def test_add_reply_youtube(self):
        i = ConversationFactory()
        u = UserFactory()
        i.add_reply(u, 'a body', 'http://youtube.com/?v=foo')
        r = i.reply_set.all()[0]
        self.assertTrue(r.is_video())
        self.assertTrue(r.is_youtube())
        self.assertFalse(r.is_vimeo())
        self.assertEqual(r.youtube_id, "foo")

    def test_add_reply_vimeo(self):
        i = ConversationFactory()
        u = UserFactory()
        i.add_reply(u, 'a body', 'http://vimeo.com/foo')
        r = i.reply_set.all()[0]
        self.assertTrue(r.is_video())
        self.assertFalse(r.is_youtube())
        self.assertTrue(r.is_vimeo())
        self.assertEqual(r.vimeo_id, "foo")


class DummyFile(object):
    pass


class ReplyTest(TestCase):
    def test_unicode(self):
        r = ReplyFactory()
        self.assertTrue(str(r).startswith("Reply to"))

    def test_mentioned_users(self):
        u = UserFactory()
        u2 = UserFactory()
        r = ReplyFactory(
            body="@nonexistent @%s @%s" % (u.username, u2.username),
            author=u2)
        self.assertEqual(r.mentioned_users(), [u])

    def test_conversation_users(self):
        r = ReplyFactory()
        self.assertEqual(len(r.conversation_users()), 0)
        ReplyFactory(item=r.item)
        self.assertEqual(len(r.conversation_users()), 1)

    def test_link_usernames(self):
        u = UserFactory()
        u2 = UserFactory()
        r = ReplyFactory(
            body="@nonexistent @%s @%s" % (u.username, u2.username),
            author=u2)
        new_body = r.link_usernames()
        self.assertEquals(
            new_body,
            """@nonexistent [@%s](/accounts/%s/) [@%s](/accounts/%s/)""" % (
                u.username, u.username, u2.username, u2.username)
        )

    def test_save_image_invalid_ext(self):
        r = ReplyFactory()
        d = DummyFile()
        d.name = "invalid.extension"
        self.assertIsNone(r.save_image(d))


class CommentTests(TestCase):
    def test_create(self):
        r = ReplyFactory()
        u = UserFactory()
        c = Comment.objects.create(reply=r, author=u, body="some text")
        self.assertIsNotNone(c)


class NowPostTest(TestCase):
    def test_unicode(self):
        n = NowPostFactory()
        self.assertTrue(str(n).startswith("[twitter]"))

    def test_twitter_external_link(self):
        n = NowPostFactory()
        self.assertTrue(n.external_link().startswith("https://twitter.com/"))

    def test_instagram_external_link(self):
        n = NowPostFactory(service="instagram")
        self.assertTrue(n.external_link().startswith(n.service_id))

    def test_misc_external_link(self):
        n = NowPostFactory(service="foo")
        self.assertIsNone(n.external_link())

    def test_create_instagram(self):
        np = NowPost.objects.create_instagram(
            "foo", "bar", "text", timezone.now(),
            "http://example.com/image", "http://example.com/video",
            "{}")
        self.assertEqual(np.image_width, 640)
        self.assertEqual(np.service, "instagram")

    def test_create_twitter(self):
        np = NowPost.objects.create_twitter(
            "foo", "bar", "text", timezone.now(),
            "{}")
        self.assertEqual(np.service, "twitter")

    def test_create_tumblr(self):
        np = NowPost.objects.create_tumblr(
            "foo", "bar", "text", timezone.now(),
            "http://example.com/image", 640, 480,
            "{}")
        self.assertEqual(np.service, "tumblr")
