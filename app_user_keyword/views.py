from django.shortcuts import render
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import MySQLdb as mariadb

# (1) we can load data using read_csv()
# global variable
# df = pd.read_csv('dataset/news_dataset_preprocessed_for_django.csv', sep='|')

# (2) we can load data using reload_df_data() function
def load_df_data():
    # global variable
    global  df
    conn=mariadb.connect(host='localhost',user='root',passwd='9bhtj93g',db='poa')
    df=pd.read_sql('select * from data_cnyes;',conn)
    # cursor=conn.cursor()
    # cursor.execute('select `item_id`,`category`,`tokens_v2`,`date` from cnyes;')
    # items_id=[]
    # categories=[]
    # tokens_v2s=[]
    # dates=[]

    # for item_id,category,token_v2,date in cursor:
    #     items_id.append(item_id)
    #     categories.append(category)
    #     tokens_v2s.append(token_v2)
    #     dates.append(date)
    # conn.commit()
    # conn.close()
    # data=zip(items_id,categories,tokens_v2s,dates)
    # df=pd.DataFrame(list(data), columns=['item_id','category','tokens_v2','date'])
    # df.tokens_v2=df.tokens_v2.apply(lambda row :str(str('[\'')+row.replace(',','\',\'')+str('\']')).replace(' ',''))
    
# We should reload df when necessary
load_df_data() 

# hoem page
def home(request):
    return render(request, 'app_user_keyword/home.html')

# When POST is used, make this function be exempted from the csrf 
@csrf_exempt
def api_get_top_userkey(request):
    # (1) get keywords, category, condition, and weeks passed from frontend
    userkey = request.POST.get('userkey')
    cate = request.POST.get('cate')
    cond = request.POST.get('cond')
    weeks = int(request.POST.get('weeks'))
    key = userkey.split()
    
    # (2) make df_query global, so it can be used by other functions
    global  df_query 

    # (3) filter dataframe
    df_query = filter_dataFrame(key, cond, cate,weeks)
    #print(len(df_query))

    # (4) get frequency data
    key_freq_cat, key_occurrence_cat = count_keyword(df_query, key)
    print(key_occurrence_cat)
    
    # (5) get line chart data
    # key_time_freq = [
    # '{"x": "2019-03-07", "y": 2}',
    # '{"x": "2019-03-08", "y": 2}',
    # '{"x": "2019-03-09", "y": 13}']
    key_time_freq = get_keyword_time_based_freq(df_query)

    # (6) response all data to frontend home page
    response = {
    'key_occurrence_cat': key_occurrence_cat,
    'key_freq_cat': key_freq_cat,
    'key_time_freq': key_time_freq, }

    return JsonResponse(response)

def filter_dataFrame(key, cond, cate,weeks):
    # end date: the date of the latest record of news
    end_date = df.date.max()
    print('latest date for dataset:', end_date)

    # start date
    start_date = (datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S').date() - timedelta(weeks=weeks)).strftime('%Y-%m-%d')

    # proceed filtering
    if (cate == "全部") & (cond == 'and'):
        query_df = df[(df.date >= start_date) & (df.date <= end_date) & df.tokens_v2.apply(
            lambda row: all((qk in row) for qk in key))]
    elif (cate == "全部") & (cond == 'or'):
        queryKey = '|'.join(key)
        query_df = df[(df['date'] >= start_date) & (df['date'] <= end_date) & df.tokens_v2.str.contains(queryKey)]
    elif (cond == 'and'):
        query_df = df[(df.category == cate) & (df.date >= start_date) & (df.date <= end_date) & df.tokens_v2.apply(
            lambda row: all((qk in row) for qk in key))]
    elif (cond == 'or'):
        queryKey = '|'.join(key)
        query_df = df[(df.category == cate) & (df['date'] >= start_date) & (df['date'] <= end_date) & df[
            'tokens_v2'].str.contains(queryKey)]

    return query_df


# ** How many pieces of news containing the keyword(s)?
# ** How many times were the keyword(s) mentioned?

# For the df_query, count the occurence and frequency for every category:
# (1) cate_occurence={}  number of pieces of news
# (2) cate_freq={}       number of times the keywords were mentioned

news_categories = ['全部','台股','國際股','陸港股','區塊鏈','外匯','期貨']

def count_keyword(df_query, key):
    cate_occurence={}
    cate_freq={}

    for cate in news_categories:
        cate_occurence[cate]=0
        cate_freq[cate]=0

    for idx, row in df_query.iterrows():
        # count pieces of news
        cate_occurence[row.category] += 1
        cate_occurence['全部'] += 1
        # count keyword frequency
        tokens = eval(row.tokens_v2)
        freq =  len([word for word in tokens if (word in key)])
        cate_freq[row.category] += freq
        cate_freq['全部'] += freq
    return cate_freq, cate_occurence

def get_keyword_time_based_freq(df_query):
    date_samples = df_query.date
    query_freq = pd.DataFrame({'date_index': pd.to_datetime(date_samples), 'freq': [1 for _ in range(len(df_query))]})
    data = query_freq.groupby(pd.Grouper(key='date_index', freq='D')).sum()
    time_data = []
    for i, idx in enumerate(data.index):
        row = {'x': idx.strftime('%Y-%m-%d'), 'y': int(data.iloc[i].freq)}
        time_data.append(row)
    return time_data

print("app_user_keyword was loaded!")

