from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Post, Category, Author, Comment
from .forms import CommentForm
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.sessions.models import Session
import os
import requests
import json
from django.http import JsonResponse
import codecs
import re
import datetime
def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def homepage_views(request):
    post_list = Post.objects.all().order_by('-published')
    paginator = Paginator(post_list, 2) # Show x post per page.
    post_number = request.GET.get('page')
    post = paginator.get_page(post_number)
    category = Category.objects.all()
    access_token = request.session.get('access_token')
    context = {
        'post': post,  
        'category': category
    }
    return render(request, 'index_afterLogin.html', context={'login_failed': True})

def wrong_login(request):
    url = "https://api.kulpick.com/api/v1/member/login/"  # 실제 엔드포인트 URL로 대체해야 합니다.
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        # 요청 헤더 설정
        headers = {
            "Content-Type": "application/json"
        }

        # 로그인 정보 설정
        login_data = {
            "joinType": "1",           # 일반 회원 로그인
            "cellphoneNo": phone,  # 가입 시 사용한 휴대폰 번호
            "userPwd": password       # 가입 시 설정한 비밀번호
        }

        # POST 요청 보내기
        try:
            # POST 요청 보내기
            response = requests.post(url, headers=headers, json=login_data)
            response_data = json.loads(response.text)
            access_token = response_data['result']['data']['accessToken']
            request.session['access_token'] = access_token
            # 응답 확인
            return redirect(homepage_views_afterLogin)
        except KeyError:
            # 'accessToken' 키가 없는 경우 '잘못된 로그인 정보입니다' 팝업을 표시하고 현재 페이지에 머무릅니다.
            return redirect(wrong_login)

def homepage_views_afterLogin(request):
    if request.method == 'POST':
        store_no = request.POST.get('store_no')
        store_name = request.POST.get('store_name')
        request.session['store_no'] = store_no
        request.session['store_name'] = store_name
        request.session['store_no_session'] = store_no
        store_no_session = request.session.get('store_no_session')
        
        url = 'https://api.kulpick.com/api/v1/product'
        product_list = []  # 음식명과 가격을 번갈아 저장할 리스트
        access_token = request.session.get('access_token')
        product_name = None
        for key, value in request.POST.items():
            if key.startswith('product_'):
                if product_name is not None:
                    product_list.append([product_name, value])
                    product_name = None
                else:
                    product_name = value
        headers = {
            'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
        }
        # 이제 product_list에는 음식명과 가격이 번갈아가면서 저장됩니다.
        # 필요한 작업을 수행하고 응답을 반환
        context = {}
        for item in product_list:
            product_name, product_price = item
            a = normalize_price(product_price)
            data = {
                "storeNo": store_no,
                "productName": product_name,
                "price": a,
                "photoImgPaths": []
            }
            response = requests.post(url,headers=headers, json = data)
        url2 = 'https://api.kulpick.com/api/v1/product/list'
        data2 = {
            "storeNo": store_no,
            "pageCnt":'0'
        }
        response2 = requests.get(url2,headers=headers, params = data2)
        data_list = json.loads(response2.text)
        context = data_list
        url3 = 'https://api.kulpick.com/api/v1/store/info'
        data3 = {
            "storeNo": store_no,
        }
        response3 = requests.get(url3,headers=headers, params = data3)
        data4 = json.loads(response3.text)
        address = data4["result"]["data"]["storeInfo"]["address"]
        request.session['store_address'] = address
        return render(request, 'menu.html',context)
    else:
        # POST 요청이 아닌 경우 다른 작업을 수행하거나 적절한 응답을 반환할 수 있습니다.
        return HttpResponse('POST 요청이 아닙니다.')

def post_views(request, slug, id):
    post = Post.objects.get(slug=slug, id=id)
    comment = Comment.objects.all()
    
    new_comment = None
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            comment = CommentForm()
            messages.success(request, 'The form is valid.')
            return HttpResponseRedirect(reverse('post', kwargs={'slug': slug, 'id': id}))
    else:
        form = CommentForm()
    context = {
        'post': post,
        'comment': comment,
        'form': form,
        'new_comment': new_comment
    }
    return render(request, 'single.html', context)



