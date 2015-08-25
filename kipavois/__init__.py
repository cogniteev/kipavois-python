
import base64

from flask import (
    Blueprint,
    Response,
    request,
    stream_with_context,
)
import requests

__all__ = ['flask_blueprint', '__version__']

KIBANA_DEFAULT_URL = 'http://kibana:5601'
MONITOR_SESSION = requests.Session()
CHUNK_SIZE = 16 * 1024
ALL_METHODS = [
    'GET',
    'HEAD',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
]
__version__ = (0, 1, 1)


def chunked_response_iterator(resp, native_chunk_support, line_based, chunk_size):
    """
    Return stream with chunked encoding if native_chunk_support is True.
    """
    if line_based:
        for chunk in resp.iter_lines(1):
            chunk += '\n'
            if native_chunk_support:
                yield chunk
            else:
                yield hex(len(chunk))[2:] + '\r\n' + chunk + '\r\n'
        if not native_chunk_support:
            yield '0\r\n\r\n'
    else:
        for chunk in resp.iter_content(chunk_size):
            if native_chunk_support:
                yield chunk
            else:
                yield hex(len(chunk))[2:] + '\r\n' + chunk + '\r\n'
        if not native_chunk_support:
            yield '0\r\n\r\n'


def flask_blueprint(kibana_addr=KIBANA_DEFAULT_URL, get_user=None,
                    get_referer=None, decorators=None,
                    response_chunk_size=CHUNK_SIZE):
    pikavois_blueprint = Blueprint('pikavois', __name__)

    try:
        iter(decorators):
    except TypeError:
        decorators = [decorators]

    @pikavois_blueprint.route('/', defaults={'url': ''}, methods=ALL_METHODS)
    @pikavois_blueprint.route('/<path:url>', methods=ALL_METHODS)
    def monitor_proxy(url):
        params = dict(request.args.items())
        headers = dict(request.headers.items())
        user = get_user()
        if user:
            headers.update({
                'x-kibana-user': user,
            })
        headers.update({
            'Referer': get_referer() + '/' + url
        })
        addr = kibana_addr + '/' + url
        req =requests.request(
            request.method,
            addr,
            stream=True,
            headers=headers,
            params=params,
            data=request.data
        )
        # content_type = req.headers.get('Content-type', '')
        # line_based = content_type.startswith(('text/', 'application/json'))
        # gunicorn/werkzeug supports chunked encoding, no need to
        # encode it manually
        # native_chunk_support = (
        #     'gunicorn' in request.environ['SERVER_SOFTWARE'] or
        #     'Werkzeug' in request.environ['SERVER_SOFTWARE']
        # )
        headers = dict(req.headers)
        if headers.get('transfer-encoding', None) == 'chunked':
            stream_reader = chunked_response_iterator(
                req, True, False, response_chunk_size
            )
            # do not pass the gzip header if provided by kibana
            # because content is uncompressed when reading the stream.
            headers.pop('content-encoding', None)
        else:
            stream_reader = stream_with_context(req.iter_content())
        return Response(stream_reader, headers=headers,
                        direct_passthrough=True, status=req.status_code)
    decorators.append(pikavois_blueprint)
    return reduce(lambda f1, f2: f1(f2), decorators)
