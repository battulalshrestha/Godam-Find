from rest_framework import viewsets
from .models import Tag,Warehouse,CustomUser,WarehouseImage,ProductList,Review,TopWarehouse,BillImage,AddWarehouse
from .serializers import TagSerializer,CustomUserSerializer,WarehouseImageSerializer,BillSerializer,ReviewSerializer,TopWarehouseSerializer,BillImageSerializer,AddWarehouseSerializer,WarehouseListSerializer,WarehouseDetailSerializer,CreateReviewSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from .models import Tag
from django.db.models import Count, Q,Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from rest_framework import  status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.parsers import MultiPartParser,FormParser
import requests
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseListSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WarehouseDetailSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
         queryset = super().get_queryset()
         user_id = self.request.query_params.get('user_id')
         recommand = self.request.query_params.get('recommand')=="true"
         tags = self.request.query_params.get('tags')
         if recommand:
             if user_id:
                 user = get_object_or_404(CustomUser,id = user_id)
                 queryset = self.get_recommend_warehouses(user)

             else:
                 raise NotFound(detail="User id is required for recommandations")
         elif tags:
             queryset = queryset.annotate(matching_tags_count= Count('tags',filter=Q(tags__name__in=tags.split(',')))).order_by('-matching_tags_count','id')
         return queryset
    def get_recommended_warehouses(self,user):
        user_favorites = user.favorite_warehouses.all()
        print(f'User favorites: {user_favorites}')
        user_reviews = Review.objects.filter(user = user)
        print(f'User reviews: {user_reviews}')
        similar_users = CustomUser.objects.filter(Q(favorite_warehouses__in = user_favorites) | Q(reviewss_warehouse__in = [review.warehouse for review in user_reviews])).exclude(id = user.id).distinct()
        print(f'Similar users: {similar_users}')

        collaborative_recommendations = Warehouse.objects.filter(Q(favorited_by__in = similar_users) | Q(reviews__user__in = similar_users)).exclude(favorited_by = user).exclude(Q(favorited_by= user) | Q(reviews__user = user)).distinct()
        print(f'Collaborative recommendations: {collaborative_recommendations}')
        user_tags = Tag.objects.filter(warehouses__in = user_favorites).distinct()
        print(f'User tags: {user_tags}')
        content_recommendations = Warehouse.objects.filter(tags__in = user_tags).exclude(favorited_by = user).exclude(Q(favorited_by = user) | Q(reviews__user = user)).distinct()
        print(f'Content recommendations: {content_recommendations}')
        recommended_warehouses = (collaborative_recommendations | content_recommendations).distinct()
        print(f'Recommended warehouses: {recommended_warehouses}')
        recommended_warehouses = recommended_warehouses.annotate(avg_rating = Avg('reviews__rating'),no_of_reviews = Count('reviews')).order_by('-avg_rating','-no_of_reviews')
        print(f'Recommended warehouses: {recommended_warehouses}')
        return recommended_warehouses

class TopWarehouseViewSet(viewsets.ModelViewSet):
    queryset = TopWarehouse.objects.all()
    serializer_class = TopWarehouseSerializer
    
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class GoogleLoginView(APIView):
    def post(self,request):
        token = request.data.get('token')
        if not token:
            return Response({'error':'Token is required'},status = status.HTTP_400_BAD_REQUEST)
        # fetch the user info using google access token

        try:
            user_info_response = requests.get(f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}')
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
        except requests.exceptions.RequestException as e:
            return Response({'error':'Invalid token'},status = status.HTTP_400_BAD_REQUEST)
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        profile_pic = user_info.get('picture')
        username = user_info.get('name')
        if not google_id or not email:
            return Response({'error':'Incomplete user information from the google'},status = status.HTTP_400_BAD_REQUEST)
        user, created = CustomUser.objects.get_or_create(google_id = google_id, defaults={'email':email,'username':username,'profile_pic':profile_pic})
        if created:
            user.set_unusable_password()
            user.save()
        serializer = CustomUserSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)  
    
class GoogleLoginTestView(APIView):
    def post(self,request):
        print("Request to retrieve user data:",request.data)
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'error':'Token is required'},status = status.HTTP_400_BAD_REQUEST)
        # simulate a successful response from google
        user_data = {
            'id':'test_user_id',
            'username':'test_user',
            'email':'test_user@example.com',
            'profile_pic':'https://example.com/test_user.jpg'


        }
        return Response(user_data,status=status.HTTP_200_OK)