def category_views(request, slug):
    category = get_object_or_404(Category, slug=slug)
    post = Post.objects.filter(category=category)

    context = {
        'category': category,
        'post': post
    }
    return render(request, 'category.html',context)

#사진 촬영

def take_picture(request):
    if request.method == 'POST':
        # request.FILES를 사용하여 업로드된 이미지에 접근합니다.
        uploaded_image = request.FILES.get('camera-input')
        if uploaded_image:
            url = 'http://43.201.215.208:8000/hongbo/upload_img/'
            files = {'image': uploaded_image}
            response = requests.post(url, files={'image': ('uploaded_image.jpg', uploaded_image)})
            #print(response.text)  # response에서 텍스트 데이터를 확인
            data_list = json.loads(response.text)
            # 이스케이프된 유니코드 디코딩
            decoded_response = codecs.decode(response.text, 'unicode_escape')

            # JSON 문자열로 변환
            json_data = json.dumps(decoded_response, ensure_ascii=False)

            # 디코딩된 JSON 문자열을 파싱하여 딕셔너리로 변환
            parsed_data = json.loads(json_data)
            # context 변수 선언 및 할당
            context = data_list
            for item in context['menu']:
                price = re.sub(r'[^\d]', '', item['price'])
                if len(price) == 2:  # 두 자릿수 숫자인 경우
                    price = int(price) * 100
                elif len(price) == 3 and price[-1] == '0':  # 세 자릿수이면서 일의 자리가 0인 경우
                    price = int(price) * 100
                item['price'] = price

            return render(request, 'menuManage.html', context)
        else:
            return JsonResponse({'error': 'Image not found in the request'}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
"""def upload_product(request):
    if request.method == 'POST':
        print('upload_product')
        url = 'https://api.kulpick.com/api/v1/product/'
        files = {'productNo': 1}
        response = requests.get(url, params=files)
        return HttpResponse('제품 업로드가 완료되었습니다.')
    else:
        return HttpResponse('POST 요청이 아닙니다.')"""

def normalize_price(price_str):
    # 특수문자 (','나 '.')를 모두 제거합니다.
    cleaned_price_str = ''.join(char for char in price_str if char.isdigit())
    
    # 숫자 문자열의 길이가 2자리라면 100을 곱하고, 그렇지 않으면 변화 없이 반환합니다.
    if len(cleaned_price_str) == 2:
        normalized_price = int(cleaned_price_str) * 100
    else:
        normalized_price = cleaned_price_str
    
    return str(normalized_price)

def upload_product(request):
    if request.method == 'POST':
        store_no_session = request.session.get('store_no')
        store_name_session = request.session.get('store_name')
        url = 'https://api.kulpick.com/api/v1/product'
        product_list = []  # 음식명과 가격을 번갈아 저장할 리스트
        access_token = request.session.get('access_token')
        product_name = None
        for key, value in request.POST.items():
            if key.startswith('product_'):
                if product_name is not None:
                    product_list.append([product_name, value])
                    product_name = None
                else:
                    product_name = value
        headers = {
            'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
        }
        # 이제 product_list에는 음식명과 가격이 번갈아가면서 저장됩니다.
        # 필요한 작업을 수행하고 응답을 반환
        for item in product_list:
            product_name, product_price = item
            a = normalize_price(product_price)
            data = {
                "storeNo": store_no_session,
                "productName": product_name,
                "price": a,
                "photoImgPaths": []
            }
            response = requests.post(url,headers=headers, json = data)

        url2 = 'https://api.kulpick.com/api/v1/product/list'
        data2 = {
            "storeNo": store_no_session,
            "pageCnt":'0'
        }
        response2 = requests.get(url2,headers=headers, params = data2)

        data_list = json.loads(response2.text)
        context = data_list

        return render(request, 'menu.html',context)
    else:
        # POST 요청이 아닌 경우 다른 작업을 수행하거나 적절한 응답을 반환할 수 있습니다.
        return HttpResponse('POST 요청이 아닙니다.')
    
def login(request):
    url = "https://api.kulpick.com/api/v1/member/login/"  # 실제 엔드포인트 URL로 대체해야 합니다.
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        # 요청 헤더 설정


        # 로그인 정보 설정
        login_data = {
            "joinType": "1",           # 일반 회원 로그인
            "cellphoneNo": phone,  # 가입 시 사용한 휴대폰 번호
            "userPwd": password       # 가입 시 설정한 비밀번호
        }

        # POST 요청 보내기
        try:
            # POST 요청 보내기
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(url, headers=headers, json=login_data)
            response_data = json.loads(response.text)
            access_token = response_data['result']['data']['accessToken']
            request.session['access_token'] = access_token

            # 응답 확인
            return redirect(select_store)
        except KeyError:
            # 'accessToken' 키가 없는 경우 '잘못된 로그인 정보입니다' 팝업을 표시하고 현재 페이지에 머무릅니다.
            return render(request, 'wrong_login.html')
        
def select_store(request):
    url = "https://api.kulpick.com/api/v1/store/list/"  # 실제 엔드포인트 URL로 대체해야 합니다.

    # 요청 헤더 설정
    access_token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
    }
    # 로그인 정보 설정
    params = {
        "listType": "3",           # 내 매장 리스트
    }
    response = requests.get(url,headers=headers, params = params)

    response_data = json.loads(response.text)
    store_list = response_data["result"]["data"]["storeList"]

    store_no_list = [store["storeNo"] for store in response_data["result"]["data"]["storeList"]]
    store_name_list = [store["storeName"] for store in response_data["result"]["data"]["storeList"]]
    request.session['store_no_list'] = store_no_list
    request.session['store_name_list'] = store_name_list
    for store_no in store_no_list:
        print("storeNo:", store_no)
    data_list = json.loads(response.text)
    context = data_list
    return render(request, 'select_store2.html', {'store_list': store_list})

