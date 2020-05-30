from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)

from urllib.parse import quote_plus
import json
import datetime
import base64

from .models import Oficio, OficioOwner, Category
from .forms import OficioForm

from core.utils import text_to_image, image_to_base64

# Create your views here.
def set_owner_and_update_values(request, new_help_request):
    if 'user' in request.ayuda_session and request.ayuda_session['user'] is not None:
        user = request.ayuda_session['user']
        oficio_owner = OficioOwner()
        oficio_owner.oficio = new_help_request
        oficio_owner.user_iid = user
        oficio_owner.save()

        # try to update user values
        if user.name is None:
            user.name = oficio_owner.help_request.name
            user.city = oficio_owner.help_request.city
            user.city_code = oficio_owner.help_request.city_code
            user.phone = oficio_owner.help_request.phone
            user.address = oficio_owner.help_request.address
            user.location = oficio_owner.help_request.location
            user.save()

def oficio_form(request):
    
    if request.method == "POST":
        form = OficioForm(request.POST, request.FILES)
        if form.is_valid():
            new_oficio = form.save()
            try:
                set_owner_and_update_values(request, new_oficio)
            except Exception as e:
                # ignore if we can't set the help_request_ownser
                print(str(e))
            messages.success(request, "¡Se creó tu oficio exitosamente!")
            return redirect("oficio-detail", id=new_oficio.id)
    else:
        form = OficioForm()

    categories = Category.objects.filter(active=True)
    selected_categories = []
    if form.is_bound:
        for field in form.visible_fields():
            if field.name == 'categories':
                for category in field.subwidgets:
                    if category.data['selected']:
                        selected_categories.append(category.data['value'])
                break

    context = {"form": form, 'selected_categories': selected_categories, 'categories': categories}
    return render(request, "oficios/create.html", context)


def view_oficio(request, id):
    oficio = get_object_or_404(Oficio, pk=id)
    active_oficios = []
    if not oficio.active:
        active_oficios = Oficio.objects.filter(phone=oficio.phone, active=True).order_by('-pk')
    vote_ctrl = {}
    vote_ctrl_cookie_key = 'votectrl'
    # cookie expiration
    dt = datetime.datetime(year=2067, month=12, day=31)

    context = {
        "oficio": oficio,
        "name": oficio.name,
        "thumbnail": oficio.thumb if oficio.picture else "/static/img/logo.jpg",
        "phone_number_img": image_to_base64(text_to_image(oficio.phone, 300, 50)),
        "whatsapp": '595'+oficio.phone[1:]+'?text=Hola+'+oficio.name
                    + ',+te+escribo+por+el+oficio+que+creaste:+'+quote_plus(oficio.title)
                    + '+https:'+'/'+'/'+'ayudapy.org/oficios/'+oficio.id.__str__(),
        "active_oficios": active_oficios,
    }
    if request.POST:
        if request.POST['vote']:
            if vote_ctrl_cookie_key in request.COOKIES:
                try:
                    vote_ctrl = json.loads(base64.b64decode(request.COOKIES[vote_ctrl_cookie_key]))
                except:
                    pass

                try:
                    voteFlag = vote_ctrl["{id}".format(id=oficio.id)]
                except KeyError:
                    voteFlag = None

                if voteFlag is None:
                    if request.POST['vote'] == 'up':
                        oficio.upvotes += 1
                    elif request.POST['vote'] == 'down':
                        oficio.downvotes += 1
                    oficio.save()
                    vote_ctrl["{id}".format(id=oficio.id)] = True

    response = render(request, "oficios/details.html", context)

    if vote_ctrl_cookie_key not in request.COOKIES:
        # initialize control cookie
        if request.POST and request.POST['vote']:
            # set value in POST request if cookie not exists
            b = json.dumps({"{id}".format(id=oficio.id): True}).encode('utf-8')
        else:
            # set empty value in others requests
            b = json.dumps({}).encode('utf-8')
        value = base64.b64encode(b).decode('utf-8')
        response.set_cookie(vote_ctrl_cookie_key, value,
                            expires=dt)
    else:
        if request.POST:
            if request.POST['vote']:
                # update control cookie only in POST request
                b = json.dumps(vote_ctrl).encode('utf-8')
                value = base64.b64encode(b).decode('utf-8')
                response.set_cookie(vote_ctrl_cookie_key, value,
                                    expires=dt)
    return response


def list_oficios(request):
    cities = [(i['city'], i['city_code']) for i in Oficio.objects.all().values('city', 'city_code').distinct().order_by('city_code')]
    categories = Category.objects.filter(active=True)
    context = {"list_cities": cities, "categories": categories}
    return render(request, "oficios/list.html", context)


def list_by_city(request, city):
    list_oficios = Oficio.objects.filter(city_code=city, active=True, resolved=False).order_by("-added")  # TODO limit this
    city = list_oficios[0].city
    query = list_oficios
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))

    page = request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_oficios, paginate_by)
    try:
        list_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_paginated = paginator.page(1)
    except EmptyPage:
        list_paginated = paginator.page(paginator.num_pages)

    context = {"list_oficios": list_oficios, "geo": geo, "city": city, "list_paginated": list_paginated}
    return render(request, "oficios/list_by_city.html", context)
