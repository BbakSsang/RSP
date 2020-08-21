from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from .models import Category, Detail
from .forms import OrderForm,CreateUserForm

from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

from .filters import OrderFilter


from .crawling import book_all

##
from xml.dom import minidom
import requests
##

##
# Create your views here.
def home(request):
    context ={}   
    return render(request, 'app/home.html',context)

@login_required(login_url = 'login')
@admin_only
def adminDashboard(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_orders = orders.count()
    total_customers = customers.count()

    item_ready = orders.filter(status='제품준비중').count()
    riding = orders.filter(status='배송중').count()
    delivered = orders.filter(status='배송완료').count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    print(orders)

    context = {'orders':orders,  'customers':customers,
    'total_customers':total_customers,'delivered':delivered, 
    'riding':riding,'item_ready':item_ready, 'total_orders':total_orders,
    'myFilter':myFilter,}
    
    return render(request, 'app/dashboard.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()

    context ={'customer':customer,'orders':orders,
    'order_count':order_count}
    
    return render(request, 'app/customer.html',context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    
    total_orders = orders.count()
    #total_customers = customers.count()

    item_ready = orders.filter(status='제품준비중').count()
    riding = orders.filter(status='배송중').count()
    delivered = orders.filter(status='배송완료').count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    
    context = {'orders':orders, 'myFilter':myFilter,
    'delivered':delivered,'riding':riding,'item_ready':item_ready,
    'total_orders':total_orders, }

    return render(request, 'app/user.html',context)

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, '계정생성완료 ' + user)

            return redirect('login')
    
    context = {'form':form}
    return render(request, 'app/register.html',context)

@unauthenticated_user
def loginPage(request):
   # if request.user.is_authenticated:
   #    return redirect('home')
   # else:
      if request.method == 'POST':
         username = request.POST.get('username')
         password = request.POST.get('password')

         user = authenticate(request, username=username, password=password)  

         if user is not None:
            login(request, user)
            return redirect('home')
         else:
            messages.info(request,'아이디 혹은 비밀번호가 잘못입력되었습니다!')
      context  = {}
      return render(request, 'app/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request):
   form = OrderForm()
   if request.method == 'POST':
      #print('Printing POST:', request.POST)
      form = OrderForm(request.POST)
      if form.is_valid():
         form.save()
         return redirect('/adminpage')

   context= {'form':form}
   return render(request, 'app/order_form.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')
    context = {'item':order}
    return render(request, 'app/delete.html',context)

def bookFind(request):
    book = book_all(2,3)
    return render(request,'app/book.html',{'book':book })
###

typeList = [] #유형분류
nameList = [] #레시피 이름
levelList = [] #난이도
menuImageList = [] #대표 이미지 url

def recipeBase():
    api_key = "cbd0c48c7d1cfa5e14f92af7a55ede7b057ca584fdc408b5996526bc55140552"
    # URL이 인코딩된 상태로 제공된 KEY이므로 Decoding이 필요
    api_key_decode = requests.utils.unquote(api_key)
    # 위의 명령어로 URL이 제외된 디코딩 코드
    req = requests.get("http://211.237.50.150:7080/openapi/"+api_key_decode+"/xml/Grid_20150827000000000226_1/1/85")
    xmlraw = minidom.parseString(req.text) #문자열을 xml 파싱이 가능한 형식으로 변형
    clist  = xmlraw.getElementsByTagName("RECIPE_NM_KO") #레시피 이름
    blist = xmlraw.getElementsByTagName("IMG_URL") #대표 이미지 url
    elist = xmlraw.getElementsByTagName("LEVEL_NM") #난이도
    xlist = xmlraw.getElementsByTagName("NATION_NM") #유형분류
    global nameList
    nameList = []
    global menuImageList
    menuImageList = []
    global levelList
    levelList = []
    global typeList
    typeList = []
    for i in range(len(clist)):
        nameList.insert(i, clist[i].firstChild.data)
        menuImageList.insert(i, blist[i].firstChild.data)
        levelList.insert(i, elist[i].firstChild.data)
        typeList.insert(i, xlist[i].firstChild.data)
    allDic = {
        'recipeName': nameList,
        'menuImage': menuImageList,
        'level': levelList
    }
    # return render(request, 'app\product.html', {'recipeName': nameList, 'menuImage': menuImageList, 'level': levelList , 'type': typeList})
    return allDic


def recipeIngredient(request):
    api_key = "cbd0c48c7d1cfa5e14f92af7a55ede7b057ca584fdc408b5996526bc55140552"
    # URL이 인코딩된 상태로 제공된 KEY이므로 Decoding이 필요
    api_key_decode = requests.utils.unquote(api_key)
    # 위의 명령어로 URL이 제외된 디코딩 코드
    req = requests.get("http://211.237.50.150:7080/openapi/"+api_key_decode+"/xml/Grid_20150827000000000227_1/1/999")
    xmlraw = minidom.parseString(req.text)
    clist = xmlraw.getElementsByTagName("IRDNT_NM") #재료명
    alist = []
    for i in range(len(clist)):
        alist.insert(i, clist[i].firstChild.data)
    return render(request, 'app\get.html', {'ingredient': alist})

def recipeProcess(request):
    api_key = "cbd0c48c7d1cfa5e14f92af7a55ede7b057ca584fdc408b5996526bc55140552"
    api_key_decode = requests.utils.unquote(api_key)
    req = requests.get("http://211.237.50.150:7080/openapi/"+api_key_decode+"/xml/Grid_20150827000000000228_1/1/471")
    xmlraw = minidom.parseString(req.text)
    clist = xmlraw.getElementsByTagName("COOKING_DC") #요리설명
    alist = []
    for i in range(len(clist)):
        alist.insert(i, clist[i].firstChild.data)
    return render(request, 'app\get.html', {'cookingProcess': alist})

def get(request):
    category = Category()
    category.level_nm = request.GET.get('level_nm') #난이도
    category.calorie = request.GET.get('calorie') #칼로리
    category.nation_nm = request.GET.get('nation_nm') #유형분류
    category.cooking_time = request.GET.get('cooking_time') #조리시간
    detail = Detail()
    detail.irdnt_nm = request.GET.get('irdnt_nm') #재료
    allList = recipeBase()
    alist = []
    global typeList
    global nameList
    global levelList
    global menuImageList

    if category.nation_nm == "한식":
        for i in range(len(typeList)):
            if typeList[i] == "한식":
                alist.insert(i, i) #한식인 인덱스 값 들어있음
    elif category.nation_nm == "중국":
        for i in range(len(typeList)):
            if typeList[i] == "중국":
                alist.insert(i, i)
    elif category.nation_nm == "일본":
        for i in range(len(typeList)):
            if typeList[i] == "일본":
                alist.insert(i, i)
    elif category.nation_nm == "이탈리아":
        for i in range(len(typeList)):
            if typeList[i] == "이탈리아":
                alist.insert(i, i)
    elif category.nation_nm == "동남아시아":
        for i in range(len(typeList)):
            if typeList[i] == "동남아시아":
                alist.insert(i, i)
    elif category.nation_nm == "퓨전":
        for i in range(len(typeList)):
            if typeList[i] == "퓨전":
                alist.insert(i,i)
    else:
        for i in range(len(typeList)):
            if typeList[i] == "서양":
                alist.insert(i, i)
    
    nameLast = [] #조건에 맞는 레시피이름
    levelLast = [] #조건에 맞는 난이도
    menuImageLast = [] #조건에 맞는 레시피 대표 url
    for i in range(len(alist)):
        nameLast.insert(i, nameList[int(alist[i])])
        levelLast.insert(i, levelList[int(alist[i])])
        menuImageLast.insert(i, menuImageList[int(alist[i])])
        #유형 분류 가져오기

    
    test = [["null" for col in range(3)]for row in range(len(nameLast))]
    for i in range(len(nameLast)):
        test[i][0] = nameLast[i]
        test[i][1] = levelLast[i]
        test[i][2] = menuImageLast[i]

    if not (category.level_nm or category.calorie or category.nation_nm or category.cooking_time or detail.irdnt_nm ):
        return render(request, 'app\error.html')
    return render(request, 'app\get.html', {'test': test})

def product(request):
    api_key = "cbd0c48c7d1cfa5e14f92af7a55ede7b057ca584fdc408b5996526bc55140552"
    # URL이 인코딩된 상태로 제공된 KEY이므로 Decoding이 필요
    api_key_decode = requests.utils.unquote(api_key)
    # 위의 명령어로 URL이 제외된 디코딩 코드
    req = requests.get("http://211.237.50.150:7080/openapi/"+api_key_decode+"/xml/Grid_20150827000000000226_1/1/85")
    xmlraw = minidom.parseString(req.text) #문자열을 xml 파싱이 가능한 형식으로 변형
    clist  = xmlraw.getElementsByTagName("RECIPE_NM_KO") #레시피 이름
    blist = xmlraw.getElementsByTagName("IMG_URL") #대표 이미지 url
    elist = xmlraw.getElementsByTagName("LEVEL_NM") #난이도
    xlist = xmlraw.getElementsByTagName("NATION_NM") #유형분류
    global nameList
    nameList = []
    global menuImageList
    menuImageList = []
    global levelList
    levelList = []
    global typeList
    typeList = []

    aa=[]
    for i in range(len(clist)):
      aa.append({"nameList":clist[i].firstChild.data,"menueImageList":blist[i].firstChild.data,"leveList":elist[i].firstChild.data,"typeList":xlist[i].firstChild.data})
    return render(request, 'app\product.html', {'aa':aa })
