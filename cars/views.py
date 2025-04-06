import os
import base64
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch import Elasticsearch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

es = Elasticsearch(settings.ELASTICSEARCH_HOST)  # Elasticsearch 서버 주소

class CarSearchView(APIView):
    # Swagger 문서화 추가
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY, description="검색어 (브랜드, 모델, 연료 유형, 변속기)",
                type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={200: "검색 결과 반환"}
    )
    def get(self, request):
        query = request.GET.get("q", "")  # 검색어 가져오기
        if not query:
            return Response({"error": "검색어를 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)

        # Elasticsearch 검색 쿼리
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["brand", "model", "fuelType", "transmission"]
                }
            },
            "size": 100
        }

        results = es.search(index="cars", body=body)
        return Response(results["hits"]["hits"], status=status.HTTP_200_OK)


BRAND_LOGOS = {
    "ford": "/static/logos/ford.png",
    "volkswagen": "/static/logos/volkswagen.png",
    "vauxhall": "/static/logos/vauxhall.png",
    "mercedes": "/static/logos/mercedes.png",
    "bmw": "/static/logos/bmw.png",
    "audi": "/static/logos/audi.png",
    "toyota": "/static/logos/toyota.png",
    "skoda": "/static/logos/skoda.png",
    "hyundi": "/static/logos/hyundi.png",
    "cclass": "/static/logos/cclass.png",
}

def get_base64_image(brand):
    """ 브랜드 로고를 Base64로 변환하여 반환 """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "static", "logos", f"{brand.lower()}.png")

    print(f"🔍 Checking logo path: {logo_path}")  # ✅ 경로 확인용 로그 추가

    if os.path.exists(logo_path):  # 파일 존재 여부 확인
        with open(logo_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    print(f"🚨 Logo not found: {logo_path}")  # ✅ 파일이 없을 경우 로그 출력
    return None  # 로고 이미지 없으면 None 반환



# 가장많이 등록된 top10
class TopBrandsView(APIView):
    @swagger_auto_schema(
        responses={200: openapi.Response("가장 많이 등록된 브랜드 리스트 (Base64 로고 포함)")}
    )
    def get(self, request):
        body = {
            "size": 0,
            "aggs": {
                "top_brands": {
                    "terms": {
                        "field": "brand",
                        "size": 10
                    }
                }
            }
        }
        results = es.search(index="cars", body=body)
        brands = []

        for bucket in results["aggregations"]["top_brands"]["buckets"]:
            brand_name = bucket["key"]
            brand_logo = get_base64_image(brand_name)  # ✅ Base64 변환된 이미지 가져오기
            brand_count = bucket["doc_count"]
            brands.append({
                "brand": brand_name,
                "logo": brand_logo if brand_logo else "No Image",  # 로고가 없을 경우 메시지 추가
                "count": brand_count
            })

        return Response({"top_brands": brands}, status=status.HTTP_200_OK)




class PriceDistributionView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('brand', openapi.IN_QUERY, description="브랜드명", type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: openapi.Response("가격 분포 데이터")}
    )
    def get(self, request):
        brand = request.GET.get("brand", "")
        if not brand:
            return Response({"error": "브랜드명을 입력하세요"}, status=400)

        body = {
            "size": 0,
            "query": {"term": {"brand": brand}},
            "aggs": {
                "price_distribution": {
                    "histogram": {
                        "field": "price",
                        "interval": 5000
                    }
                }
            }
        }
        results = es.search(index="cars", body=body)
        distribution = [
            {"price_range": bucket["key"], "count": bucket["doc_count"]}
            for bucket in results["aggregations"]["price_distribution"]["buckets"]
        ]
        return Response({"brand": brand, "price_distribution": distribution})


class DepreciationView(APIView):
    @swagger_auto_schema(
        responses={200: openapi.Response("연식별 평균 가격 변화")}
    )
    def get(self, request):
        body = {
            "size": 0,
            "aggs": {
                "yearly_price": {
                    "terms": {
                        "field": "year",
                        "size": 200,
                        "order": {"_key": "asc"}
                    },
                    "aggs": {
                        "avg_price": {"avg": {"field": "price"}}
                    }
                }
            }
        }
        results = es.search(index="cars", body=body)
        depreciation = [
            {"year": bucket["key"], "avg_price": bucket["avg_price"]["value"]}
            for bucket in results["aggregations"]["yearly_price"]["buckets"]
        ]
        return Response({"depreciation": depreciation})


