# -*- coding: utf-8 -*-

"""Common interface for upload pic services"""
#
# Author: Andrea Stagi (4ndreaSt4gi)
# Author: Wil Alvarez (aka Satanas)
# 2010-08-01

import os
import httplib
import urllib2
import logging

from libturpial.api.interfaces.service import GenericService
from libturpial.api.interfaces.service import ServiceResponse
from libturpial.api.interfaces.http import TurpialHTTPRequest

try:
    import mimetypes
    MIME_FLAG = True
except ImportError:
    MIME_FLAG = False


class UploadService(GenericService):
    def __init__(self, host, base_url, provider):
        self.log = logging.getLogger('Service')
        self.host = host
        self.base_url = base_url
        self.provider = provider

    def _upload_pic(self, account, fields, files, custom_headers={}):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
            uploaded as files
        Return the server's response page.
        """
        content_type, body = self._encode_multipart_formdata(fields, files)
        h = httplib.HTTPConnection(self.host)

        headers = {
            'User-Agent': 'Turpial',
            'Content-Type': content_type
        }

        headers = dict(headers.items() + custom_headers.items())

        httpreq = TurpialHTTPRequest(method='GET', uri=self.provider)
        httpresp = account.auth_http_request(httpreq, {})
        auth_head = httpresp.headers['Authorization']
        auth_head = auth_head.replace('OAuth realm=""',
                                      'OAuth realm="http://api.twitter.com/"')

        headers['X-Verify-Credentials-Authorization'] = auth_head
        headers['X-Auth-Service-Provider'] = self.provider

        h.request('POST', self.base_url, body, headers)
        res = h.getresponse()
        return res.read()

    def _open_file(self, filepath):
        _file = open(filepath, 'r')
        imgbin = _file.read()
        _file.close()
        return imgbin

    def _error_opening_file(self, filepath):
        self.log.debug("Error: El archivo %s no existe" % filepath)
        return ServiceResponse(err=True,
                               err_msg=_('Select something to uploading'))

    def _encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
        uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self._get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def _get_content_type(self, filename):
        """Get the image content type"""
        if MIME_FLAG:
            return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        else:
            return 'image/jpg'

    def _get_pic_name(self, filepath):
        return os.path.split(filepath)[1]
