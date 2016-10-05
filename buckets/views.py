from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext as _
from django.core.files.storage import default_storage

from buckets.exceptions import InvalidPayload, S3ResourceNotFound


def validate_payload(payload):
    errors = {}

    key = payload.get('key', None)
    if not key:
        errors['key'] = _("'key' is required")

    if errors:
        raise InvalidPayload(errors=errors)


@require_POST
def signed_url(request):
    if not hasattr(default_storage, 'get_signed_url'):
        response = {'error': 'Not found'}
        status = 404
    else:
        try:
            validate_payload(request.POST)
            response = default_storage.get_signed_url(key=request.POST['key'])
            status = 200
        except InvalidPayload as e:
            response = e.errors
            status = 400

    return JsonResponse(response, status=status)


@require_POST
def delete_resource(request):
    try:
        default_storage.delete(request.POST['key'])
        return HttpResponse('', status=204)
    except S3ResourceNotFound:
        return JsonResponse({'error': _("S3 resource does not exist.")},
                            status=400)
