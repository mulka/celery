
class Loader(object):

    def __init__(self):
        self._conf_cache = None

    def read_configuration(self):
        from django.conf import settings
        return settings

    def on_task_init(self, task_id, task):
        # See: http://groups.google.com/group/django-users/browse_thread/
        #       thread/78200863d0c07c6d/38402e76cf3233e8?hl=en&lnk=gst&
        #       q=multiprocessing#38402e76cf3233e8
        from django.db import connection
        connection.close()

        # Reset cache connection only if using memcached/libmemcached
        from django.core import cache
        # XXX At Opera we use a custom memcached backend that uses libmemcached
        # instead of libmemcache (cmemcache). Should find a better solution for
        # this, but for now "memcached" should probably be unique enough of a
        # string to not make problems.
        cache_backend = cache.settings.CACHE_BACKEND
        if hasattr(cache, "parse_backend_uri"):
            cache_scheme = cache.parse_backend_uri(cache_backend)[0]
        else:
            # Django <= 1.0.2
            cache_scheme = cache_backend.split(":", 1)[0]
        if "memcached" in cache_scheme:
            cache.cache.close()

    def on_worker_init(self):
        from celery.discovery import autodiscover
        autodiscover()

    @property
    def conf(self):
        if not self._conf_cache:
            self._conf_cache = self.read_configuration()
        return self._conf_cache

