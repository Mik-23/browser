from rest_framework import generics
from rest_framework.response import Response
from .services import voice_search


class VoiceView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        audio = request.data
        file = audio.get('file')
        print(type(file))
        data = voice_search(file)
        print('Файл записался')
        return Response({"data": data})