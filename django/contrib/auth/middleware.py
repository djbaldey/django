from django.conf import settings
from django.contrib import auth
from django.contrib.auth import load_backend, logout
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.functional import SimpleLazyObject

UNIQUE_SESSION_LIMIT_SECONDS = getattr(settings, 'UNIQUE_SESSION_LIMIT_SECONDS', 0)
UNIQUE_SESSION_TOKEN_LIMIT_SECONDS = getattr(settings, 'UNIQUE_SESSION_TOKEN_LIMIT_SECONDS', 300)

def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = auth.get_user(request)
    return request._cached_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_user(request))


class SessionAuthenticationMiddleware(object):
    """
    Formerly, a middleware for invalidating a user's sessions that don't
    correspond to the user's current session authentication hash. However, it
    caused the "Vary: Cookie" header on all responses.

    Now a backwards compatibility shim that enables session verification in
    auth.get_user() if this middleware is in MIDDLEWARE_CLASSES.
    """
    def process_request(self, request):
        pass


class RemoteUserMiddleware(object):
    """
    Middleware for utilizing Web-server-provided authentication.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``REMOTE_USER`` request header.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    The header used is configurable and defaults to ``REMOTE_USER``.  Subclass
    this class and change the ``header`` attribute if you need to use a
    different header.
    """

    # Name of request header to grab username from.  This will be the key as
    # used in the request.META dictionary, i.e. the normalization of headers to
    # all uppercase and the addition of "HTTP_" prefix apply.
    header = "REMOTE_USER"

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if request.user.is_authenticated():
                self._remove_invalid_user(request)
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.get_username() == self.clean_username(username, request):
                return
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)

    def clean_username(self, username, request):
        """
        Allows the backend to clean the username, if the backend defines a
        clean_username method.
        """
        backend_str = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_str)
        try:
            username = backend.clean_username(username)
        except AttributeError:  # Backend has no clean_username method.
            pass
        return username

    def _remove_invalid_user(self, request):
        """
        Removes the current authenticated user in the request which is invalid
        but only if the user is authenticated via the RemoteUserBackend.
        """
        try:
            stored_backend = load_backend(request.session.get(auth.BACKEND_SESSION_KEY, ''))
        except ImportError:
            # backend failed to load
            auth.logout(request)
        else:
            if isinstance(stored_backend, RemoteUserBackend):
                auth.logout(request)


class SessionCollector(object):
    """
    Collector of sessions for user
    """

    def __init__(self):
        self._sessions = {}

    def register(self, request):
        """
        Register session by key with creation time
        """
        if not request.session.session_key in self._sessions.keys():
            self._sessions[request.session.session_key] = (timezone.now(), request)

    @property
    def opened(self):
        """
        Return the number of sessions after a flush
        """
        self.flush()
        return len(self._sessions)

    def flush(self, session_limit=UNIQUE_SESSION_LIMIT_SECONDS):
        """
        Flush the cache of opened sessions and close expired session
        """
        now = timezone.now()

        for session_key, values in self._sessions.items():
            creation_time, request = values
            delta = now - creation_time
            if session_limit and delta.seconds >= session_limit:
                logout(request)
            if not request.session.exists(session_key):
                del self._sessions[session_key]

    def set_unique(self):
        """
        Choose the current session, and close the others
        """
        current_session_key = self.get_current_session_key()

        for session_key, values in self._sessions.items():
            if session_key == current_session_key:
                creation_time, request = values
                logout(request)
                del self._sessions[session_key]

    def get_current_session_key(self, session_token_limit=UNIQUE_SESSION_TOKEN_LIMIT_SECONDS):
        """
        Return the current session key, selected by his creation time
        and his limit before destruction, we suppose that we always
        have 2 items in sessions
        """
        sessions = self._sessions.items()[:2]

        if sessions[0][1][0] > sessions[1][1][0]:
            most_recent_session = sessions[0]
            most_oldest_session = sessions[1]
        else:
            most_recent_session = sessions[1]
            most_oldest_session = sessions[0]

        delta_oldest = timezone.now() - most_oldest_session[1][0]
        if session_token_limit and delta_oldest.seconds < session_token_limit:
            return most_oldest_session[0]
        return most_recent_session[0]


class UniqueSessionMiddleware(object):

    def __init__(self):
        """
        Amorcing the datas
        """
        self._user_sessions = {}

    def process_request(self, request):
        """
        Attacking the view with the middleware
        """
        return self.check_sessions(request)

    def check_sessions(self, request):
        """
        Check for unique sessions
        """
        if request.user.is_authenticated():
            user_sessions = self.get_sessions(request.user.username)
            user_sessions.register(request)

            if user_sessions.opened > 1:
                user_sessions.set_unique()
        else:
            return None

    def get_sessions(self, key):
        """
        Return user sessions from his username as key
        """
        self._user_sessions.setdefault(key, SessionCollector())
        return self._user_sessions.get(key)

