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
    context = login_check(request)  
    # if request.user.is_authenticated():
    #     print("asd")
    # else:
    #     print("sss")
    #print(request.user)
    
   
    context = {'check' : login_check(request) }
    return render(request, 'app/home.html',context)

def login_check(request):
    context = {}
    if(str(request.user) == "AnonymousUser"):
        context = '2'
    elif(str(request.user) == "admin"):
        context = '3'
    else:
        context = '1'
    return context


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
    'myFilter':myFilter,'check' : login_check(request) }
    
    return render(request, 'app/dashboard.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()

    context ={'customer':customer,'orders':orders,
    'order_count':order_count,'check' : login_check(request) }
    
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
    'total_orders':total_orders, 'check' : login_check(request) }

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
    
    context = {'form':form,'check' : login_check(request) }
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
      context  = {'check' : login_check(request) }
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

   context= {'form':form,'check' : login_check(request) }
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
    context = {'item':order,'check' : login_check(request) }
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
###

typeList = [] #유형분류
nameList = [] #레시피 이름
levelList = [] #난이도
menuImageList = [] #대표 이미지 url
summaryList = []
pkList = []
pkLast = []

typeList2 = []
nameList2 = []
levelList2 = []
menuImageList2 = []
summaryList2 = []
pkList2 = []
pkLast2 =[]

nameLast3 = []
levelLast3 = []
menuImageLast3 = []
summaryLast3 = []
pkLast3 = []
finalLast = []
###



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
    jlist = xmlraw.getElementsByTagName("SUMRY") #요약
    tlist = xmlraw.getElementsByTagName("RECIPE_ID") # pk
    global nameList
    nameList = []
    global menuImageList
    menuImageList = []
    global levelList
    levelList = []
    global typeList
    typeList = []
    global pkList
    pkList = []
    global summaryList
    summaryList = []
    for i in range(len(clist)):
        nameList.insert(i, clist[i].firstChild.data)
        menuImageList.insert(i, blist[i].firstChild.data)
        levelList.insert(i, elist[i].firstChild.data)
        typeList.insert(i, xlist[i].firstChild.data)
        summaryList.insert(i, jlist[i].firstChild.data)
        pkList.insert(i, tlist[i].firstChild.data)
    allDic = {
        'recipeName': nameList,
        'menuImage': menuImageList,
        'level': levelList,
        'summary': summaryList,
        'pk': pkList
    }
    return allDic

def recipeIngredient():
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


    tlist = xmlraw.getElementsByTagName("RECIPE_ID")
    klist = []
    for i in range(len(tlist)):
        klist.insert(i, tlist[i].firstChild.data)

    allDic = {
        'ingredient': alist,
        'id': klist
    }
    return allDic

def recipeProcess():
    api_key = "cbd0c48c7d1cfa5e14f92af7a55ede7b057ca584fdc408b5996526bc55140552"
    api_key_decode = requests.utils.unquote(api_key)
    req = requests.get("http://211.237.50.150:7080/openapi/"+api_key_decode+"/xml/Grid_20150827000000000228_1/1/471")
    xmlraw = minidom.parseString(req.text)
    clist = xmlraw.getElementsByTagName("COOKING_DC") #요리설명
    alist = []
    for i in range(len(clist)):
        alist.insert(i, clist[i].firstChild.data)

    tlist = xmlraw.getElementsByTagName("RECIPE_ID")
    klist = []
    for i in range(len(tlist)):
        klist.insert(i, tlist[i].firstChild.data)
    allDic = {
        'process': alist,
        'id': klist
    }
    return allDic

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
    global summaryList
    global pkList

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
    elif category.nation_nm == "서양":
        for i in range(len(typeList)):
            if typeList[i] == "서양":
                alist.insert(i, i)
    else:
        alist = []
    
    nameLast = [] #조건에 맞는 레시피이름
    levelLast = [] #조건에 맞는 난이도
    menuImageLast = [] #조건에 맞는 레시피 대표 url
    summaryLast = []

    global pkLast
    pkLast = []

    for i in range(len(alist)):
        nameLast.insert(i, nameList[int(alist[i])])
        levelLast.insert(i, levelList[int(alist[i])])
        menuImageLast.insert(i, menuImageList[int(alist[i])])
        summaryLast.insert(i, summaryList[int(alist[i])])
        pkLast.insert(i,pkList[int(alist[i])])

    
    test = [["null" for col in range(5)]for row in range(len(nameLast))]
    for i in range(len(nameLast)):
        test[i][0] = nameLast[i]
        test[i][1] = levelLast[i]
        test[i][2] = menuImageLast[i]
        test[i][3] = summaryLast[i]
        test[i][4] = pkLast[i]
        
    ##########################################

    #난이도 조건에 맞는 리스트들
    alist2 = []

    if category.level_nm == "초보환영":
        for i in range(len(levelList)):
            if levelList[i] == "초보환영":
                alist2.insert(i, i) #초보환영인 인덱스 들어가있음
    elif category.level_nm == "보통":
        for i in range(len(levelList)):
            if levelList[i] == "보통":
                alist2.insert(i, i)
    elif category.level_nm =="어려움":
        for i in range(len(levelList)):
            if levelList[i] == "어려움":
                alist2.insert(i, i)
    else:
        alist2 = []
    
    nameLast2 = [] #조건에 맞는 레시피이름
    levelLast2 = [] #조건에 맞는 난이도
    menuImageLast2 = [] #조건에 맞는 레시피 대표 url
    summaryLast2 = []


    for i in range(len(alist2)):
        nameLast2.insert(i, nameList[int(alist2[i])])
        levelLast2.insert(i, levelList[int(alist2[i])])
        menuImageLast2.insert(i, menuImageList[int(alist2[i])])
        summaryLast2.insert(i, summaryList[int(alist2[i])])
        pkLast2.insert(i,pkList[int(alist2[i])])

    
    test2 = [["null" for col in range(5)]for row in range(len(nameLast2))]
    for i in range(len(nameLast2)):
        test2[i][0] = nameLast2[i]
        test2[i][1] = levelLast2[i]
        test2[i][2] = menuImageLast2[i]
        test2[i][3] = summaryLast2[i]
        test2[i][4] = pkLast2[i]