# 유사 차량 추천
class SimilarCarsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('car_id', openapi.IN_QUERY, description="기준 차량 ID", type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: openapi.Response("유사 차량 리스트")}
    )
    def get(self, request):
        car_id = request.GET.get("car_id", "")
        if not car_id:
            return Response({"error": "차량 ID를 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)

        body = {
            "query": {
                "more_like_this": {
                    "fields": ["brand", "model", "fuelType"],
                    "like": [{"_id": car_id}],
                    "min_term_freq": 1,
                    "max_query_terms": 10
                }
            },
            "size": 5
        }

        results = es.search(index="cars", body=body)
        return Response(results["hits"]["hits"], status=status.HTTP_200_OK)


class FilteredCarSearchView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('brand', openapi.IN_QUERY, description="브랜드", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('model', openapi.IN_QUERY, description="모델", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('fuelType', openapi.IN_QUERY, description="연료 유형", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="최소 가격", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="최대 가격", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('year', openapi.IN_QUERY, description="연식", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('sort', openapi.IN_QUERY, description="정렬 (price_asc, price_desc, year_asc, year_desc, mileage_asc, mileage_desc)", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('page', openapi.IN_QUERY, description="페이지 번호 (1부터 시작)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('size', openapi.IN_QUERY, description="페이지 당 결과 수", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={200: openapi.Response("필터링된 차량 리스트")}
    )
    def get(self, request):
        filters = []
        sort_option = request.GET.get("sort", "price_asc")

        # 페이징 파라미터
        try:
            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 20))
        except ValueError:
            return Response({"error": "page와 size는 정수여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        from_index = (page - 1) * size

        # 필터 추가
        if "brand" in request.GET:
            filters.append({"term": {"brand": request.GET["brand"]}})
        if "model" in request.GET:
            filters.append({"term": {"model": request.GET["model"]}})
        if "fuelType" in request.GET:
            filters.append({"term": {"fuelType": request.GET["fuelType"]}})
        if "min_price" in request.GET:
            filters.append({"range": {"price": {"gte": request.GET["min_price"]}}})
        if "max_price" in request.GET:
            filters.append({"range": {"price": {"lte": request.GET["max_price"]}}})
        if "year" in request.GET:
            filters.append({"range": {"year": {"gte": request.GET["year"]}}})

        # 정렬 옵션 처리
        sort_mapping = {
            "price_asc": {"price": "asc"},
            "price_desc": {"price": "desc"},
            "year_asc": {"year": "asc"},
            "year_desc": {"year": "desc"},
            "mileage_asc": {"mileage": "asc"},
            "mileage_desc": {"mileage": "desc"}
        }
        sort_query = [sort_mapping.get(sort_option, {"price": "asc"})]

        body = {
            "query": {
                "bool": {
                    "must": filters
                }
            },
            "sort": sort_query,
            "from": from_index,
            "size": size
        }

        results = es.search(index="cars", body=body)

        response_data = {
            "results": results["hits"]["hits"],
            "total": results["hits"]["total"]["value"],
            "page": page,
            "size": size
        }

        return Response(response_data, status=status.HTTP_200_OK)

# 브랜드별 모델 검색
class BrandModelsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('brand', openapi.IN_QUERY, description="브랜드명", type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: openapi.Response("특정 브랜드의 모델 리스트 (모델별 등록 수 포함)")},
    )
    def get(self, request):
        brand = request.GET.get("brand", "")

        if not brand:
            return Response({"error": "브랜드명을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # Elasticsearch Aggregation 쿼리
        body = {
            "size": 0,
            "query": {
                "term": {
                    "brand": brand
                }
            },
            "aggs": {
                "models": {
                    "terms": {
                        "field": "model",
                        "size": 50  # 모델 최대 수
                    }
                }
            }
        }

        results = es.search(index="cars", body=body)

        models = [
            {
                "model": bucket["key"].strip(),  # ✅ 양쪽 공백 제거
                "model_count": bucket["doc_count"]
            }
            for bucket in results["aggregations"]["models"]["buckets"]
        ]

        return Response({"brand": brand, "models": models}, status=status.HTTP_200_OK)



class BrandAvgPriceView(APIView):
    @swagger_auto_schema(
        responses={200: openapi.Response("브랜드별 평균 가격 리스트 (Top 5)")}
    )
    def get(self, request):
        body = {
            "size": 0,
            "aggs": {
                "brands": {
                    "terms": {
                        "field": "brand",
                        "size": 5,  # top 5 브랜드
                        "order": { "avg_price": "desc" }
                    },
                    "aggs": {
                        "avg_price": {
                            "avg": { "field": "price" }
                        }
                    }
                }
            }
        }

        results = es.search(index="cars", body=body)

        brand_prices = [
            {
                "brand": bucket["key"],
                "avg_price": round(bucket["avg_price"]["value"], 2)
            }
            for bucket in results["aggregations"]["brands"]["buckets"]
        ]

        return Response({"brand_avg_prices": brand_prices}, status=200)


class EngineSizesByBrandModelView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("brand", openapi.IN_QUERY, description="브랜드", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("model", openapi.IN_QUERY, description="모델", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("fuelType", openapi.IN_QUERY, description="연료 타입", type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: openapi.Response("브랜드/모델/연료타입별 엔진 사이즈 리스트")},
    )
    def get(self, request):
        brand = request.GET.get("brand")
        model = request.GET.get("model")
        fuel_type = request.GET.get("fuelType", None)

        if not brand or not model:
            return Response({"error": "brand와 model 파라미터는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        must_filters = [
            {"term": {"brand": brand}},
            {"term": {"model": model}}
        ]
        if fuel_type:
            must_filters.append({"term": {"fuelType": fuel_type}})

        body = {
            "size": 0,
            "query": {
                "bool": {
                    "must": must_filters
                }
            },
            "aggs": {
                "engine_sizes": {
                    "terms": {
                        "field": "engineSize",
                        "size": 50,
                        "order": {"_key": "asc"}
                    }
                }
            }
        }

        try:
            results = es.search(index="cars", body=body)
            engine_sizes = [bucket["key"] for bucket in results["aggregations"]["engine_sizes"]["buckets"]]

            return Response({
                "brand": brand,
                "model": model,
                "fuelType": fuel_type,
                "engine_sizes": engine_sizes
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": "Elasticsearch 조회 중 오류 발생", "detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
