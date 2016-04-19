from django.views.decorators.http import require_POST


@require_POST
def fake_s3_upload(request):
    pass
