from django.urls import path

from .views import (
    CarSearchView,
    TopBrandsView,
    PriceDistributionView,
    DepreciationView,
    SimilarCarsView,
    FilteredCarSearchView,
    BrandModelsView,
    BrandAvgPriceView
)

urlpatterns = [
    path('search/', CarSearchView.as_view(), name="car-search"),

    path('top-brands/', TopBrandsView.as_view(), name="top-brands"),
    path('price-distribution/', PriceDistributionView.as_view(), name="price-distribution"),
    path('depreciation/', DepreciationView.as_view(), name="depreciation"),
    path('similar/', SimilarCarsView.as_view(), name="similar-cars"),  # ✅ 유사 차량 추천 API
    path('filter-search/', FilteredCarSearchView.as_view(), name="filter-search"),  # ✅ 필터링 및 정렬 API
    path('brand-models/', BrandModelsView.as_view(), name="brand-models"),  # ✅ 특정 브랜드 모델 조회

    path("brand-avg-prices/", BrandAvgPriceView.as_view(), name="brand-avg-prices"),

]
