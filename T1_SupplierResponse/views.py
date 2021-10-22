from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
#from .models import Category, Writer, Book, Review, Slider
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
#from .forms import RegistrationForm, ReviewForm
from django.shortcuts import render_to_response
import cx_Oracle
#获取操作数据库锚点
def get_cursor():
    connection = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
    return connection.cursor()

def dict_fetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
from collections import namedtuple

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    cursor = get_cursor()
    cursor.execute("select pmaal004,pmdn001,imaal003,imaal004,pmdn006, pmdn007, pmdn220 from pmdn_t inner join  pmdl_t on pmdldocno=pmdndocno inner join imaal_t on imaal001=pmdn001 inner join pmaal_t on pmaal001=pmdl004  where rownum<=10")
    Result = cursor.fetchall()
    #Result = dict(cursor.fetchall())
    #Result = dict_fetchall(cursor)
    print(Result)
    cursor.close()
    return render_to_response('test.html', {"Order": Result})
    #return render(request, 'test.html', {"Order": Order})

from django.http import HttpResponse

# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")
# def get_sale_detail():
#     connection = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
#     cursor = connection.cursor()
#     cmd_query = query_data(request)
#     data_sort = sort_data(request)
#     cmd = "set session group_concat_max_len = 8000;"
#     cursor.execute(cmd)
#
#     cursor.execute("SELECT distinct sale_order.id,res_partner.ref FROM sale_order left join res_partner on res_partner.id=sale_order.partner_id  order by sale_order.id desc limit 10")
#     res = cursor.fetchall()
#     for tao in res:
#         row = tao[0]
#
# def signin(request):
#     if request.user.is_authenticated:
#         return redirect('store:index')
#     else:
#         if request.method == "POST":
#             user = request.POST.get('user')
#             password = request.POST.get('pass')
#             auth = authenticate(request, username=user, password=password)
#             if auth is not None:
#                 login(request, auth)
#                 return redirect('store:index')
#             else:
#             	messages.error(request, 'username and password doesn\'t match')
#
#     return render(request, "store/login.html")
#
#
# def signout(request):
#     logout(request)
#     return redirect('store:index')
#
#
# def registration(request):
# 	form = RegistrationForm(request.POST or None)
# 	if form.is_valid():
# 		form.save()
# 		return redirect('store:signin')
#
# 	return render(request, 'store/signup.html', {"form": form})
#
# def payment(request):
#     return render(request, 'store/payment.html')
#
#
# def get_book(request, id):
#     form = ReviewForm(request.POST or None)
#     book = get_object_or_404(Book, id=id)
#     rbooks = Book.objects.filter(category_id=book.category.id)
#     r_review = Review.objects.filter(book_id=id).order_by('-created')
#
#     paginator = Paginator(r_review, 4)
#     page = request.GET.get('page')
#     rreview = paginator.get_page(page)
#
#     if request.method == 'POST':
#         if request.user.is_authenticated:
#             if form.is_valid():
#                 temp = form.save(commit=False)
#                 temp.customer = User.objects.get(id=request.user.id)
#                 temp.book = book
#                 temp = Book.objects.get(id=id)
#                 temp.totalreview += 1
#                 temp.totalrating += int(request.POST.get('review_star'))
#                 form.save()
#                 temp.save()
#
#                 messages.success(request, "Review Added Successfully")
#                 form = ReviewForm()
#         else:
#             messages.error(request, "You need login first.")
#     context = {
#         "book":book,
#         "rbooks": rbooks,
#         "form": form,
#         "rreview": rreview
#     }
#     return render(request, "store/book.html", context)
#
#
# def get_books(request):
#     books_ = Book.objects.all().order_by('-created')
#     paginator = Paginator(books_, 10)
#     page = request.GET.get('page')
#     books = paginator.get_page(page)
#     return render(request, "store/category.html", {"book":books})
#
# def get_book_category(request, id):
#     book_ = Book.objects.filter(category_id=id)
#     paginator = Paginator(book_, 10)
#     page = request.GET.get('page')
#     book = paginator.get_page(page)
#     return render(request, "store/category.html", {"book":book})
#
# def get_writer(request, id):
#     wrt = get_object_or_404(Writer, id=id)
#     book = Book.objects.filter(writer_id=wrt.id)
#     context = {
#         "wrt": wrt,
#         "book": book
#     }
#     return render(request, "store/writer.html", context)':'ran safari successful'})