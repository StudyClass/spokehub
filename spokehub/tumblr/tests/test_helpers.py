import unittest
from spokehub.tumblr import video_text, audio_text


class TestHelpers(unittest.TestCase):
    def test_video_text_nonvideo(self):
        r = video_text('something', None, 'some text')
        self.assertEqual(r, 'some text')

    def test_video_text_video(self):
        d = {'player': [{'embed_code': 'an embed code'}]}
        r = video_text('video', d, 'some text')
        self.assertEqual(r, 'an embed code')

    def test_audio_text_nonaudio(self):
        r = audio_text('something', None, 'some text')
        self.assertEqual(r, 'some text')

    def test_audio_text_video(self):
        d = {'player': 'some audio text'}
        r = audio_text('audio', d, 'some text')
        self.assertEqual(r, 'some audio text')
