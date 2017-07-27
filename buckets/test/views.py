from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from .errors import EXCEED_MAX_SIZE


@csrf_exempt
@require_POST
def fake_s3_upload(request):
    key = request.POST.get('key')

    file = request.FILES.get('file')

    max_file_size = settings.AWS.get('MAX_FILE_SIZE')
    if max_file_size and file.size > max_file_size:
        msg = EXCEED_MAX_SIZE.format(max_size=max_file_size,
                                     proposed_size=file.size)
        return HttpResponse(msg, status=400)

    default_storage.save(key, file.read())
    return HttpResponse('', status=204)
