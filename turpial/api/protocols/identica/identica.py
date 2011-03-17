# -*- coding: utf-8 -*-

""" Identi.ca implementation for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Jun 08, 2010

from turpial.api.common import UpdateType, STATUSPP
from turpial.api.models.status import Status
from turpial.api.models.profile import Profile
from turpial.api.interfaces.protocol import Protocol


class Main(Protocol):
    def __init__(self, username, account_id):
        p_name = 'Identi.ca(%s)' % username
        Protocol.__init__(self, account_id, p_name, 
            'http://identi.ca/api', 
            'http://identi.ca/api', 
            'http://identi.ca/tag/', 
            'http://identi.ca/group',
            'http://identi.ca')
        
        self.uname = None
        self.account_id = account_id
    
    def json_to_profile(self, response):
        if isinstance(response, list):
            profiles = []
            for pf in response:
                profile = self.json_to_status(json_to_profile)
                profiles.append(profile)
            return profiles
        else:
            profile = Profile()
            profile.id_ = response['id']
            profile.fullname = response['name']
            profile.username = response['screen_name']
            profile.avatar = response['profile_image_url']
            profile.location = response['location']
            profile.url = response['url']
            profile.bio = response['description']
            profile.following = response['following']
            profile.followers_count = response['followers_count']
            profile.friends_count = response['friends_count']
            profile.statuses_count = response['statuses_count']
            if response.has_key('status'):
                profile.last_update = response['status']['text']
                profile.last_update_id = response['status']['id']
            profile.link_color = ('#' + response['profile_link_color']) or Profile.DEFAULT_LINK_COLOR
            return profile
    
    def json_to_status(self, response, _type=UpdateType.STD):
        if isinstance(response, list):
            statuses = []
            for resp in response:
                if not resp:
                    continue
                status = self.json_to_status(resp, _type)
                #if status.retweet_by:
                #    users = self.__get_retweet_users(status._id)
                #    status.retweet_by = users
                statuses.append(status)
            return statuses
        else:
            retweet_by = None
            if response.has_key('retweeted_status'):
                retweet_by = response['user']['screen_name']
                tweet = response['retweeted_status']
            else:
                tweet = response
            
            if tweet.has_key('user'):
                username = tweet['user']['screen_name']
                avatar = tweet['user']['profile_image_url']
            elif tweet.has_key('sender'):
                username = tweet['sender']['screen_name']
                avatar = tweet['sender']['profile_image_url']
            elif tweet.has_key('from_user'):
                username = tweet['from_user']
                avatar = tweet['profile_image_url']
            
            in_reply_to_id = None
            in_reply_to_user = None
            if tweet.has_key('in_reply_to_status_id') and \
               tweet['in_reply_to_status_id']:
                in_reply_to_id = tweet['in_reply_to_status_id']
                in_reply_to_user = tweet['in_reply_to_screen_name']
                
            fav = False
            if tweet.has_key('favorited'):
                fav = tweet['favorited']
            
            source = None
            if tweet.has_key('source'):
                source = tweet['source']
            
            own = True if (username.lower() == self.uname.lower()) else False
            
            status = Status()
            status.id_ = str(tweet['id'])
            status.username = username
            status.avatar = avatar
            status.source = source
            status.text = tweet['text']
            status.in_reply_to_id = in_reply_to_id
            status.in_reply_to_user = in_reply_to_user
            status.is_favorite = fav
            status.reposted_by = retweet_by
            status.datetime = self.get_str_time(tweet['created_at'])
            status.timestamp = self.get_int_time(tweet['created_at'])
            status._type = _type
            status.account_id = self.account_id
            status.is_own = own
            return status
    
    def auth(self, username, password):
        ''' Start Auth '''
        self.log.debug('Starting Basic Auth')
        self.auth_args = {'username': username, 'password': password}
        rtn = self.request('/account/verify_credentials')
        profile = self.json_to_profile(rtn)
        self.uname = profile.username
        return profile
        
    def get_timeline(self, count=STATUSPP):
        self.log.debug('Getting timeline')
        rtn = self.request('/statuses/home_timeline', {'count': count})
        return self.json_to_status(rtn)
        
    def get_replies(self, count=STATUSPP):
        self.log.debug('Getting replies')
        rtn = self.request('/statuses/mentions', {'count': count})
        return self.json_to_status(rtn)
        
    def get_directs(self, count=STATUSPP):
        self.log.debug('Getting directs')
        rtn = self.request('/direct_messages', {'count': count / 2})
        directs = self.json_to_status(rtn, _type=UpdateType.DM)
        rtn2 = self.request('/direct_messages/sent', {'count': count / 2})
        directs += self.json_to_status(rtn2, _type=UpdateType.DM)
        return directs
            
    def get_sent(self, count=STATUSPP):
        self.log.debug('Getting my statuses')
        rtn = self.request('/statuses/user_timeline', {'count': count})
        return self.json_to_status(rtn)
        
    def get_favorites(self):
        self.log.debug('Getting favorites')
        rtn = self.request('/favorites')
        return self.json_to_status(rtn)
        
    def update_status(self, text, in_reply_id=None):
        self.log.debug(u'Updating status: %s' % text)
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        
        rtn = self.request('/statuses/update', args)
        return self.json_to_status(rtn)