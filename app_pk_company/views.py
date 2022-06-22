from django.http import JsonResponse
import pandas as pd
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import app_user_keyword_association.views as userkeyword_view 

def load_data_pk():
    # Read data from csv file
    
    df_data_pk = pd.read_csv('app_pk_company/dataset/pk_company.csv')
    
    global data
    data={}
    for k,v in zip(df_data_pk.name, df_data_pk.value):
        data[k]=eval(v)
    
    # 沒用到的變數刪除之
    del df_data_pk

# load pk data
load_data_pk()

def home(request):
    return render(request,'app_pk_company/home.html')

# csrf_exempt is used for POST
# 單獨指定這一支程式忽略csrf驗證
@csrf_exempt
def api_get_taipei_mayor_data(request):
    return JsonResponse(data)

print('app_leaderboard was loaded!')
