from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Product(models.Model):
	CATEGORY = (
			('한식', '한식'), 
			('퓨전', '퓨전'),
            ('서양', '퓨전'),
            ('일본','일본'),
            ('이탈리아', '이탈리아'),
            ('동남아시아', '동남아시아'),
		) 

	name = models.CharField(max_length=200, null=True)
	price = models.FloatField(null=True)
	category = models.CharField(max_length=200, null=True, choices=CATEGORY)
	date_created = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return self.name

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	phone = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True)
	date_created = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return self.name

class Order(models.Model):
	STATUS = (
			('제품준비중', '제품준비중'),
			('배송중', '배송중'),
			('배송완료', '배송완료'),
			)

	customer = models.ForeignKey(Customer, null=True, on_delete= models.SET_NULL)
	product = models.ForeignKey(Product, null=True, on_delete= models.SET_NULL)
	date_created = models.DateTimeField(auto_now_add=True, null=True)
	status = models.CharField(max_length=200, null=True, choices=STATUS)

	def __str__(self):
		return self.product.name


class Category(models.Model):
    level_nm = models.CharField(max_length=1000) #난이도 #레시피기본정보
    calorie = models.CharField(max_length=1000)  #칼로리 #레시피기본정보
    nation_nm = models.CharField(max_length=1000) #유형분류 #레시피기본정보
    cooking_time = models.CharField(max_length=1000) #조리시간 #레시피기본정보


class Detail(models.Model):
    recipe_nm_ko = models.CharField(max_length=1000) #레시피 이름 #레시피기본정보
    cooking_dc = models.CharField(max_length=100000) #요리설명 #레시피과정정보
    irdnt_nm = models.CharField(max_length=10000) #재료명 #레시피재료정보
    stre_step_image_url = models.CharField(max_length=100000) #과정 이미지 URL #레시피과정정보


