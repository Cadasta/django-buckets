from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.translation import ugettext as _

from buckets.utils import get_signed_url
from buckets.exceptions import InvalidPayload


def validate_payload(payload):
    errors = {}
    AWS_METHODS = ['get', 'put', 'delete']

    client_method = payload.get('client_method', None)
    if not client_method:
        errors['client_method'] = _("'client_method' is required")
    else:
        client_methods = [m + '_object' for m in AWS_METHODS]
        if client_method not in client_methods:
            one_of = ", ".join(client_methods)
            errors['client_method'] = _(
                "'client_method' must be one of {}".format(one_of))

    http_method = payload.get('http_method', None)
    if not http_method:
        errors['http_method'] = _("'http_method' is required")
    else:
        if http_method.lower() not in AWS_METHODS:
            one_of = ", ".join(AWS_METHODS)
            errors['http_method'] = _(
                "'http_method' must be one of {}".format(one_of))

    if errors:
        raise InvalidPayload(errors=errors)


@require_POST
def signed_url(request):
    try:
        validate_payload(request.POST)
        response = {
            'signed_url': get_signed_url(**request.POST)
        }
        status = 200
    except InvalidPayload as e:
        response = e.errors
        status = 400

    return JsonResponse(response, status=status)
