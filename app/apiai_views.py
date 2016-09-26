
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random
import apiai

ai=apiai.ApiAI('0ff73c1acdaa4de09e64c512dc1bbba5')
res = requests.get('http://allecarte.azurewebsites.net/FoodSearch/GetFoods').json()

def home(request):
   return HttpResponse("I am in the home page")

@csrf_exempt
def apiai_webhook(request):
   if request.method=='POST':
       body_unicode=request.body.decode('utf-8')
       request_body=json.loads(body_unicode)

       print(request_body)

       if 'city' in request_body['result']['parameters']:
           city=request_body['result']['parameters']['city']
           print(city)
           res=sendCarousel(city)
           api_response=JsonResponse(res)
           api_response['Content-Type']="application/json"
           print(api_response)
           return api_response

   else:
       return HttpResponse("This method is not allowed at all")

def sendCarousel(city):
    data=generateSamples()
    all_elements=[]
    for element in data:
        element_title=element['title']
        element_redirect_url='https://www.facebook.com'
        postback_button ={
            "type": "postback",
            "title":"Show Restaurant",
            "payload":element_title
        }
        web_button = elements.WebUrlButton(
            title='Show More',
            url='https://www.facebook.com'
        )

        buttons=[postback_button, web_button]

        current_element={
            "title": element['title'],
            "image_url": element['image_url'],
            "subtitle": element['subtitle'],
            "item_url": element['item_url'],
            "buttons": buttons
        }

        all_elements.append(current_element)

    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements":all_elements
            }
        }
    }


    return{
        'data': {'facebook': facebook_message}
    }


def sendDirection(hotel):

    element=''
    for i in range(len(res)):
        if res[i]['Name']==hotel:
            element=getResults(res[i])

    if element is not '':
        element_title = element['title']
        element_subtitle = element['subtitle']
        element_item_url = "https://www.google.com.tr/maps/place/WeDoBurgers/@56.1541691,10.2058315,15z/data=!4m5!3m4!1s0x0:0x3ac9e66233791bb2!8m2!3d56.1541691!4d10.2058315"
        element_image_url = "http://www.techmerry.com/wp-content/uploads/thumbs_dir/Implement-GPS-data-for-your-Google-MAP-69w74hiswbk73ywi6js6jord0ubncxd6zkf2spdwpiy.gif"
        web_button={
            'type':"web_url",
            'title':"Get Directions",
            'url':"https://www.google.com.tr/maps/place/WeDoBurgers/@56.1541691,10.2058315,15z/data=!4m5!3m4!1s0x0:0x3ac9e66233791bb2!8m2!3d56.1541691!4d10.2058315"
        }


        buttons = [web_button]
        current_element ={
            'title': element_title,
            'item_url':element_item_url,
            'image_url':element_image_url,
            'subtitle':element_subtitle,
            'buttons':buttons
        }
        current_elements=[current_element]

        facebook_message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": current_elements
                }
            }
        }

        return{
            'data': {'facebook': facebook_message}
        }

    else:
        print ("This hotel does not exist")

def generateSamples():

    samples=[]
    numbers=random.sample([i for i in range(len(res)-1)], 6)
    for number in numbers:
        samples.append(getResults(res[number]))

    return samples



def getResults(sample):
    results={}
    results['title']=sample['Name']

    if(sample['RestaurantInfo'][0]['Address'] and sample['RestaurantInfo'][0]['Phone']):
       results['subtitle'] = sample['RestaurantInfo'][0]['Address'] + ", " + sample['RestaurantInfo'][0]['Phone']
    else:
        results['subtitle']="No hotel Info"



    if sample['BaseImageURL']==None:
        results['image_url'] = 'http://www.isabegovhotel.com/images/HOTEL/hotel/hotel/IMG_7135.jpg'
    else:
        results['image_url'] = 'http://allecarte.azurewebsites.net/' + str(sample['BaseImageURL'])




    results['item_url']=sample['RestaurantInfo'][0]['WebPage']
    results['button_url'] = sample['RestaurantInfo'][0]['WebPage']

    if results['item_url']==None:
        results['item_url']='http://allecarte.azurewebsites.net'
    if results['button_url'] ==None:
        results['button_url']='http://allecarte.azurewebsites.net'

    results['button_title']='Hotel Website'

    return results
