from django.views.generic import TemplateView
from .jsonrpc_client import call_remote_method
import pprint


class CallAPIView(TemplateView):
    template_name = "call_api.html"

    def post(self, request):
        method_name = request.POST.get("method_name")
        params = request.POST.get("params")
        # Вызов удаленного метода API
        result = pprint.pformat(call_remote_method(method_name, params))
        return self.render_to_response({"result": result})