def flowbite_test(request):
   
    return render(request, 'flowbite_test.html')

"""=======================================AI 추천화면======================================"""

import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import LabelEncoder
from altair.vegalite.v4.api import Chart
from . import salesarea_v1 as sla
import joblib
import geopandas as gpd
from shapely.geometry import Point
import requests
from pyproj import Transformer
np.random.seed()
random.seed()

"""================== template ============================"""
def menu(request):
    
    return render(request, 'menu.html')

def picture(request):
    
    return render(request, 'picture.html')

def menuManage(request):
    
    return render(request, 'menuManage.html')

def special(request):
    
    product_name = request.POST.get('product_name')
    product_price = request.POST.get('product_price')
    product_image = request.POST.get('product_image')
    product_no = request.POST.get('product_no') 
    request.session['session_product_image'] = product_image
    request.session['session_product_no'] = product_no
    context = {
        'product_name': product_name,
        'product_price': product_price,
        'product_image' : product_image,
    }
    request.session['gogo_product_name'] = product_name
    request.session['gogo_product_price'] = product_price
    return render(request, 'special.html', context)

def speacial_menu(request):
    if request.method == 'POST':
        store_no_session = request.session.get('store_no')
        store_name_session = request.session.get('store_name')
        store_no = request.POST.get('store_no')
        store_name = request.POST.get('store_name')
        request.session['store_no'] = store_no
        request.session['store_name'] = store_name
        url = 'https://api.kulpick.com/api/v1/product'
        product_list = []  # 음식명과 가격을 번갈아 저장할 리스트
        access_token = request.session.get('access_token')
        product_name = None
        for key, value in request.POST.items():
            if key.startswith('product_'):
                if product_name is not None:
                    product_list.append([product_name, value])
                    product_name = None
                else:
                    product_name = value
        headers = {
            'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
        }
        # 이제 product_list에는 음식명과 가격이 번갈아가면서 저장됩니다.
        # 필요한 작업을 수행하고 응답을 반환
        context = {}
        for item in product_list:
            product_name, product_price = item
            a = normalize_price(product_price)
            data = {
                "storeNo": store_no,
                "productName": product_name,
                "price": a,
                "photoImgPaths": []
            }
            response = requests.post(url,headers=headers, json = data)
        url2 = 'https://api.kulpick.com/api/v1/product/list'
        data2 = {
            "storeNo": store_no_session,
            "pageCnt":'0'
        }
        response2 = requests.get(url2,headers=headers, params = data2)
        data_list = json.loads(response2.text)
        context = data_list
        return render(request, 'speacial_menu.html')
    else:
        store_no_session = request.session.get('store_no')
        store_name_session = request.session.get('store_name')
        url = 'https://api.kulpick.com/api/v1/product'
        product_list = []  # 음식명과 가격을 번갈아 저장할 리스트
        access_token = request.session.get('access_token')
        product_name = None
        print(store_no_session)
        print(store_name_session)
        for key, value in request.POST.items():
            if key.startswith('product_'):
                if product_name is not None:
                    product_list.append([product_name, value])
                    product_name = None
                else:
                    product_name = value
        headers = {
            'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
        }
        # 이제 product_list에는 음식명과 가격이 번갈아가면서 저장됩니다.
        # 필요한 작업을 수행하고 응답을 반환
        context = {}
        for item in product_list:
            product_name, product_price = item
            a = normalize_price(product_price)
            data = {
                "storeNo": store_no_session,
                "productName": product_name,
                "price": a,
                "photoImgPaths": []
            }
            response = requests.post(url,headers=headers, json = data)
        url2 = 'https://api.kulpick.com/api/v1/product/list'
        data2 = {
            "storeNo": store_no_session,
            "pageCnt":'0'
        }
        response2 = requests.get(url2,headers=headers, params = data2)
        data_list = json.loads(response2.text)
        context = data_list
        return render(request, 'speacial_menu.html', context)
    
