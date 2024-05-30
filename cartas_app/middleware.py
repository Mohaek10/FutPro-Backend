from http import HTTPStatus

from django.http import JsonResponse


class JSONErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.status_code_description = {
            v.value: v.description for v in HTTPStatus
        }

    def __call__(self, request):
        response = self.get_response(request)

        # If the content_type isn't 'application/json', do nothing.
        if not request.content_type == "application/json":
            return response

        # If there's no error, let Django and DRF's default views deal
        # with it.
        status_code = response.status_code
        if (
                not HTTPStatus.BAD_REQUEST
                    < status_code
                    <= HTTPStatus.INTERNAL_SERVER_ERROR
        ):
            return response

        # Return a JSON error response if any of 403, 404, or 500 occurs.
        r = JsonResponse(
            {
                "error": {
                    "status_code": status_code,
                    "message": self.status_code_description[status_code],
                    "detail": {"url": request.get_full_path()},
                }
            },
        )
        r.status_code = response.status_code
        return r
