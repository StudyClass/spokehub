from json import dumps
from django.conf import settings
from django_statsd.clients import statsd
from .scrape import (
    get_script, parse_json, entries, Entry,
    user_page_entries
)
import requests


class Adder(object):
    def __init__(self):
        from ..main.models import NowPost
        self.model = NowPost

    def now_post_exists(self, service_id):
        r = self.model.objects.filter(
            service='instagram',
            service_id=service_id)
        return r.exists()

    def add(self, media):
        if self.now_post_exists(self.link(media)):
            print("existing instagram post")
            return
        try:
            self._add(media)
            print("new instagram post added")
            statsd.incr('instagram.add.success')
        except Exception as e:
            print("failed with exception: " + str(e))
            statsd.incr('instagram.add.failed')

    def text(self, media):
        try:
            return self.caption_text(media)
        except:  # noqa: E722
            return ""

    def video_url(self, media, sru):
        if media.type == 'video':
            return sru
        return ""

    def _add(self, media):
        sru = self.sru(media)
        text = self.text(media)
        video_url = self.video_url(media, sru)
        image_url = self.image_url(media, sru)

        self.model.objects.create_instagram(
            self.username(media), self.link(media), text,
            self.created_time(media),
            image_url, video_url, dumps(
                dict(
                    standard_resolution_url=sru,
                    thumbnail_url=self.thumbnail_url(media),
                    id=media.id,
                    link=self.link(media),
                    filter=self.filter(media),
                    user_id=self.user_id(media),
                    user_full_name=self.user_full_name(media),
                    user_username=self.username(media),
                    )
                )
        )


class ScrapeAdder(Adder):
    def link(self, media):
        return media.url()

    def sru(self, media):
        return media.clean_display_src()

    def caption_text(self, media):
        return media.caption

    def created_time(self, media):
        return media.date.isoformat()

    def image_url(self, media, media_url):
        return media_url

    def thumbnail_url(self, media):
        return media.clean_thumbnail_src()

    def user_id(self, media):
        return media.owner

    def user_full_name(self, media):
        return media.fullname()

    def username(self, media):
        return media.username()

    def filter(self, media):
        return ""


def scrape_entries(entry_data):
    a = ScrapeAdder()
    for entry in entry_data:
        graphql = False
        if 'node' in entry.keys():
            entry = entry['node']
            graphql = True
        if graphql:
            print("- entry {}".format(entry['shortcode']))
        else:
            print("- entry {}".format(entry['code']))
        e = Entry(entry, graphql)
        if e.is_video:
            # can't handle video yet
            print("skip video")
            continue
        a.add(e)


def hashtag_scrape():
    print("hashtag scrape")
    tag_name = settings.HASHTAG.strip('#')

    url = "https://www.instagram.com/explore/tags/{}/".format(tag_name)
    r = requests.get(url)
    print("fetched")
    script = get_script(r.text)
    d = parse_json(script)
    print("parsed")
    entry_data = entries(d)
    scrape_entries(entry_data)
    statsd.incr('instagram.hashtag.run')


def my_posts_scrape():
    print("my posts scrape")
    username = settings.INSTAGRAM_USER

    url = "https://www.instagram.com/{}/".format(username)
    r = requests.get(url)
    print("fetched")
    script = get_script(r.text)
    d = parse_json(script)
    print("parsed")
    entry_data = user_page_entries(d)
    scrape_entries(entry_data)
    statsd.incr('instagram.myposts.run')