"""================== template ============================"""

def ai_recommand(request):
    
    return render(request, 'ai_recommand.html')

def ai_recommand_progress(request):
    if request.method == 'POST':
        loaded_model = joblib.load("C:/Users/PC/Desktop/git_추천_ver3/test999.pkl")
        default_input = request.POST.get('default_input')
        product2 = request.POST.get('product')
        weather2 = request.POST.get('weather')
        event2 = request.POST.get('event')
        time2 = request.POST.get('time')
        products = pd.DataFrame({
        '상품종류': ['product1', 'product2', 'product3', 'product4', 'product5'],
        '마진율': [0.2, 0.3, 0.3, 0.4, 0.5],
        '가격': [5000, 7000, 9000, 10000, 12000],
        '할인율': [random.uniform(1 * margin_rate, 0.5 * margin_rate) for margin_rate in [0.2, 0.3, 0.3, 0.4, 0.5]],
        })
        data_size = 100
        product = random.choices(products['상품종류'], k=data_size)
        margin_rate = [products.loc[products['상품종류'] == p, '마진율'].values[0] for p in product]
        price = [products.loc[products['상품종류'] == p, '가격'].values[0] for p in product]
        discount_rate = [products.loc[products['상품종류'] == p, '할인율'].values[0] for p in product]
        weather = random.choices(['맑음', '흐림', '비'], k=data_size)
        event = random.choices([0, 1], k=data_size)
        sale_time = random.choices(['오전', '오후'], k=data_size)
        df = pd.DataFrame({
            '상품종류': product,
            '마진율': margin_rate,
            '가격': price,
            '할인율': discount_rate,
            '날씨': weather,
            '이벤트 여부': event,
            '판매시간': sale_time,
            '판매량': np.random.randint(1, 10, size=data_size)
        })
        le_product_type = LabelEncoder()
        le_weather = LabelEncoder()
        le_sale_time = LabelEncoder()
        le_product_type.fit(df['상품종류'])
        le_weather.fit(df['날씨'])
        le_sale_time.fit(df['판매시간'])

    
        address = default_input
        product_type = product2
        weather = weather2
        event = event2
        sale_time = time2
        # location_type = st.selectbox('거리상권환경', ['대로변 1층', '아파트 상가', '소로변'])
        product_type_encoded = le_product_type.transform([product_type])[0]
        
        weather_encoded = le_weather.transform([weather])[0]
        sale_time_encoded = le_sale_time.transform([sale_time])[0]
        event = event

        input_data = pd.DataFrame([[
            product_type_encoded,
            products.loc[products['상품종류'] == product_type, '마진율'].values[0],
            products.loc[products['상품종류'] == product_type, '가격'].values[0],
            weather_encoded,
            event,
            sale_time_encoded
        ]])

        prediction = loaded_model.predict(input_data)[0]
        area_type, area_detail = sla.find_biz_ara_info(address)
        # 주변상권환경 및 거리상권환경에 따른 조정 
        # (상품군에 따른 특가상품 판매 데이터에 대한 통계치 이용으로 변경예정 - 꿀픽을 통한 데이터 확보 시)
        if area_type == '골목상권':        
            prediction[0] *= 0.8
        elif area_type == '관광특구': # 관광특구 내 이벤트 발생시 가중치 증가
            kk = 1 # 관광특구 가중치 설정
            prediction[0] *= (0.8 + event * kk)
        elif area_type == '전통시장': 
            prediction[0] *= 1.2
        else:  # 발달상권
            prediction[0] *= 2
        
        # 만일 추천 할인율이 마진율보다 크다면, 마진율로 설정 (최소 이익을 위해 변경 가능)
        if prediction[1] > products.loc[products['상품종류'] == product_type, '마진율'].values[0] :
            prediction[1] = products.loc[products['상품종류'] == product_type, '마진율'].values[0]
        context = {
            'area_detail' : area_detail,
            'area_type' : area_type,
            'prediction' : round(prediction[0]),
            'discount' : prediction[1]*100,
        }

        return render(request, 'ai_recommand_done.html', context)
    else:
        loaded_model = joblib.load("C:/Users/PC/Desktop/git_추천_ver3/test999.pkl")
        default_input = request.POST.get('default_input')
        product2 = request.POST.get('product')
        weather2 = request.POST.get('weather')
        event2 = request.POST.get('event')
        time2 = request.POST.get('time')
        products = pd.DataFrame({
        '상품종류': ['product1', 'product2', 'product3', 'product4', 'product5'],
        '마진율': [0.2, 0.3, 0.3, 0.4, 0.5],
        '가격': [5000, 7000, 9000, 10000, 12000],
        '할인율': [random.uniform(1 * margin_rate, 0.5 * margin_rate) for margin_rate in [0.2, 0.3, 0.3, 0.4, 0.5]],
        })
        data_size = 100
        product = random.choices(products['상품종류'], k=data_size)
        margin_rate = [products.loc[products['상품종류'] == p, '마진율'].values[0] for p in product]
        price = [products.loc[products['상품종류'] == p, '가격'].values[0] for p in product]
        discount_rate = [products.loc[products['상품종류'] == p, '할인율'].values[0] for p in product]
        weather = random.choices(['맑음', '흐림', '비'], k=data_size)
        event = random.choices([0, 1], k=data_size)
        sale_time = random.choices(['오전', '오후'], k=data_size)
        df = pd.DataFrame({
            '상품종류': product,
            '마진율': margin_rate,
            '가격': price,
            '할인율': discount_rate,
            '날씨': weather,
            '이벤트 여부': event,
            '판매시간': sale_time,
            '판매량': np.random.randint(1, 10, size=data_size)
        })
        le_product_type = LabelEncoder()
        le_weather = LabelEncoder()
        le_sale_time = LabelEncoder()
        le_product_type.fit(df['상품종류'])
        le_weather.fit(df['날씨'])
        le_sale_time.fit(df['판매시간'])

    
        address = default_input
        product_type = 'product2'
        weather = '맑음'
        event = '1'
        sale_time = '오후'
        # location_type = st.selectbox('거리상권환경', ['대로변 1층', '아파트 상가', '소로변'])
        product_type_encoded = le_product_type.transform([product_type])[0]
        
        weather_encoded = le_weather.transform([weather])[0]
        sale_time_encoded = le_sale_time.transform([sale_time])[0]
        event = event

        input_data = pd.DataFrame([[
            product_type_encoded,
            products.loc[products['상품종류'] == product_type, '마진율'].values[0],
            products.loc[products['상품종류'] == product_type, '가격'].values[0],
            weather_encoded,
            event,
            sale_time_encoded
        ]])

        prediction = loaded_model.predict(input_data)[0]
        area_type, area_detail = sla.find_biz_ara_info(address)
        # 주변상권환경 및 거리상권환경에 따른 조정 
        # (상품군에 따른 특가상품 판매 데이터에 대한 통계치 이용으로 변경예정 - 꿀픽을 통한 데이터 확보 시)
        if area_type == '골목상권':        
            prediction[0] *= 0.8
        elif area_type == '관광특구': # 관광특구 내 이벤트 발생시 가중치 증가
            kk = 1 # 관광특구 가중치 설정
            prediction[0] *= (0.8 + event * kk)
        elif area_type == '전통시장': 
            prediction[0] *= 1.2
        else:  # 발달상권
            prediction[0] *= 2
        
        # 만일 추천 할인율이 마진율보다 크다면, 마진율로 설정 (최소 이익을 위해 변경 가능)
        if prediction[1] > products.loc[products['상품종류'] == product_type, '마진율'].values[0] :
            prediction[1] = products.loc[products['상품종류'] == product_type, '마진율'].values[0]

        context = {
            'area_detail' : area_detail,
            'area_type' : area_type,
            'prediction' : round(prediction[0]),
            'discount' : prediction[1]*100,
        }
        return render(request, 'ai_recommand_done.html', context)
    