#############
    global finalLast
    finalLast = []
    key = False
    if category.level_nm and category.nation_nm:
        key = True
        for i in range(len(alist)):
            for j in range(len(alist2)):
                if alist[i] == alist2[j]:
                    finalLast.insert(i, alist[i]) #같은 인덱스 값 들어감
    
    nameLast3 = []
    levelLast3 = []
    menuImageLast3 = []
    summaryLast3 = []
    pkLast3 = []

    for i in range(len(finalLast)):
        nameLast3.insert(i, nameList[int(finalLast[i])])
        levelLast3.insert(i, levelList[int(finalLast[i])])
        menuImageLast3.insert(i, menuImageList[int(finalLast[i])])
        summaryLast3.insert(i, summaryList[int(finalLast[i])])
        pkLast3.insert(i,pkList[int(finalLast[i])])

    test3 = [["null" for col in range(5)]for row in range(len(nameLast3))]
    for i in range(len(nameLast3)):
        test3[i][0] = nameLast3[i]
        test3[i][1] = levelLast3[i]
        test3[i][2] = menuImageLast3[i]
        test3[i][3] = summaryLast3[i]
        test3[i][4] = pkLast3[i]

    if not (category.level_nm or category.nation_nm):
        error_msg = "조건을 입력해주세요"
        return render(request, 'app\error.html',{'error_msg': error_msg} )
    
    if key == True and not(finalLast):
        error_msg = "등록된 레시피가 없습니다."
        return render(request, 'app/error.html', {'error_msg': error_msg})
    else:
        return render(request, 'app/get.html', {'test': test,'test2': test2, 'test3': test3, 'pkLast3': pkLast3})



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

    sslist = xmlraw.getElementsByTagName("SUMRY")

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
      aa.append({"nameList":clist[i].firstChild.data,"menueImageList":blist[i].firstChild.data
      ,"leveList":elist[i].firstChild.data,"typeList":xlist[i].firstChild.data
      , "summaryList": sslist[i].firstChild.data})
    return render(request, 'app/product.html', {'aa':aa })

def detail(request):
    pk = request.GET["pk"]
    
    base = recipeBase()
    nList = base['recipeName']
    iList = base['menuImage']
    lList = base['level']
    sList = base['summary']

    ingredient = recipeIngredient()
    idList = ingredient['id']
    ingList = ingredient['ingredient']
    ingLast = []
    for i in range(len(idList)):
        if idList[i] == pk:
            ingLast.insert(i, ingList[i])

    process = recipeProcess()
    pIdList = process['id']
    plist = process['process']
    pLast = []
    for i in range(len(pIdList)):
        if pIdList[i] == pk:
            pLast.insert(i, plist[i])
    return render(request, 'app\detail.html', {'process': pLast, 'recipeName': nList[int(pk) -1],
        'menuImage': iList[int(pk)-1], 'level': lList[int(pk)-1], 'summary': sList[int(pk) -1],
        'ingLast': ingLast})

def detail(request):
    pk = request.GET["pk"]
    
    base = recipeBase()
    nList = base['recipeName']
    iList = base['menuImage']
    lList = base['level']
    sList = base['summary']

    ingredient = recipeIngredient()
    idList = ingredient['id']
    ingList = ingredient['ingredient']
    ingLast = []
    for i in range(len(idList)):
        if idList[i] == pk:
            ingLast.insert(i, ingList[i])

    process = recipeProcess()
    pIdList = process['id']
    plist = process['process']
    pLast = []
    for i in range(len(pIdList)):
        if pIdList[i] == pk:
            pLast.insert(i, plist[i])
    return render(request, 'app/detail.html', {'process': pLast, 'recipeName': nList[int(pk) -1],
        'menuImage': iList[int(pk)-1], 'level': lList[int(pk)-1], 'summary': sList[int(pk) -1],
        'ingLast': ingLast})