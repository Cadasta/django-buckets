from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.http import HttpResponse


@require_POST
def fake_s3_upload(request):
    file = request.POST.get('file')
    path = default_storage.save('uploads/' + file.name, file)

    response = (
        '<Location>{}</Location>'.format(path)
    )
    print(response)

    return HttpResponse(response, content_type='application/xml')
