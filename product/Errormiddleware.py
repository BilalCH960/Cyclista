from django.shortcuts import render
import logging


class CustomErrorMiddleware:
    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return render(request, '404.html')