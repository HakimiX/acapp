"""
The python modules used in this code are:
  messengerbot-> A python module for handling facebook messenger bots
  apiai-> a python sdk for handling api.ai natural language processing platform
  requests- > a python module for handling web requests programmatically
  json-> a python module for handling json files

  django-> a python webframework is used to create a webhook for receiving and sending data to the the bot
"""
#import django modules
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

#import python modules

import json
from messengerbot import MessengerClient, messages, attachments, templates, elements
import requests
import random
import apiai


#api.ai

ai=apiai.ApiAI('0ff73c1acdaa4de09e64c512dc1bbba5')
client=apiai.ApiAI('0ff73c1acdaa4de09e64c512dc1bbba5')


#getting data from  demoac.azurewebsites.net/FoodSearch/GetFoods

res = requests.get('http://allecarte.azurewebsites.net/FoodSearch/GetFoods').json()

#python module to send messages and media to facebook.

messenger=MessengerClient('EAACpqvXnT7wBAJiLE2V7l0cgCxGDZCr4MG3Uwr5xC00845oCYqNkSoDep1hCs71a2n9OJMQ2mChDlQkFq9o3iNCq81el2mCZBZAFW5YMLwEksejDo0j5DwDXO1D67Nyng1ZBTnwXpqfifVhp6qWT5EAVuj0jHkDLIb7OvhVKF3GUbfnF9WpB')

# a list of greeetings

greeetings=['Hey', 'hey', 'hi','Hi', 'Hello', 'hello','Whats up']
chile=['chile','vegan in chile', 'vegan in Chile','Vegan in Chile','Vegan in chile','Chile','Santiago', 'santiago']
finish=['bye', 'Bye', 'Thank you', 'thank you', 'Okay', 'okay','ok','Ok','alright','Alright','see you','See you']

#cities=['copenhagen', 'Copenhagen', 'Aalborg', 'aalborg', 'Mimice', 'mimice', 'Dunakeszi', 'dunakeszi', 'Aarhus', 'aarhus', 'København', 'københavn', 'Budapest', 'budapest']


def home(request):
   return HttpResponse("I am in the home page")


#this function defines the webhook

@csrf_exempt
def webhook(request):

    #verify webhook for use on facebook messenger
    if request.method=='GET':
        if request.GET['hub.mode']=='subscribe' and request.GET['hub.verify_token']=='application_programming_interface':
            print("Verifying webhook")
            return HttpResponse(request.GET['hub.challenge'])
        else:
            print("verification failed")
            return HttpResponse("could not be verified")

    #Handle data posted from facebook messenger

    elif request.method=='POST':
        request_body=request.body.decode('utf-8')
        request_body=json.loads(request_body)

        print(request_body)

        messagingEvent=request_body['entry'][0]['messaging']
        recipient_id=messagingEvent[0]['sender']['id']

        print (recipient_id)

        recipient=messages.Recipient(recipient_id=recipient_id)

        if 'message' in  messagingEvent[0]:
            print('received a message')
            message=messagingEvent[0]['message']['text']

            if message in greeetings:
                sendWelcome(recipient)
            if message in chile:
                sendChile(recipient)
            if message in finish:
                sendMessage(recipient,
                            'I hope that i could help you! Remember that you have a choice! See you :)')
            else:
                call_apiai(message, recipient)

        elif 'postback' in messagingEvent[0]:
            hotel=messagingEvent[0]['postback']['payload']
            sendDirection(recipient, hotel)
        return JsonResponse(request_body)


#This functions calls api.ai

def call_apiai(mes, recipient):
    request=ai.text_request()
    request.query=mes
    data=''
    response=request.getresponse().read()

    result=json.loads(response.decode('utf-8'))

    print(result)

    parameters=result['result']['parameters']
    print(parameters)

    #this part handles data from api.ai to determine whether a user asked for a city, foodtype or both


    if 'City' in parameters and 'foodtype' in parameters:
        if parameters['City'] is not '' and parameters['foodtype'] is not '':
            foodtype = parameters['foodtype']
            food = foodtype.split(' ')
            food = ' '.join(i.capitalize() for i in food)
            data = generateFoodSamples(food)

        elif parameters['City'] is not '' and parameters['foodtype'] == '':
            sendMessage(recipient,
                        'You did not enter a foodtype :(. But here are some general results!')
            data = generateSamples()

        elif parameters['City'] == '' and parameters['foodtype'] is not '':
            sendMessage(recipient,
                        'Unfortunately, there are no matches for your criteria yet. :( Try around Copenhagen and Aalborg.')

    if data is '' or len(data)==0:
        sendMessage(recipient, 'Please enter a food type in a city!')
        return
    sendCarousel(recipient, data)

