"""
    deviantart.api
    ^^^^^^^^^^^^^^
    
    A Python wrapper for the DeviantArt API
    
    :copyright: (c) 2015 by Kevin Eichhorn
"""

from __future__ import absolute_import

try:
    from urllib import urlencode
    from urllib2 import HTTPError
except ImportError:
    from urllib.parse import urlencode
    from urllib.error import HTTPError
from sanction import Client

from .deviation import Deviation
from .user import User
from .comment import Comment
from .status import Status
from .message import Message

class DeviantartError(Exception):

    """Representing API Errors"""

    @property
    def message(self):
        return self.args[0]


class Api(object):

    """The API Interface (handles requests to the DeviantArt API)

       :param client_id: client_id provided by DeviantArt
       :param client_secret: client_secret provided by DeviantArt
       :param standard_grant_type: The used authorization type | client_credentials (read-only) or authorization_code
       :param scope: The scope of data the application can access    
    """

    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri="",
        standard_grant_type="client_credentials",
        scope="browse feed message note stash user user.manage comment.post collection"
    ):

        """Instantiate Class and create OAuth Client"""

        self.client_id = client_id
        self.client_secret = client_secret

        self.auth_endpoint = "https://www.deviantart.com/oauth2/authorize"
        self.token_endpoint = "https://www.deviantart.com/oauth2/token"
        self.resource_endpoint = "https://www.deviantart.com/api/v1/oauth2"
        self.redirect_uri = redirect_uri
        self.standard_grant_type = standard_grant_type
        self.scope = scope
        self.access_token = None
        self.refresh_token = None

        self.oauth = Client(
            auth_endpoint=self.auth_endpoint,
            token_endpoint=self.token_endpoint,
            resource_endpoint=self.resource_endpoint,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        if self.standard_grant_type == "client_credentials":
            self.auth()



    def auth(self, code="", refresh_token=""):

        """Authenticates user and retrieves (and refreshes) access token

        :param code: code provided after redirect (authorization_code only)
        :param refresh_token: the refresh_token to update access_token without authorization
        """

        if refresh_token:
            try:
                self.oauth.request_token(grant_type="refresh_token", refresh_token=refresh_token)
                self.refresh_token = self.oauth.refresh_token
            except HTTPError as e:

                if e.code == 401:
                    raise DeviantartError("Unauthorized: Please check your credentials (client_id and client_secret).")
                else:
                    raise DeviantartError(e)
        elif self.standard_grant_type == "authorization_code":
            try:
                self.oauth.request_token(grant_type=self.standard_grant_type, redirect_uri=self.redirect_uri, code=code)
                self.refresh_token = self.oauth.refresh_token
            except HTTPError as e:

                if e.code == 401:
                    raise DeviantartError("Unauthorized: Please check your credentials (client_id and client_secret).")
                else:
                    raise DeviantartError(e)
        elif self.standard_grant_type == "client_credentials":
            try:
                self.oauth.request_token(grant_type=self.standard_grant_type)
            except HTTPError as e:

                if e.code == 401:
                    raise DeviantartError("Unauthorized: Please check your credentials (client_id and client_secret).")
                else:
                    raise DeviantartError(e)
        else:
            raise DeviantartError('Unknown grant type.')

        self.access_token = self.oauth.access_token



    @property
    def auth_uri(self):

        """The authorzation URL that should be provided to the user"""

        return self.oauth.auth_uri(redirect_uri=self.redirect_uri, scope=self.scope)



    def browse_dailydeviations(self):

        """Retrieves Daily Deviations"""

        response = self._req('/browse/dailydeviations')


        deviations = []
        for item in response['results']:
            d = Deviation()
            d.from_dict(item)
            deviations.append(d)

        return deviations



    def browse_userjournals(self, username, featured=False, offset=0, limit=10):

        """Fetch user journals from user

        :param username: name of user to retrieve journals from
        :param featured: fetch only featured or not
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        response = self._req('/browse/user/journals', {
            "username":username,
            "featured":featured,
            "offset":offset,
            "limit":limit
        })

        deviations = []

        for item in response['results']:
            d = Deviation()
            d.from_dict(item)
            deviations.append(d)

        return {
            "results" : deviations,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def browse_morelikethis_preview(self, seed):

        """Fetch More Like This preview result for a seed deviation

        :param seed: The deviationid to fetch more like
        """

        response = self._req('/browse/morelikethis/preview', {
            "seed":seed
        })

        returned_seed = response['seed']

        author = User()
        author.from_dict(response['author'])

        more_from_artist = []

        for item in response['more_from_artist']:
            d = Deviation()
            d.from_dict(item)
            more_from_artist.append(d)

        more_from_da = []

        for item in response['more_from_da']:
            d = Deviation()
            d.from_dict(item)
            more_from_da.append(d)

        return {
            "seed" : returned_seed,
            "author" : author,
            "more_from_artist" : more_from_artist,
            "more_from_da" : more_from_da
        }



    def browse(self, endpoint="hot", category_path="", seed="", q="", timerange="24hr", tag="", offset=0, limit=10):

        """Fetch deviations from public endpoints

        :param endpoint: The endpoint from which the deviations will be fetched (hot/morelikethis/newest/undiscovered/popular/tags)
        :param category_path: category path to fetch from
        :param q: Search query term
        :param timerange: The timerange
        :param tag: The tag to browse
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if endpoint == "hot":
            response = self._req('/browse/hot', {
                "category_path":category_path,
                "offset":offset,
                "limit":limit
            })
        elif endpoint == "morelikethis":
            if seed:
                response = self._req('/browse/morelikethis', {
                    "seed":seed,
                    "category_path":category_path,
                    "offset":offset,
                    "limit":limit
                })
            else:
                raise DeviantartError("No seed defined.")
        elif endpoint == "newest":
            response = self._req('/browse/newest', {
                "category_path":category_path,
                "q":q,
                "offset":offset,
                "limit":limit
            })
        elif endpoint == "undiscovered":
            response = self._req('/browse/undiscovered', {
                "category_path":category_path,
                "offset":offset,
                "limit":limit
            })
        elif endpoint == "popular":
            response = self._req('/browse/popular', {
                "category_path":category_path,
                "q":q,
                "timerange":timerange,
                "offset":offset,
                "limit":limit
            })
        elif endpoint == "tags":
            if tag:
                response = self._req('/browse/tags', {
                    "tag":tag,
                    "offset":offset,
                    "limit":limit
                })
            else:
                raise DeviantartError("No tag defined.")
        else:
            raise DeviantartError("Unknown endpoint.")

        deviations = []

        for item in response['results']:
            d = Deviation()
            d.from_dict(item)
            deviations.append(d)

        return {
            "results" : deviations,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_categories(self, catpath="/"):

        """Fetch the categorytree

        :param catpath: The category to list children of
        """

        response = self._req('/browse/categorytree', {
            "catpath":catpath
        })

        categories = response['categories']

        return categories



    def search_tags(self, tag_name):

        """Searches for tags

        :param tag_name: Partial tag name to get autocomplete suggestions for
        """

        response = self._req('/browse/tags/search', {
            "tag_name":tag_name
        })

        tags = list()

        for item in response['results']:
            tags.append(item['tag_name'])

        return tags



    def get_deviation(self, deviationid):

        """Fetch a single deviation

        :param deviationid: The deviationid you want to fetch
        """

        response = self._req('/deviation/{}'.format(deviationid))
        d = Deviation()
        d.from_dict(response)

        return d



    def whofaved_deviation(self, deviationid, offset=0, limit=10):

        """Fetch a list of users who faved the deviation

        :param deviationid: The deviationid you want to fetch
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        response = self._req('/deviation/whofaved', get_data={
            'deviationid' : deviationid,
            'offset' : offset,
            'limit' : limit
        })

        users = []

        for item in response['results']:
            u = {}
            u['user'] = User()
            u['user'].from_dict(item['user'])
            u['time'] = item['time']

            users.append(u)

        return {
            "results" : users,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_deviation_metadata(self, deviationids, ext_submission=False, ext_camera=False, ext_stats=False, ext_collection=False):

        """Fetch deviation metadata for a set of deviations

        :param deviationid: The deviationid you want to fetch
        :param ext_submission: Return extended information - submission information
        :param ext_camera: Return extended information - EXIF information (if available)
        :param ext_stats: Return extended information - deviation statistics
        :param ext_collection: Return extended information - favourited folder information
        """

        response = self._req('/deviation/metadata', {
            'ext_submission' : ext_submission,
            'ext_camera' : ext_camera,
            'ext_stats' : ext_stats,
            'ext_collection' : ext_collection
        },
        post_data={
            'deviationids[]' : deviationids
        })

        metadata = []

        for item in response['metadata']:
            m = {}
            m['deviationid'] = item['deviationid']
            m['printid'] = item['printid']

            m['author'] = User()
            m['author'].from_dict(item['author'])

            m['is_watching'] = item['is_watching']
            m['title'] = item['title']
            m['description'] = item['description']
            m['license'] = item['license']
            m['allows_comments'] = item['allows_comments']
            m['tags'] = item['tags']
            m['is_favourited'] = item['is_favourited']
            m['is_mature'] = item['is_mature']

            if "submission" in item:
                m['submission'] = item['submission']

            if "camera" in item:
                m['camera'] = item['camera']

            if "collections" in item:
                m['collections'] = item['collections']

            metadata.append(m)

        return metadata



    def get_deviation_embeddedcontent(self, deviationid, offset_deviationid="", offset=0, limit=10):

        """Fetch content embedded in a deviation

        :param deviationid: The deviationid of container deviation
        :param offset_deviationid: UUID of embedded deviation to use as an offset
        :param offset: the pagination offset
        :param limit: the pagination limit
        """
        
        response = self._req('/deviation/embeddedcontent', {
            'deviationid' : deviationid,
            'offset_deviationid' : offset_deviationid,
            'offset' : 0,
            'limit' : 0
        })

        deviations = []

        for item in response['results']:

            d = Deviation()
            d.from_dict(item)

            deviations.append(d)

        return {
            "results" : deviations,
            "has_less" : response['has_less'],
            "has_more" : response['has_more'],
            "prev_offset" : response['prev_offset'],
            "next_offset" : response['next_offset']
        }



    def get_deviation_content(self, deviationid):

        """Fetch full data that is not included in the main devaition object

        The endpoint works with journals and literatures. Deviation objects returned from API contain only excerpt of a journal, use this endpoint to load full content. 
        Any custom CSS rules and fonts applied to journal are also returned.

        :param deviationid: UUID of the deviation to fetch full data for
        """
        
        response = self._req('/deviation/content', {
            'deviationid':deviationid
        })

        content = {}

        if "html" in response:
            content['html'] = response['html']

        if "css" in response:
            content['css'] = response['css']

        if "css_fonts" in response:
            content['css_fonts'] = response['css_fonts']

        return content



    def download_deviation(self, deviationid):

        """Get the original file download (if allowed)

        :param deviationid: The deviationid you want download info for
        """

        response = self._req('/deviation/download/{}'.format(deviationid))

        return {
            'src' : response['src'],
            'width' : response['width'],
            'height' : response['height'],
            'filesize' : response['filesize']
        }

    def get_collections(self, username="", calculate_size=False, ext_preload=False, offset=0, limit=10):

        """Fetch collection folders

        :param username: The user to list folders for, if omitted the authenticated user is used
        :param calculate_size: The option to include the content count per each collection folder
        :param ext_preload: Include first 5 deviations from the folder
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if not username and self.standard_grant_type == "authorization_code":
            response = self._req('/collections/folders', {
                "calculate_size":calculate_size,
                "ext_preload":ext_preload,
                "offset":offset,
                "limit":limit
            })
        else:
            if not username:
                raise DeviantartError("No username defined.")
            else:
                response = self._req('/collections/folders', {
                    "username":username,
                    "calculate_size":calculate_size,
                    "ext_preload":ext_preload,
                    "offset":offset,
                    "limit":limit
                })

        folders = []

        for item in response['results']:
            f = {}
            f['folderid'] = item['folderid']
            f['name'] = item['name']

            if "size" in item:
                f['size'] = item['size']

            if "deviations" in item:
                f['deviations'] = []

                for deviation_item in item['deviations']:
                    d = Deviation()
                    d.from_dict(deviation_item)
                    f['deviations'].append(d)

            folders.append(f)

        return {
            "results" : folders,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_collection(self, folderid, username="", offset=0, limit=10):

        """Fetch collection folder contents

        :param folderid: UUID of the folder to list
        :param username: The user to list folders for, if omitted the authenticated user is used
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if not username and self.standard_grant_type == "authorization_code":
            response = self._req('/collections/{}'.format(folderid), {
                "offset":offset,
                "limit":limit
            })
        else:
            if not username:
                raise DeviantartError("No username defined.")
            else:
                response = self._req('/collections/{}'.format(folderid), {
                    "username":username,
                    "offset":offset,
                    "limit":limit
                })

        deviations = []

        for item in response['results']:
            d = Deviation()
            d.from_dict(item)
            deviations.append(d)

        if "name" in response:
            name = response['name']
        else:
            name = None

        return {
            "results" : deviations,
            "name" : name,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def fave(self, deviationid, folderid=""):

        """Add deviation to favourites

        :param deviationid: Id of the Deviation to favourite
        :param folderid: Optional UUID of the Collection folder to add the favourite into
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        post_data = {}

        post_data['deviationid'] = deviationid

        if folderid:
            post_data['folderid'] = folderid

        response = self._req('/collections/fave', post_data = post_data)

        return response



    def unfave(self, deviationid, folderid=""):

        """Remove deviation from favourites

        :param deviationid: Id of the Deviation to unfavourite
        :param folderid: Optional UUID remove from a single collection folder
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        post_data = {}

        post_data['deviationid'] = deviationid

        if folderid:
            post_data['folderid'] = folderid

        response = self._req('/collections/unfave', post_data = post_data)

        return response



    def get_gallery_folders(self, username="", calculate_size=False, ext_preload=False, offset=0, limit=10):

        """Fetch gallery folders

        :param username: The user to list folders for, if omitted the authenticated user is used
        :param calculate_size: The option to include the content count per each gallery folder
        :param ext_preload: Include first 5 deviations from the folder
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if not username and self.standard_grant_type == "authorization_code":
            response = self._req('/gallery/folders', {
                "calculate_size":calculate_size,
                "ext_preload":ext_preload,
                "offset":offset,
                "limit":limit
            })
        else:
            if not username:
                raise DeviantartError("No username defined.")
            else:
                response = self._req('/gallery/folders', {
                    "username":username,
                    "calculate_size":calculate_size,
                    "ext_preload":ext_preload,
                    "offset":offset,
                    "limit":limit
                })

        folders = []

        for item in response['results']:
            f = {}
            f['folderid'] = item['folderid']
            f['name'] = item['name']
            f['name'] = item['name']

            if "parent" in item:
                f['parent'] = item['parent']

            if "deviations" in item:
                f['deviations'] = []

                for deviation_item in item['deviations']:
                    d = Deviation()
                    d.from_dict(deviation_item)
                    f['deviations'].append(d)

            folders.append(f)

        return {
            "results" : folders,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_gallery_folder(self, username="", folderid="", mode="popular", offset=0, limit=10):

        """Fetch gallery folder contents

        :param username: The user to query, defaults to current user
        :param folderid: UUID of the folder to list, if omitted query ALL folders
        :param mode: Sort results by either newest or popular
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if not username and self.standard_grant_type == "authorization_code":
            response = self._req('/gallery/{}'.format(folderid), {
                "mode":mode,
                "offset":offset,
                "limit":limit
            })
        else:
            if not username:
                raise DeviantartError("No username defined.")
            else:
                response = self._req('/gallery/{}'.format(folderid), {
                    "username":username,
                    "mode":mode,
                    "offset":offset,
                    "limit":limit
                })

        deviations = []

        for item in response['results']:
            d = Deviation()
            d.from_dict(item)
            deviations.append(d)

        if "name" in response:
            name = response['name']
        else:
            name = None

        return {
            "results" : deviations,
            "name" : name,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_user(self, username="", ext_collections=False, ext_galleries=False):

        """Get user profile information

        :param username: username to lookup profile of
        :param ext_collections: Include collection folder info
        :param ext_galleries: Include gallery folder info
        """

        if not username and self.standard_grant_type == "authorization_code":
            response = self._req('/user/whoami')
            u = User()
            u.from_dict(response)
        else:
            if not username:
                raise DeviantartError("No username defined.")
            else:
                response = self._req('/user/profile/{}'.format(username), {
                    'ext_collections' : ext_collections,
                    'ext_galleries' : ext_galleries
                })
                u = User()
                u.from_dict(response['user'])

        return u



#     def search_friends(self, q, username=""):
#
#         if not username and self.standard_grant_type == "authorization_code":
#             response = self._req('/user/friends/search', {
#                 "q":q
#             })
#         else:
#             if not username:
#                 raise DeviantartError("No username defined.")
#             else:
#                 response = self._req('/user/friends/search', {
#                     "username":username,
#                     "q":q
#                 })
#
#         friends = []
#
#         for item in response['results']:
#             f = User()
#             f.from_dict(item)
#
#         return friends

    def get_users(self, usernames):

        """Fetch user info for given usernames

        :param username: The usernames you want metadata for (max. 50)
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/user/whois', post_data={
            "usernames":usernames
        })

        users = []

        for item in response['results']:
            u = User()
            u.from_dict(item)
            users.append(u)

        return users



    def watch(
        self,
        username,
        watch={
            "friend":True,
            "deviations":True,
            "journals":True,
            "forum_threads":True,
            "critiques":True,
            "scraps":True,
            "activity":True,
            "collections":True
        }
    ):

        """Watch a user

        :param username: The username you want to watch
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/user/friends/watch/{}'.format(username), post_data={
            "watch[friend]": watch['friend'],
            "watch[deviations]": watch['deviations'],
            "watch[journals]": watch['journals'],
            "watch[forum_threads]": watch['forum_threads'],
            "watch[critiques]": watch['critiques'],
            "watch[scraps]": watch['scraps'],
            "watch[activity]": watch['activity'],
            "watch[collections]": watch['collections'],
        })

        return response['success']



    def unwatch(self, username):

        """Unwatch a user

        :param username: The username you want to unwatch
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/user/friends/unwatch/{}'.format(username))

        return response['success']



    def is_watching(self, username):

        """Check if user is being watched by the given user

        :param username: Check if username is watching you
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/user/friends/watching/{}'.format(username))

        return response['watching']



    def update_user(self, user_is_artist="", artist_level="", artist_specialty="", real_name="", tagline="", countryid="", website="", bio=""):

        """Update the users profile information

        :param user_is_artist: Is the user an artist?
        :param artist_level: If the user is an artist, what level are they
        :param artist_specialty: If the user is an artist, what is their specialty
        :param real_name: The users real name
        :param tagline: The users tagline
        :param countryid: The users location
        :param website: The users personal website
        :param bio: The users bio
        """



        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        post_data = {}

        if user_is_artist:
            post_data["user_is_artist"] = user_is_artist

        if artist_level:
            post_data["artist_level"] = artist_level

        if artist_specialty:
            post_data["artist_specialty"] = artist_specialty

        if real_name:
            post_data["real_name"] = real_name

        if tagline:
            post_data["tagline"] = tagline

        if countryid:
            post_data["countryid"] = countryid

        if website:
            post_data["website"] = website

        if bio:
            post_data["bio"] = bio

        response = self._req('/user/profile/update', post_data=post_data)

        return response['success']

    def get_damntoken(self):

        """Retrieve the dAmn auth token required to connect to the dAmn servers"""

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/user/damntoken')

        return response['damntoken']



    def get_watchers(self, username, offset=0, limit=10):

        """Get the user's list of watchers

        :param username: The username you want to get a list of watchers of
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        response = self._req('/user/watchers/{}'.format(username), {
            'offset' : offset,
            'limit' : limit
        })

        watchers = []

        for item in response['results']:
            w = {}
            w['user'] = User()
            w['user'].from_dict(item['user'])
            w['is_watching'] = item['is_watching']
            w['lastvisit'] = item['lastvisit']
            w['watch'] = {
                "friend" : item['watch']['friend'],
                "deviations" : item['watch']['deviations'],
                "journals" : item['watch']['journals'],
                "forum_threads" : item['watch']['forum_threads'],
                "critiques" : item['watch']['critiques'],
                "scraps" : item['watch']['scraps'],
                "activity" : item['watch']['activity'],
                "collections" : item['watch']['collections']
            }

            watchers.append(w)

        return {
            "results" : watchers,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_friends(self, username, offset=0, limit=10):

        """Get the users list of friends

        :param username: The username you want to get a list of friends of
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        response = self._req('/user/friends/{}'.format(username), {
            'offset' : offset,
            'limit' : limit
        })

        friends = []

        for item in response['results']:
            f = {}
            f['user'] = User()
            f['user'].from_dict(item['user'])
            f['is_watching'] = item['is_watching']
            f['lastvisit'] = item['lastvisit']
            f['watch'] = {
                "friend" : item['watch']['friend'],
                "deviations" : item['watch']['deviations'],
                "journals" : item['watch']['journals'],
                "forum_threads" : item['watch']['forum_threads'],
                "critiques" : item['watch']['critiques'],
                "scraps" : item['watch']['scraps'],
                "activity" : item['watch']['activity'],
                "collections" : item['watch']['collections']
            }

            friends.append(f)

        return {
            "results" : friends,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_statuses(self, username, offset=0, limit=10):

        """Fetch status updates of a user

        :param username: The username you want to get a list of status updates from
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        response = self._req('/user/statuses/', {
            "username" : username,
            'offset' : offset,
            'limit' : limit
        })

        statuses = []

        for item in response['results']:
            s = Status()
            s.from_dict(item)
            statuses.append(s)

        return {
            "results" : statuses,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_status(self, statusid):

        """Fetch the status

        :param statusid: Status uuid
        """

        response = self._req('/user/statuses/{}'.format(statusid))

        s = Status()
        s.from_dict(response)

        return s



    def post_status(self, body="", id="", parentid="", stashid=""):

        """Post a status

        :param username: The body of the status
        :param id: The id of the object you wish to share
        :param parentid: The parentid of the object you wish to share
        :param stashid: The stashid of the object you wish to add to the status
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/user/statuses/post', post_data={
            "body":body,
            "id":id,
            "parentid":parentid,
            "stashid":stashid
        })

        return response['statusid']



    def get_countries(self):

        """Get a list of countries"""

        response = self._req('/data/countries')

        countries = response['results']

        return countries



    def get_data(self, endpoint="privacy"):

        """Returns policies of DeviantArt"""

        if endpoint == "privacy":
            response = self._req('/data/privacy')
        elif endpoint == "submission":
            response = self._req('/data/submission')
        elif endpoint == "tos":
            response = self._req('/data/tos')
        else:
            raise DeviantartError("Unknown endpoint.")

        return response['text']



    def get_comments(self, endpoint="deviation", deviationid="", commentid="", username="", statusid="", ext_item=False, offset=0, limit=10, maxdepth=0):

        """Fetch comments

        :param endpoint: The source/endpoint you want to fetch comments from (deviation/profile/status/siblings)
        :param deviationid: The deviationid you want to fetch
        :param commentid: The commentid you want to fetch
        :param username: The username you want to get a list of status updates from
        :param statusid: The statusid you want to fetch
        :param ext_item: the pagination limit
        :param offset: the pagination offset
        :param limit: the pagination limit
        :param maxdepth: Depth to query replies until
        """

        if endpoint == "deviation":
            if deviationid:
                response = self._req('/comments/{}/{}'.format(endpoint, deviationid), {
                    "commentid" : commentid,
                    'offset' : offset,
                    'limit' : limit,
                    'maxdepth' : maxdepth
                })
            else:
                raise DeviantartError("No deviationid defined.")

        elif endpoint == "profile":
            if username:
                response = self._req('/comments/{}/{}'.format(endpoint, username), {
                    "commentid" : commentid,
                    'offset' : offset,
                    'limit' : limit,
                    'maxdepth' : maxdepth
                })
            else:
                raise DeviantartError("No username defined.")

        elif endpoint == "status":
            if statusid:
                response = self._req('/comments/{}/{}'.format(endpoint, statusid), {
                    "commentid" : commentid,
                    'offset' : offset,
                    'limit' : limit,
                    'maxdepth' : maxdepth
                })
            else:
                raise DeviantartError("No statusid defined.")

        elif endpoint == "siblings":
            if commentid:
                response = self._req('/comments/{}/{}'.format(commentid, endpoint), {
                    "ext_item" : ext_item,
                    'offset' : offset,
                    'limit' : limit
                })
            else:
                raise DeviantartError("No commentid defined.")
        else:
            raise DeviantartError("Unknown endpoint.")

        comments = []

        for item in response['thread']:
            c = Comment()
            c.from_dict(item)
            comments.append(c)

        return {
            "thread" : comments,
            "has_less" : response['has_less'],
            "has_more" : response['has_more'],
            "prev_offset" : response['prev_offset'],
            "next_offset" : response['next_offset']
        }



    def post_comment(self, target, body, comment_type="profile", commentid=""):

        """Post comment

        :param target: The target you want to post the comment to (username/deviation UUID/status UUID)
        :param body: The comment text
        :param comment_type: The type of entry you want to post your comment to
        :param commentid: The commentid you are replying to
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        if comment_type == "profile":
            response = self._req('/comments/post/profile/{}'.format(target), post_data={
                "body":body,
                "commentid":commentid
            })
        elif comment_type == "deviation":
            response = self._req('/comments/post/deviation/{}'.format(target), post_data={
                "body":body,
                "commentid":commentid
            })
        elif comment_type == "status":
            response = self._req('/comments/post/status/{}'.format(target), post_data={
                "body":body,
                "commentid":commentid
            })
        else:
            raise DeviantartError("Unknown comment type.")

        comment = Comment()
        comment.from_dict(response)

        return comment



    def get_messages(self, folderid="", stack=1, cursor=""):

        """Feed of all messages

        :param folderid: The folder to fetch messages from, defaults to inbox
        :param stack: True to use stacked mode, false to use flat mode
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/messages/feed', {
            'folderid' : folderid,
            'stack' : stack,
            'cursor' : cursor
        })

        messages = []

        for item in response['results']:

            m = Message()
            m.from_dict(item)

            messages.append(m)

        return {
            "results" : messages,
            "has_more" : response['has_more'],
            "cursor" : response['cursor']
        }



    def delete_message(self, messageid="", folderid="", stackid=""):

        """Delete a message or a message stack

        :param folderid: The folder to delete the message from, defaults to inbox
        :param messageid: The message to delete
        :param stackid: The stack to delete
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/messages/delete', post_data={
            'folderid' : folderid,
            'messageid' : messageid,
            'stackid' : stackid
        })

        return response



    def get_feedback(self, feedbacktype="comments", folderid="", stack=1, offset=0, limit=10):

        """Fetch feedback messages

        :param feedbacktype: Type of feedback messages to fetch (comments/replies/activity)
        :param folderid: The folder to fetch messages from, defaults to inbox
        :param stack: True to use stacked mode, false to use flat mode
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/messages/feedback', {
            'type' : feedbacktype,
            'folderid' : folderid,
            'stack' : stack,
            'offset' : offset,
            'limit' : limit
        })

        messages = []

        for item in response['results']:

            m = Message()
            m.from_dict(item)

            messages.append(m)

        return {
            "results" : messages,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_feedback_in_stack(self, stackid, offset=0, limit=10):

        """Fetch feedback messages in a stack

        :param stackid: Id of the stack
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/messages/feedback/{}'.format(stackid), {
            'offset' : offset,
            'limit' : limit
        })

        messages = []

        for item in response['results']:

            m = Message()
            m.from_dict(item)

            messages.append(m)

        return {
            "results" : messages,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_mentions(self, folderid="", stack=1, offset=0, limit=10):

        """Fetch mention messages

        :param folderid: The folder to fetch messages from, defaults to inbox
        :param stack: True to use stacked mode, false to use flat mode
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/messages/mentions', {
            'folderid' : folderid,
            'stack' : stack,
            'offset' : offset,
            'limit' : limit
        })

        messages = []

        for item in response['results']:

            m = Message()
            m.from_dict(item)

            messages.append(m)

        return {
            "results" : messages,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_mentions_in_stack(self, stackid, offset=0, limit=10):

        """Fetch mention messages in a stack

        :param stackid: Id of the stack
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/messages/mentions/{}'.format(stackid), {
            'offset' : offset,
            'limit' : limit
        })

        messages = []

        for item in response['results']:

            m = Message()
            m.from_dict(item)

            messages.append(m)

        return {
            "results" : messages,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_notes(self, folderid="", offset=0, limit=10):

        """Fetch notes

        :param folderid: The UUID of the folder to fetch notes from
        :param offset: the pagination offset
        :param limit: the pagination limit
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes', {
            'folderid' : folderid,
            'offset' : offset,
            'limit' : limit
        })

        notes = []

        for item in response['results']:
            n = {}

            n['noteid'] = item['noteid']
            n['ts'] = item['ts']
            n['unread'] = item['unread']
            n['starred'] = item['starred']
            n['sent'] = item['sent']
            n['subject'] = item['subject']
            n['preview'] = item['preview']
            n['body'] = item['body']
            n['user'] = User()
            n['user'].from_dict(item['user'])
            n['recipients'] = []

            for recipient_item in item['recipients']:
                u = User()
                u.from_dict(recipient_item)
                n['recipients'].append(u)

            notes.append(n)

        return {
            "results" : notes,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }



    def get_note(self, noteid):

        """Fetch a single note

        :param folderid: The UUID of the note
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/{}'.format(noteid))

        return response



    def send_note(self, to, subject="", body="", noetid=""):

        """Send a note

        :param to: The username(s) that this note is to
        :param subject: The subject of the note
        :param body: The body of the note
        :param noetid: The UUID of the note that is being responded to
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/send', post_data={
            'to[]' : to,
            'subject' : subject,
            'body' : body,
            'noetid' : noetid
        })

        sent_notes = []

        for item in response['results']:
            n = {}
            n['success'] = item['success']
            n['user'] = User()
            n['user'].from_dict(item['user'])

            sent_notes.append(n)

        return sent_notes



    def move_notes(self, noteids, folderid):

        """Move notes to a folder

        :param noteids: The noteids to move
        :param folderid: The folderid to move notes to
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/move', post_data={
            'noteids[]' : noteids,
            'folderid' : folderid
        })

        return response



    def delete_notes(self, noteids):

        """Delete a note or notes

        :param noteids: The noteids to delete
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/delete', post_data={
            'noteids[]' : noteids
        })

        return response



    def mark_notes(self, noteids, mark_as):

        """Mark notes

        :param noteids: The noteids to delete
        :param mark_as: Mark notes as (read/unread/starred/notstarred/spam)
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/mark', post_data={
            'noteids[]' : noteids,
            'mark_as' : mark_as
        })

        return response



    def get_notes_folders(self):

        """Fetch note folders"""

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/folders')

        return response['results']



    def create_notes_folder(self, title, parentid=""):

        """Create new folder

        :param title: The title of the folder to create
        :param parentid: The UUID of the parent folder
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/folders/create', post_data={
            'title' : title,
            'parentid' : parentid
        })

        return response



    def rename_notes_folder(self, title, folderid):

        """Rename a folder

        :param title: New title of the folder
        :param folderid: The UUID of the folder to rename
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/folders/rename/{}'.format(folderid), post_data={
            'title' : title
        })

        return response



    def delete_notes_folder(self, folderid):

        """Delete note folder

        :param folderid: The UUID of the folder to delete
        """

        if self.standard_grant_type is not "authorization_code":
            raise DeviantartError("Authentication through Authorization Code (Grant Type) is required in order to connect to this endpoint.")

        response = self._req('/notes/folders/remove/{}'.format(folderid))

        return response



    def _req(self, endpoint, get_data=dict(), post_data=dict()):

        """Helper method to make API calls

        :param endpoint: The endpoint to make the API call to
        :param get_data: data send through GET
        :param post_data: data send through POST
        """

        if get_data:
            request_parameter = "{}?{}".format(endpoint, urlencode(get_data))
        else:
            request_parameter = endpoint

        try:
            encdata = urlencode(post_data, True).encode('utf-8')
            response = self.oauth.request(request_parameter, data=encdata)
            self._checkResponseForErrors(response)
        except HTTPError as e:
            raise DeviantartError(e)

        return response



    def _checkResponseForErrors(self, response):

        """Checks response for API errors"""

        if 'error' in response:
            raise DeviantartError(response['error_description'])