def speacial_result(request):
    margin_rate = random.choice([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])

    discount_rate = random.uniform(1 * margin_rate, 0.5 * margin_rate)
    start_time = None
    end_time = None
    product_image = request.session.get('session_product_image')
    store_address = request.session.get('store_address')
    gogo_product_name = request.session.get('gogo_product_name')
    gogo_product_price = request.session.get('gogo_product_price')
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        loaded_model = joblib.load("C:/Users/PC/Desktop/git_추천_ver3/test999.pkl")
        default_input = request.POST.get('default_input')
        product2 = request.POST.get('product')
        weather2 = request.POST.get('weather')
        event2 = request.POST.get('event')
        time2 = request.POST.get('time')
        products = pd.DataFrame({
        '상품종류': ['product1'],
        '마진율': [margin_rate],
        '가격': [5000],
        '할인율': [discount_rate],
        })
        data_size = 100
        product = random.choices(products['상품종류'], k=data_size)
        margin_rate = [products.loc[products['상품종류'] == p, '마진율'].values[0] for p in product]
        price = [products.loc[products['상품종류'] == p, '가격'].values[0] for p in product]
        discount_rate = [products.loc[products['상품종류'] == p, '할인율'].values[0] for p in product]
        weather = random.choices(['맑음', '흐림', '비'], k=data_size)
        event = random.choices([0, 1], k=data_size)
        sale_time = random.choices(['오전', '오후'], k=data_size)
        df = pd.DataFrame({
            '상품종류': product,
            '마진율': margin_rate,
            '가격': price,
            '할인율': discount_rate,
            '날씨': weather,
            '이벤트 여부': event,
            '판매시간': sale_time,
            '판매량': np.random.randint(1, 10, size=data_size)
        })
        le_product_type = LabelEncoder()
        le_weather = LabelEncoder()
        le_sale_time = LabelEncoder()
        le_product_type.fit(df['상품종류'])
        le_weather.fit(df['날씨'])
        le_sale_time.fit(df['판매시간'])

    
        address = store_address
        product_type = 'product1'
        weather = '맑음'
        event = '1'
        sale_time = '오후'
        # location_type = st.selectbox('거리상권환경', ['대로변 1층', '아파트 상가', '소로변'])
        product_type_encoded = le_product_type.transform([product_type])[0]
        
        weather_encoded = le_weather.transform([weather])[0]
        sale_time_encoded = le_sale_time.transform([sale_time])[0]
        event = event

        input_data = pd.DataFrame([[
            product_type_encoded,
            products.loc[products['상품종류'] == product_type, '마진율'].values[0],
            products.loc[products['상품종류'] == product_type, '가격'].values[0],
            weather_encoded,
            event,
            sale_time_encoded
        ]])

        prediction = loaded_model.predict(input_data)[0]
        area_type, area_detail = sla.find_biz_ara_info(address)
        # 주변상권환경 및 거리상권환경에 따른 조정 
        # (상품군에 따른 특가상품 판매 데이터에 대한 통계치 이용으로 변경예정 - 꿀픽을 통한 데이터 확보 시)
        if area_type == '골목상권':        
            prediction[0] *= 0.8
        elif area_type == '관광특구': # 관광특구 내 이벤트 발생시 가중치 증가
            kk = 1 # 관광특구 가중치 설정
            prediction[0] *= (0.8 + event * kk)
        elif area_type == '전통시장': 
            prediction[0] *= 1.2
        else:  # 발달상권
            prediction[0] *= 2
        
        # 만일 추천 할인율이 마진율보다 크다면, 마진율로 설정 (최소 이익을 위해 변경 가능)
        if prediction[1] > products.loc[products['상품종류'] == product_type, '마진율'].values[0] :
            prediction[1] = products.loc[products['상품종류'] == product_type, '마진율'].values[0]
        context = {
            'area_detail' : area_detail,
            'area_type' : area_type,
            'prediction' : round(prediction[0]),
            'discount' : prediction[1]*100,
        }
        context = {
            'start_time': start_time,
            'end_time': end_time,
            'prediction' : round(prediction[0]),
            'discount' : prediction[1]*100,
            'gogo_product_name' : request.session.get('gogo_product_name'),
            'gogo_product_price' : request.session.get('gogo_product_price'),
            'product_image' : product_image,
        }
        request.session['ai_recommend_session_start_time'] = start_time
        request.session['ai_recommend_session_end_time'] = end_time
        request.session['ai_recommend_session_prediction'] = round(prediction[0])
        request.session['ai_recommend_session_discount'] = prediction[1]*100
        return render(request, 'speacial_result.html', context)
    

