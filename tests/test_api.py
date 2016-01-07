import unittest
import deviantart
from api_credentials import CLIENT_ID, CLIENT_SECRET

class ApiTest(unittest.TestCase):

    def setUp(self):
        self.da = deviantart.Api(CLIENT_ID, CLIENT_SECRET)

    def test_get_user(self):
        user = self.da.get_user("devart")
        self.assertEqual("devart", user.username)

    def test_get_deviation(self):
        deviation = self.da.get_deviation("234546F5-C9D1-A9B1-D823-47C4E3D2DB95")
        self.assertEqual("234546F5-C9D1-A9B1-D823-47C4E3D2DB95", deviation.deviationid)

    def test_get_comment(self):
        comments = self.da.get_comments("siblings", commentid="E99B1CEB-933F-B54D-ABC2-88FD0F66D421")
        comment = comments['thread'][0]
        self.assertEqual("E99B1CEB-933F-B54D-ABC2-88FD0F66D421", comment.commentid)