#this function sends a text message
def sendMessage(recipient, msg):
    message=messages.Message(text=msg)
    request=messages.MessageRequest(recipient, message)
    messenger.send(request)


#this function sends a welcome
def sendWelcome(recipient):
    msg="Welcome to Alle Carte! My name is Liam and I will help you find the perfect meal for you today! How can I help you?"
    message1=messages.Message(text=msg)
    request=messages.MessageRequest(recipient, message1)
    messenger.send(request)


#Chile & Santiago easter egg - demo demo
def sendChile(recipient):
    msg="Unfortunately, I cannot provide information about meals in Chile at the moment :(. From 2017 February I will hopefully know more about that location in first hand :) Try and search for meals in Aalborg or Copenhagen, so you can get a sneak peak to what I will be capable of!"
    message1=messages.Message(text=msg)
    request=messages.MessageRequest(recipient, message1)
    messenger.send(request)


#this function sends a Carousel to  facebook

def sendCarousel(recipient, data):

    all_elements=[]
    for element in data:
        element_title=element['title']
        element_subtitle=element['subtitle']
        element_item_url=element['item_url']
        element_image_url=element['image_url']
        element_redirect_url='https://www.facebook.com'

        postback_button = elements.PostbackButton(
            title='Show Restaurant',
            payload=element_title
        )

        web_button = elements.WebUrlButton(
            title='Show More',
            url='https://www.facebook.com'
        )

        buttons=[postback_button, web_button]
        element_buttons=buttons

        current_element=elements.Element(
            title=element_title,
            item_url=element_item_url,
            image_url=element_image_url,
            subtitle=element_subtitle,
            buttons=element_buttons
        )

        all_elements.append(current_element)

    template=templates.GenericTemplate(all_elements)
    attachment=attachments.TemplateAttachment(template=template)

    message=messages.Message(attachment=attachment)
    request=messages.MessageRequest(recipient, message)
    messenger.send(request)


#this function sends a direction template

def sendDirection(recipient, hotel):

    element=''
    for i in range(len(res)):
        if res[i]['Name']==hotel:
            element=getResults(res[i])

    if element is not '':
        element_title = element['title']
        element_subtitle = element['subtitle']
        element_item_url = 'https://www.google.com.tr/maps/place/WeDoBurgers/@56.1541691,10.2058315,15z/data=!4m5!3m4!1s0x0:0x3ac9e66233791bb2!8m2!3d56.1541691!4d10.2058315'
        element_image_url = 'http://www.techmerry.com/wp-content/uploads/thumbs_dir/Implement-GPS-data-for-your-Google-MAP-69w74hiswbk73ywi6js6jord0ubncxd6zkf2spdwpiy.gif'
        web_button = elements.WebUrlButton(
            title='Get Directions',
            url='https://www.google.com.tr/maps/place/WeDoBurgers/@56.1541691,10.2058315,15z/data=!4m5!3m4!1s0x0:0x3ac9e66233791bb2!8m2!3d56.1541691!4d10.2058315'
        )


        buttons = [web_button]
        current_element = elements.Element(
            title=element_title,
            item_url=element_item_url,
            image_url=element_image_url,
            subtitle=element_subtitle,
            buttons=buttons
        )
        current_elements=[current_element]

        template = templates.GenericTemplate(current_elements)
        attachment = attachments.TemplateAttachment(template=template)

        message = messages.Message(attachment=attachment)
        request = messages.MessageRequest(recipient, message)
        messenger.send(request)
    else:
        print ("This hotel does not exist")

#this function  generates six random samples from the data

def generateSamples():

    samples=[]
    numbers=random.sample([i for i in range(len(res)-1)], 6)
    for number in numbers:
        samples.append(getResults(res[number]))

    for sth in samples:
        print(sth)
        print("________________________________________________________________________________")
    return samples


#this function generates six samples of the passed food parameter
def generateFoodSamples(food):

    samples=[]

    for i in range(len(res)-1):
        if res[i]['MostPossibleTags'] is not None:
            if food in res[i]['MostPossibleTags']:
                samples.append(getResults(res[i]))
                if len(samples) > 6:
                    break

    for sth in samples:
        print(sth)
        print("__________________________________________________________________________________")

    return samples

#this function returns organized data that is needed in the carousels and the templates

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