def upload_speacial_product(request):
    if request.method == 'POST':
        explain = request.POST.get('explain')
        store_address = request.session.get('store_address')
        session_product_no = request.session.get('session_product_no')
        ai_recommend_session_start_time = request.session.get('ai_recommend_session_start_time')
        ai_recommend_session_end_time = request.session.get('ai_recommend_session_end_time')
        ai_recommend_session_prediction = request.session.get('ai_recommend_session_prediction')
        ai_recommend_session_discount = request.session.get('ai_recommend_session_discount')
        url = 'https://api.kulpick.com/api/v1/product/timesale'
        access_token = request.session.get('access_token')
        headers = {
                    'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
                }

        a = str(ai_recommend_session_discount)
        str_ai_recommend_session_prediction = str(ai_recommend_session_prediction)
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        second = ('00')
        start_time_result = today_str + " " + ai_recommend_session_start_time + ":" + second
        end_time_result = today_str + " " + ai_recommend_session_end_time + ":" + second
        str_session_product_no = str(session_product_no)
        data = {
            "productNo": str_session_product_no,
            "timeType": "1",
            "startTime": start_time_result,
            "endTime": end_time_result,
            "discountPrice": "",
            "discountRate": a,
            "timesaleCnt": str_ai_recommend_session_prediction,
            "memo": explain
        }
        #sample data
        """{
        "productNo": "646",
        "timeType": "1",
        "startTime": "2022-04-25 23:00:00",
        "endTime": "2022-04-26 02:00:00",
        "discountPrice": "",
        "discountRate": "10",
        "timesaleCnt": "10",
        "memo": "간단설명"
        logo.png
        }"""
        response = requests.post(url,headers=headers, json = data)
        return redirect('time_speacial')
    
