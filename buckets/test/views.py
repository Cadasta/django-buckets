from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from buckets.test.mocks import ensure_dirs


@require_POST
def fake_s3_upload(request):
    ensure_dirs()

    file = request.POST.get('file')
    file = request.FILES.get('file')
    path = default_storage.save('uploads/' + file.name, file)

    response = (
        '<Location>{}</Location>'.format(path)
    )

    return HttpResponse(response, status=201, content_type='application/xml')
