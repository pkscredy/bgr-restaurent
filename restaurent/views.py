import csv
import arrow
import requests
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from restaurent.constants import (
    DETAILS_URL,
    key,
    RestaurentConstants,
    SEARCH_URL,
    TEMPLATE_URL
)
from restaurent.models import ResData
from django.views.generic import View


class HomeView(View):
    def get(self, request):
        """
        this is rendering the restaurents data for user 15 restaurents per
        page
        """
        objs = ResData.objects.all()
        paginator = Paginator(objs, 15)  # Show 15 Reataurents per page
        page = request.GET.get('page')
        try:
            restaurents = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            restaurents = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            restaurents = paginator.page(paginator.num_pages)

        return render(request, TEMPLATE_URL, {'res_info': restaurents})

    def post(self, request):
        """
        display the restaurent on google map(using google map api) as per
        the request from template
        """
        post_data = request.POST.dict()
        search_payload = {
            'key': key,
            'query': post_data['location']+' bangalore'
        }
        search_req = requests.get(SEARCH_URL, params=search_payload)
        search_json = search_req.json()

        place_id = search_json['results'][0]['place_id']

        details_payload = {'key': key, 'placeid': place_id}
        details_resp = requests.get(DETAILS_URL, params=details_payload)
        details_json = details_resp.json()
        url = details_json['result']['url']
        return HttpResponseRedirect(url)

    def get_data_from_csv(self):
        """
        reading the restaurent data from csv and return a list of obj
        """
        res_list = []
        with open(RestaurentConstants.DATA_WITH_REVIEW, 'r',
                  encoding='ascii', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            created_at = arrow.utcnow().datetime
            for row in reader:
                res_list.append(ResData(
                    url=row['Url'],
                    name=row['Name'],
                    location=row['Address'],
                    review=row['Review'],
                    rating=row['Rating'],
                    created_at=created_at,
                    modified_at=created_at,
                ))
        return res_list

    def insert_restaurent_detail(self):
        """
        inserts the list of objects into the database.In single query 100 objs
        which no leads any memory error
        """
        res_list = self.get_data_from_csv()
        ResData.objects.bulk_create(res_list, batch_size=100)