def time_speacial(request):
    store_no_session = request.session.get('store_no_session')
    all_sessions = Session.objects.all()

    for session_obj in all_sessions:
        session_data = session_obj.get_decoded()  # 세션 데이터 디코딩
    storeNo = request.session.get('store_no')
    access_token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'  # Bearer 스킴을 사용한 토큰 포함
    }
    url2 = 'https://api.kulpick.com/api/v1/product/timesale/list'
    data2 = {
        "listType": '4',
        "orderType":'1',
        #"latitude" : '',
        #"longitude" : '',
        "storeNo" : store_no_session,
        "status" : '1',
        #"pageNo" : "",
        #"pageCnt" : "",
    }
    response2 = requests.get(url2,headers=headers, params = data2)
    data_list = json.loads(response2.text)
    context = data_list
    return render(request, 'time_speacial.html', context)
    
from konlpy.tag import Komoran, Kkma, Okt
from collections import Counter
import numpy as np
import itertools

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

def brothertaeso(doc, top_n=3):
    # Kkma 형태소 분석기 초기화
    kkm = Kkma()
    
    # 줄 바꿈 및 공백 문자 제거
    content = doc.replace('\n', '').replace('\t', '').replace('\r', '')
    
    # 명사만 추출
    kkm_nouns = [word for word, pos in kkm.pos(content) if pos == 'NNG']
    
    # 가장 빈도가 높은 상위 n 개의 명사 추출
    top_nouns = Counter(kkm_nouns).most_common(top_n)
    
    return top_nouns

