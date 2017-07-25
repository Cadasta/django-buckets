from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from ..defaults import MAX_FILE_SIZE
from .errors import EXCEED_MAX_SIZE


@csrf_exempt
@require_POST
def fake_s3_upload(request):
    key = request.POST.get('key')

    file = request.FILES.get('file')

    if file.size > settings.AWS.get('MAX_FILE_SIZE', MAX_FILE_SIZE):
        return HttpResponse(EXCEED_MAX_SIZE, status=400)

    default_storage.save(key, file.read())
    return HttpResponse('', status=204)
