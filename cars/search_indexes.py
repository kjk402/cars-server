from elasticsearch_dsl import Document, Text, Integer, Float
from django_elasticsearch_dsl import Index
from .models import Car

cars_index = Index('cars')

@cars_index.doc_type
class CarDocument(Document):
    brand = Text()
    model = Text()
    year = Integer()
    price = Integer()
    transmission = Text()
    mileage = Integer()
    fuelType = Text()
    tax = Integer()
    mpg = Float()
    engineSize = Float()

    class Index:
        name = 'cars'