def extract_top_nouns(request):
    print('extract_top_nouns')
    if request.method == 'GET':
        # GET 요청에서 fulltext 파라미터 추출
        fulltext = request.GET.get('fulltext', '')

        # 요청이 올바르지 않은 경우 처리
        if not fulltext:
            response_data = {'error': 'fulltext 파라미터가 필요합니다.'}
            return JsonResponse(response_data, status=400)  # 400 Bad Request 반환

        # fulltext를 처리하고 결과를 fulltext2에 할당하는 코드 (brothertaeso 함수 사용)
        fulltext2 = brothertaeso(fulltext)

        # JSON 응답 데이터 생성
        response_data = {'keyword_mode': fulltext2}

        # JsonResponse로 JSON 형식으로 응답
        return JsonResponse(response_data)
    elif request.method == 'POST':
        # POST 요청에서 fulltext 데이터 추출
        fulltext = request.POST.get('fulltext', '')

        # 요청이 올바르지 않은 경우 처리
        if not fulltext:
            response_data = {'error': 'fulltext 데이터가 필요합니다.'}
            return JsonResponse(response_data, status=400)  # 400 Bad Request 반환

        # fulltext를 처리하고 결과를 fulltext2에 할당하는 코드 (brothertaeso 함수 사용)
        fulltext2 = brothertaeso(fulltext)

        # JSON 응답 데이터 생성
        response_data = {'fulltext2': fulltext2}

        # JsonResponse로 JSON 형식으로 응답
        return JsonResponse(response_data)
    else:
        # 지원하지 않는 메서드인 경우
        response_data = {'error': '지원하지 않는 HTTP 메서드입니다.'}
        return JsonResponse(response_data, status=405)

def keyword_value(request):
    if request.method == 'GET':
        doc = request.GET.get('fulltext', '')
        n_gram_range = (2, 2)
        stop_words = "english"

        count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([doc])
        candidates = count.get_feature_names_out()

        print('trigram 개수 :',len(candidates))
        print('trigram 다섯개만 출력 :',candidates[:3])
        candidates_list = candidates.tolist()
        response_data = {'keyword_value': candidates_list[:3]}
        return JsonResponse(response_data)
    elif request.method == 'POST':
        # POST 요청에서 fulltext 데이터 추출
        fulltext = request.POST.get('fulltext', '')

        # 요청이 올바르지 않은 경우 처리
        if not fulltext:
            response_data = {'error': 'fulltext 데이터가 필요합니다.'}
            return JsonResponse(response_data, status=400)  # 400 Bad Request 반환

        # fulltext를 처리하고 결과를 fulltext2에 할당하는 코드 (brothertaeso 함수 사용)
        fulltext2 = brothertaeso(fulltext)

        # JSON 응답 데이터 생성
        response_data = {'fulltext2': fulltext2}

        # JsonResponse로 JSON 형식으로 응답
        return JsonResponse(response_data)
    else:
        # 지원하지 않는 메서드인 경우
        response_data = {'error': '지원하지 않는 HTTP 메서드입니다.'}
        return JsonResponse(response_data, status=405)




        