from django.contrib.auth import login
from django.db.models import Func, F, Sum
from django.http import FileResponse
from rest_framework import permissions, generics, status, views, filters
from rest_framework.response import Response
from datetime import datetime, date
from django.conf import settings
from .models import User, Organization, OrganizationWorkTime, WorkTime
from .serializers import UserSerializer, OrganizationsSerializer, OrganizationWorkTimeSerializer, LoginSerializer, \
    WorkTimeSerializer
import qrcode as qr


# url provided
class HelloView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        return Response('Hello, world')


# url provided
class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, formate=None):
        serializer = LoginSerializer(data=self.request.data, context={'request': self.request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


# url provided, for admin
class UserListView(generics.ListAPIView):
    permissions_classes = (permissions.IsAdminUser,)
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        queryset = User.objects.all()
        organization = self.request.query_params.get('organization')
        query_date = self.request.query_params.get('date')
        if organization is not None:
            queryset = queryset.filter(organizations__name=organization)
        if query_date is not None:
            queryset = queryset.filter(userworktime__created_at__date=query_date)
        # queryset.order_by('pk')
        return queryset


# url provided
class GenerateQR(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        current_user = request.user
        if Organization.objects.filter(pk=pk).exists() and Organization.objects.get(pk=pk).email == current_user.email:

            organization = Organization.objects.get(pk=pk)
            print(organization.pk)
            url = settings.SITE_URL + "organizations/" + str(organization.pk) + '/checkin/'
            qr_img = qr.make(url)
            qr_img_name = organization.name + '_qr.png'
            qr_img.save(str(settings.MEDIA_ROOT) + '/qrs/' + qr_img_name)
            response = FileResponse(open(str(settings.MEDIA_ROOT) + '/qrs/' + qr_img_name, 'rb'),
                                    content_type='image/png')

            response['Content-Disposition'] = "attachment; filename=%s" % qr_img_name
            return response
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)


# url provided
class CheckinView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        requesting_user = request.user
        if Organization.objects.filter(pk=pk).exists():
            organization = Organization.objects.get(pk=pk)
            if WorkTime.objects.filter(organization=organization).filter(user=requesting_user).filter(
                    created_at__date=date.today()).exists():
                worktime = WorkTime.objects.filter(organization=organization).filter(user=requesting_user).filter(
                    created_at__date=date.today())[0]
                if worktime.end_time is not None:
                    return Response(None, status=status.HTTP_400_BAD_REQUEST)
                else:
                    worktime.end_time = datetime.now()
                    worktime.save()
                    return Response("Exit time registered", status=status.HTTP_200_OK)
            else:
                worktime = WorkTime(user=requesting_user, organization=organization)
                worktime.save()
                return Response("Enter time registered", status=status.HTTP_200_OK)


# url provided
class UserListViewOrganization(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        current_user = self.request.user
        orgpk = self.kwargs['pk']
        queryset = []
        if Organization.objects.filter(pk=orgpk).exists() and Organization.objects.get(
                pk=orgpk).email == current_user.email:
            organization = Organization.objects.get(pk=orgpk)

            queryset = User.objects.filter(organizations=organization)

            query_date = self.request.query_params.get('date')

            if query_date is not None:
                queryset = queryset.filter(userworktime__created_at__date=query_date)

        return queryset


# url provided
class WorktimeListView(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = WorkTimeSerializer

    def get_queryset(self):
        queryset = WorkTime.objects.all()
        organization = self.request.query_params.get('organization')
        query_date = self.request.query_params.get('date')
        if organization is not None:
            queryset = queryset.filter(organization__name=organization)
        if query_date is not None:
            queryset = queryset.filter(created_at__date=query_date)
        return queryset


# url provided
class WorktimeListViewOrg(generics.ListAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkTimeSerializer

    def get_queryset(self):
        orgpk = self.kwargs['pk']
        current_user = self.request.user
        if Organization.objects.filter(pk=orgpk).exists() and Organization.objects.get(
                pk=orgpk).email == current_user.email:
            organization = Organization.objects.get(pk=orgpk)
            query_date = self.request.query_params.get('date')
            queryset = WorkTime.objects.filter(organization=organization)
            if query_date is not None:
                queryset = queryset.filter(created_at__date=query_date)
            return queryset


class MonthTotalWorkView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):

        current_user = request.user
        if Organization.objects.filter(pk=pk).exists() and Organization.objects.get(pk=pk).email == current_user.email:
            organization = Organization.objects.get(pk=pk)
            year = request.query_params.get('year')
            month = request.query_params.get('month')
            queryset = WorkTime.objects.filter(organization=organization)
            user_mail = request.query_params.get('user')
            if user_mail is not None:
                user = User.objects.filter(email=user_mail)[0]
                queryset = queryset.filter(user=user)
                if year is not None and month is not None:
                    result = queryset.annotate(
                        duration=Func(F('end_time'), F('start_time'), function='age')
                    ).aggregate(Sum('duration'))
                    td = result['duration__sum']
                    return Response(f'"duration__sum":"{td.seconds // 3600} hours, {td.seconds // 60 % 60} minutes"', status=status.HTTP_200_OK)
                else:
                    raise Exception("provide year and month to query")
            else:
                raise Exception("provide user email to query")




# url provided
class OrganizationsView(generics.ListAPIView):
    permissions_classes = (permissions.IsAdminUser,)
    serializer_class = OrganizationsSerializer
    queryset = Organization.objects.all()
