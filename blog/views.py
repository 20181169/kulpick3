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
import os
import requests
import json
from django.http import JsonResponse
import codecs
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
    print(access_token)
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
            print('KeyError')
            # 'accessToken' 키가 없는 경우 '잘못된 로그인 정보입니다' 팝업을 표시하고 현재 페이지에 머무릅니다.
            return redirect(wrong_login)

def homepage_views_afterLogin(request):
    post_list = Post.objects.all().order_by('-published')
    paginator = Paginator(post_list, 2) # Show x post per page.
    post_number = request.GET.get('page')
    post = paginator.get_page(post_number)
    category = Category.objects.all()
    access_token = request.session.get('access_token')
    print(access_token)
    context = {
        'post': post,  
        'category': category
    }
    return render(request, 'index.html', context)

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
            print('uploaded')
            url = 'http://43.201.215.208:8000/hongbo/upload_img/'
            print(uploaded_image)
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
            print(parsed_data)
            print('=================')
            print(json_data)
            print(parsed_data)
            print(data_list)
            print('=================')
            # context 변수 선언 및 할당
            context = data_list
            print(type(parsed_data))
            print(type(json_data))
            print(type(decoded_response))
            print(type(data_list))
            return render(request, 'api_result.html', context)
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
        url = 'https://api.kulpick.com/api/v1/product'
        product_list = []  # 음식명과 가격을 번갈아 저장할 리스트
        access_token = request.session.get('access_token')
        print(access_token)
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
            print(item)
            print(type(product_name))
            print(type(normalize_price(product_price)))
            a = normalize_price(product_price)
            data = {
                "storeNo": "210",
                "productName": product_name,
                "price": a,
            }
            print(data)
            response = requests.post(url,headers=headers)
            print(response.text)
        return HttpResponse('제품 업로드가 완료되었습니다.')
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
            return redirect(homepage_views_afterLogin)
        except KeyError:
            print('KeyError')
            # 'accessToken' 키가 없는 경우 '잘못된 로그인 정보입니다' 팝업을 표시하고 현재 페이지에 머무릅니다.
            return render(request, 'wrong_login.html')
        