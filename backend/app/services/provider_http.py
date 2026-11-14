from urllib.request import HTTPRedirectHandler, build_opener
from urllib.error import HTTPError


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        # Never forward provider credentials to an unexpected redirect target.
        raise HTTPError(request.full_url, code, 'Provider redirect rejected', headers, fp)


def open_request(request, timeout=20):
    return build_opener(NoRedirect()).open(request, timeout=timeout)
