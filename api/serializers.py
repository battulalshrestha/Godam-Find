from rest_framework import serializers
from .models import Tag,Warehouse,CustomUser,WarehouseImage,ProductList,Review,TopWarehouse,BillImage,AddWarehouse
class CustomUserSerializer(serializers.ModelSerializer):
   user_fav_warehouses = serializers.PrimaryKeyRelatedField(many = True,read_only = True)
   class Meta:
         model = CustomUser
         fields  =['id','username','email','password','user_fav_warehouses','groups','user_permissions']
         def to_representation(self, instance):
             if instance is not None:
                 return super().to_representation(instance)
             else:
                    return None
            
class FavoriteWarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id','name','location']

class TagSerializer(serializers.ModelSerializer):
        class Meta:
            model = Tag
            fields = ['id','name']

class ReviewSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    Warehouse_name =serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id','user','rating','review_text','created_at','updated_at','Warehouse_name','Warehouse_id']

    def get_Warehouse_name(self,obj):
        return obj.warehouse.name
class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user','rating','review_text','warehouse']

    def create_or_update_review(self,validated_data):
        user =validated_data['user']
        warehouse = validated_data['warehouse']
        try:
           review = Review.objects.get(user = user,warehouse= warehouse)
        # if the review exists, update the review
           review.rating = validated_data['rating']
           review.review_text = validated_data['review_text']
           review.save()
        except Review.DoesNotExist:
           review = Review.objects.create(**validated_data)
        return review
    def validate(self, data):
        user = data['user']
        warehouse = data['warehouse']
        # check if a review already exists for the user and warehouse combination
        if Review.objects.filter(user = user,warehouse = warehouse).exists():
            return data
        return super().validate(data)

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductList
        fields = ['id','name','price','category']

    
class WarehouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseImage
        fields = ['id','image']

class WarehouseListSerializer(serializers.ModelSerializer):
    images = WarehouseImageSerializer(many = True,read_only = True)

    class Meta:
        model = Warehouse
        fields = ['id','name','location','opening_time','closing_time','description','map_url','tags','images']

class WarehouseDetailSerializer(serializers.ModelSerializer):
    Product_item = BillSerializer(many = True,read_only = True)
    images = WarehouseImageSerializer(many = True,read_only = True)
    average_rating = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many = True,read_only = True)
    no_of_reviews = serializers.SerializerMethodField()
    tags= TagSerializer(many = True,read_only = True)
    class Meta:
        model = Warehouse
        fields = ['id','name','location','description','opening_time','closing_time','price','Product_item','images','average_rating','reviews','no_of_reviews','tags','map_url','tags','Product_item']
    def get_no_of_reviews(self,obj):
        return obj.no_of_reviews()
    def get_average_rating(self,obj):
        return obj.average_rating()
class TopWarehouseSerializer(serializers.ModelSerializer):
    warehouse = WarehouseListSerializer(read_only= False)
    # warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    class Meta:
        model = TopWarehouse
        fields = ['id','warehouse','warehouse','ranking']
    def create(self, validated_data):
        # Extract the 'warehouse' data from the validated data
        warehouse_data = validated_data.pop('warehouse')

        # Create a new Warehouse instance using the extracted data
        warehouse = Warehouse.objects.create(**warehouse_data)

        # Create a new TopWarehouse instance and associate the newly created Warehouse
        top_warehouse = TopWarehouse.objects.create(warehouse=warehouse, **validated_data)

        return top_warehouse
  

class BillImageSerializer(serializers.ModelSerializer):
        class Meta:
            model = BillImage
            fields = ['image']

class AddWarehouseSerializer(serializers.ModelSerializer):
    bill_image = BillImageSerializer(many = True,read_only = True)
    class Meta:
        model = AddWarehouse
        fields = ['id','user','name','location','description','opening_time','closing_time','BillImages']
    def create(self, validated_data):
       bill_images_data =validated_data.pop('BillImages',[])
       warehouse = AddWarehouse.objects.create(**validated_data)
       for image_data in bill_images_data:
            bill_image = BillImage.objects.create(**image_data)
            warehouse.BillImages.add(bill_image)
       return warehouse
           
        