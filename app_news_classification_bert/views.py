'''
requirements:
tensorflow==2.3
transformers==4.6 or above
'''
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


from tensorflow.keras.models import load_model
from transformers import BertTokenizer, BertTokenizerFast
from transformers import TFAlbertModel, TFBertModel
import numpy as np
import os

# We don't use GPU

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# ----------------
# main steps and global variables

# Load our best trained model
model_name='app_news_classification_bert/best_model/best-albert-base-chinese.h5'
model = load_model(model_name, custom_objects={"TFAlbertModel": TFAlbertModel})

# Load tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')

# Category index
news_categories=['台股','國際股','陸港股','區塊鏈','外匯','期貨']
idx2cate = { i : item for i, item in enumerate(news_categories)}

# ----------------------
# Functions for Django 
# home
def home(request):
    return render(request, "app_news_classification_bert/home.html")

# api get score
@csrf_exempt
def api_get_news_category(request):
    
    new_text = request.POST.get('input_text')
    #new_text = request.POST['input_text']
    print(new_text)

    # See the content_type and body從前端送過來的資料格式
    print(request.content_type)
    print(request.body) # byte format

    category_prob = get_category_proba(new_text)

    return JsonResponse(category_prob)

# -------------------------------------
# Code copied from jupyter notebook
def preprocessing_for_bert(input_sentences):
    result = tokenizer(
        text=list(input_sentences),
        add_special_tokens=True,
        max_length=250,  # 文件若較長，必須放大一些 最長為512
        truncation=True,
        #padding=True, 
        padding='max_length',
        return_tensors='tf',
        return_token_type_ids = False,
        return_attention_mask = True,
        verbose = True)

    return result

# get category probability
def get_category_proba( text ):
    X_data = preprocessing_for_bert([text])
    X_newText = {'input_ids': X_data['input_ids'], 'attention_mask': X_data['attention_mask']}
    result = model.predict(X_newText)
    print(result)
    
    result_label = np.argmax(result, axis=-1)
    
    label = idx2cate[ result_label[0] ]

    # Note that result is numpy format and it should be convert to float
    proba = round(float(max(result[0])),2)

    return {'label': label, 'proba': proba}

print("Loading app bert news classification.")
