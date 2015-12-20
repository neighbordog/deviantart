"""
    deviantart.comment
    ^^^^^^^^^^^^^^^^^^
    
    Data model of the comment object
    
    :copyright: (c) 2015 by Kevin Eichhorn
"""

from .user import User

class Comment(object):
    
    def __init__(self):
        self.commentid = None
        self.parentid = None
        self.posted = None
        self.replies = None
        self.hidden = None
        self.body = None
        self.user = None
    
    def from_dict(self, c):
        
        if 'commentid' in c:
            self.commentid = c['commentid']
            
        if 'parentid' in c:
            self.parentid = c['parentid']
            
        if 'posted' in c:
            self.posted = c['posted']
            
        if 'replies' in c:
            self.replies = c['replies']
            
        if 'hidden' in c:
            self.hidden = c['hidden']
            
        if 'body' in c:
            self.body = c['body']
            
        if 'user' in c:
            self.user = User()
            self.user.from_dict(c['user'])
    
    def __repr__(self):        
        return self.commentid