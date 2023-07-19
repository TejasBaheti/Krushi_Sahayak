import nltk
import string
import random
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import googletrans
from googletrans import Translator
from googletrans import LANGUAGES
from flask import Flask,render_template,url_for,redirect,request
import json
import sys
#For weather
import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta

def weather():
    res = requests.get('https://ipinfo.io/')
    # Receiving the response in JSON format
    data1 = res.json()
    # Extracting the Location of the City from the response
    city = data1['city']
    # print(city)
    # extract today's date
    date = datetime.now() + timedelta(1)
    day = date.strftime('%A')
    # print(day)
    # creating url and requests instance
    url = "https://www.google.com/search?q="+"weather"+city+" tomorrow"
    html = requests.get(url).content
    # print("\n\n\n\n\n",html)
    # getting raw data
    soup = BeautifulSoup(html, 'html.parser')
    # temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text

    # formatting data
    data = str.split('\n')
    time = data[0]
    sky = data[1]
    temp=data[2]

    # getting all div tag
    listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
    strd = listdiv[5].text

    # getting other required data
    pos = strd.find('Wind')
    other_data = strd[pos:]

    # printing all data
    # print("Temperature is", temp)
    # print("Time: ", time)
    # print("Sky Description: ", sky)
    # print(other_data)
    forecast="In "+city+" on "+time+" the temperature will be "+temp+" and the weather will be "+sky
    return forecast

# read document
f=open('EXCEL.csv','r',errors='ignore')
raw_doc=f.read()
raw_doc=raw_doc.lower()

# import NLTK 
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')


# document processing
sentence_tokens=nltk.sent_tokenize(raw_doc)

lemmer=nltk.stem.WordNetLemmatizer()
def LemTokens(tokens):
  return [lemmer.lemmatize(token) for token in tokens]
remove_punc_dict=dict((ord(punct),None) for punct in string.punctuation)
def LemNormalize(text):
  return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punc_dict)))

greet_inputs=('hello','hi','wassup','hello there?')
greet_responses=('Hi','Hey there!','There There!?')
def greet(sentence):
  for word in sentence.split():
    if word.lower in greet_inputs:
      return random.choice(greet_responses)
#Construct response
def response(user_response):
  robo1_response=''
  TfidVec=TfidfVectorizer(tokenizer=LemNormalize,stop_words='english')
  tfidf=TfidVec.fit_transform(sentence_tokens)
  vals=cosine_similarity(tfidf[-1],tfidf)
  #print(vals)
  idx=vals.argsort()[0][-2]
  #print(idx)
  flat=vals.flatten()
  flat.sort()
  req_tfidf=flat[-2]
  if (req_tfidf==0):
    robo1_response=robo1_response+">I am sorry,I am unable to understand you!"
    return robo1_response
  else:
    robo1_response=robo1_response+sentence_tokens[idx]
    #print(sentence_tokens[idx])
    return robo1_response

app=Flask(__name__)
@app.route('/')
def welcome():
  return render_template('index.html')

@app.route('/answer/<string:ans>/<string:q>')
def func(ans,q):
  print(ans)
  print(q)
  return render_template('index2.html',answ=ans,qe=q)

@app.route('/submit',methods=['POST','GET'])
def submit():
  if request.method=='POST':
    # # question=request.form['textbox']
    # # print(question)
    x=request.form['speechtotext']
    print(x)
    translator = Translator()
    # unknown_sentence = x
    results = translator.detect(x)
    orignal = x
    translation = translator.translate(x, dest='en')
    x=translation.text
    fl=0
    if(results.lang == 'mr'):
      fl=1
      print(results.lang)
      print(fl)
    elif(results.lang == 'hi'):
      fl=2
      print(results.lang)
    elif(results.lang == 'en'):
      fl=0
      print(results.lang)
   
    flag=True
    output_var="hii"
    user_response=x
    user_response=user_response.lower()
    if(user_response!='bye'):
        if(user_response=='thank you' or user_response=='thanks'):
            flag=False
            output_var = 'BOT: You are welcome...'
        else:
            if(greet(user_response)!=None):
                output_var = 'BOT: '+greet(user_response)
            else:
                sentence_tokens.append(user_response)
                word_tokens=nltk.word_tokenize(raw_doc)
                word_tokens=word_tokens + nltk.word_tokenize(user_response)
                final_words=list(set(word_tokens))
                #output_var = 'BOT :> ',end='   '
                position=1
                for i in response(user_response):
                    position += 1
                    if i == '>':
                        break
                temp= response(user_response)[position:]
            
                if(fl==1):
                    translator = Translator()
                    user_output = translator.translate(temp, dest='mr')
                    output_var= user_output.text
        
                elif(fl==2):
                    translator = Translator()
                    user_output = translator.translate(temp, dest='hi')
                    output_var= user_output.text
        
                elif(fl==0):
                    output_var= temp
                
                sentence_tokens.remove(user_response)

    else: 
        flag=False
        output_var= 'BOT: Goodbye!'

    print(output_var)
    q=orignal
    
    

  return redirect(url_for('func',ans=output_var,q=orignal))

#for weather
@app.route('/weather_func',methods=['POST','GET'])
def weather_func():
    if request.method=='POST':
        q="Tomorrow's weather"
        ans=weather()
    return render_template('index2.html',answ=ans,qe=q)
  
  




  
if __name__=='__main__':
    app.run(debug=True)