class CreateReviewAPIView(APIView):
    def post(self,request):
        serializer = CreateReviewSerializer(data = request.data)
        if serializer.is_valid():
            review = serializer.create_or_update_review(serializer.validated_data)
            return Response(CreateReviewSerializer(review).data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserReviewsAPIView(APIView):
    def get(self,request,user_id):
        reviews = Review.objects.filter(user_id = user_id)
        if not reviews.exists():
           return Response({'error':'No reviews found'},status = status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(reviews,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
class AddToFavoritesAPIView(APIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        warehouse_id = request.data.get('warehouse_id')
        try:
           user = CustomUser.objects.get(id = user_id)
           warehouse = Warehouse.objects.get(id = warehouse_id)
           if warehouse not in user.favorite_warehouses.all():
             user.favorite_warehouses.add(warehouse)
             user.save()
             print(f'{user.username} added {warehouse.name} to favorites')
             return Response({'message':'Warehouse added to favorites'},status = status.HTTP_200_OK)
           else:
             return Response({'message':'Warehouse already in favorites'},status = status.HTTP_400_BAD_REQUEST)
           
        except CustomUser.DoesNotExist:
            return Response({'error':'User not found'},status = status.HTTP_404_NOT_FOUND)
        except Warehouse.DoesNotExist:
            return Response({'error':'Warehouse not found'},status = status.HTTP_404_NOT_FOUND) 
        
class RemoveFromFavoritesAPIView(APIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        warehouse_id = request.data.get('warehouse_id')
        try:
           user = CustomUser.objects.get(id = user_id)
           warehouse = Warehouse.objects.get(id = warehouse_id)
           if warehouse in user.favorite_warehouses.all():
             user.favorite_warehouses.remove(warehouse)
             user.save()
             print(f'{user.username} removed {warehouse.name} from favorites')
             return Response({'message':'Warehouse removed from favorites'},status = status.HTTP_200_OK)
           else:
             return Response({'message':'Warehouse not in favorites'},status = status.HTTP_400_BAD_REQUEST)
           
        except CustomUser.DoesNotExist:
            return Response({'error':'User not found'},status = status.HTTP_404_NOT_FOUND)
        except Warehouse.DoesNotExist:
            return Response({'error':'Warehouse not found'},status = status.HTTP_404_NOT_FOUND)
        


class FavoriteWarehouseAPIView(APIView):

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            favorite_warehouses= user.favorite_warehouses.all()
            print(f"Favorite warehouses for user {user_id}: {favorite_warehouses}")
            serializer = FavoriteWarehouseAPIView(favorite_warehouses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class AddWarehouseView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request,*args,**kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error':'User id is required'},status = status.HTTP_400_BAD_REQUEST)
        warehouse_data = {
            'name':request.data.get('name'),
            'location':request.data.get('location'),
            'description':request.data.get('description'),
            'opening_time':request.data.get('opening_time'),
            'closing_time':request.data.get('closing_time'),
            'tags':request.data.get('tags'),
            'images':request.data.getlist('images'),
            'user_id':user_id,

        }
        serializer = AddWarehouseSerializer(data = warehouse_data)
        if not serializer.is_valid():
            return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
        warehouse = serializer.save()
        Bill_imgs = []
        for key, file in request.FILES.items():
            if key.startswith('bill_'):
               bill_img = BillImage.objects.create(image =file)
               Bill_imgs.append(bill_img)
        # add the images to the warehouse
        
        warehouse.Bill_imgs.set(Bill_imgs)
        warehouse.save()
        return Response(serializer.data,status = status.HTTP_201_CREATED)
    
class UserRequestWarehouseAPIView(APIView):
    serializer_class =AddWarehouseSerializer
    def get_queryset(self):
        user_id =self.kwargs.get('user_id')
        if not user_id:
            return AddWarehouse.objects.none()
        try:
            return AddWarehouse.objects.filter(user_id = user_id)
        except Exception as e:
            print(f'Error fetching user requests: {e}')
            return AddWarehouse.objects.none()
        