from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting
from urllib.parse import urljoin
from django.conf import settings

class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """
    Google Cloud Storage class that returns MEDIA_URL for files instead of 
    Google-generated URLs.
    """
    bucket_name = setting("GS_BUCKET_NAME")

    def url(self, name):
        """
        Returns the correct MEDIA_URL instead of the default Google Storage URL.
        """
        return urljoin(settings.MEDIA_URL, name)



