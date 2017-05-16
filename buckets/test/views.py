from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse


@csrf_exempt
@require_POST
def fake_s3_upload(request):
    key = request.POST.get('key')

    file = request.FILES.get('file')
    default_storage.save(key, file.read())

    return HttpResponse('', status=204)
