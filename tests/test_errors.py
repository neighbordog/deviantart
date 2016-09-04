import unittest
import deviantart
from deviantart.api import DeviantartError
from helpers import mock_response


class ErrorsTest(unittest.TestCase):

    @mock_response('token')
    def setUp(self):
        self.da = deviantart.Api("", "")

    def test_browse(self):
        for ep in ["morelikethis", "tags"]:
            with self.assertRaises(DeviantartError):
                self.da.browse(endpoint=ep)

    def test_unknown_endpoint(self):
        for call in [self.da.browse, self.da.get_data, self.da.get_comments]:
            with self.assertRaisesRegexp(DeviantartError, "Unknown endpoint"):
                call(endpoint="unknown")

    def test_missing_user(self):
        for call in [self.da.get_collections, self.da.get_gallery_folder,
                self.da.get_gallery_folders, self.da.get_user]:
            with self.assertRaisesRegexp(DeviantartError, "No username"):
                call()
        with self.assertRaisesRegexp(DeviantartError, "No username"):
            self.da.get_collection("ignored")

    def test_comments_missing_param(self):
        for ep in ["deviation", "profile", "status", "siblings"]:
            with self.assertRaisesRegexp(DeviantartError, "No .* defined"):
                self.da.get_comments(endpoint=ep)


    def test_wrong_grant(self):
        errRegEx = "Grant Type"
        da = self.da # Shortcut
        for call in [da.get_damntoken, da.get_notes_folders]:
            with self.assertRaisesRegexp(DeviantartError, errRegEx):
                call()
        for call in [da.fave, da.unfave, da.get_users, da.watch, da.unwatch,
                da.is_watching, da.update_user, da.post_status,
                da.get_messages, da.delete_message, da.get_feedback,
                da.get_feedback_in_stack, da.get_mentions,
                da.get_mentions_in_stack, da.get_notes, da.get_note,
                da.send_note, da.delete_notes, da.create_notes_folder,
                da.delete_notes_folder]:
            with self.assertRaisesRegexp(DeviantartError, errRegEx):
                call("ignored")
        for call in [da.post_comment, da.move_notes, da.mark_notes,
                da.rename_notes_folder]:
            with self.assertRaisesRegexp(DeviantartError, errRegEx):
                call("ignored", "ignored")
