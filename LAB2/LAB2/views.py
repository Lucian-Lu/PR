from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete(request, search_string):
    if request.method == 'DELETE':
        print('Printing now: ' + str(search_string))
    else:
        return HttpResponse("Invalid request method.")

@csrf_exempt
def put(request, search_string):
    if request.method == 'PUT':
        pass
    else:
        return HttpResponse("Invalid request method.")

@csrf_exempt
def get(request, search_string):
    if request.method == 'GET':
        pass
    else:
        return HttpResponse("Invalid request method.")