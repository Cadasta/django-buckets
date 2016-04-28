import os
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings

from buckets.test.utils import ensure_dirs


@require_POST
def fake_s3_upload(request):
    ensure_dirs()
    key = request.POST.get('key')

    path = os.path.join(settings.MEDIA_ROOT,
                        's3/uploads', key[:key.rfind('/')])
    if not os.path.exists(path):
        os.makedirs(path)

    file = request.FILES.get('file')
    default_storage.save(key, file)

    return HttpResponse('', status=204)
