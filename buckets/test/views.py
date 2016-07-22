import os
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings


@require_POST
def fake_s3_upload(request):
    key = request.POST.get('key')

    if '/' in key:
        path = os.path.join(settings.MEDIA_ROOT,
                            's3/uploads', key[:key.rfind('/')])
        if not os.path.exists(path):
            os.makedirs(path)

    file = request.FILES.get('file')
    default_storage.save(key, file.read())

    return HttpResponse('', status=204)
