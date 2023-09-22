import geopandas as gpd
from shapely.geometry import Point
import streamlit as st
import requests
from pyproj import Transformer

address = st.text_input("서울특별시 서초구 바우뫼로 175")  # 예시 주소
api_key = "d46f200eab5046fb4000daf50176699b"
def get_lat_lon_from_address(address, api_key):
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={address}"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)
    if not data['documents']:
        return None, None
    
    lat = data['documents'][0]['y']
    lon = data['documents'][0]['x']
    
    return float(lat), float(lon)

def transform_to_epsg5181(lat, lon):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y

def find_area_containing_point(shp_path, x, y):
    # Shapefile을 읽습니다.
    gdf = gpd.read_file(shp_path)
    
    # 주어진 x, y 좌표로 Point 객체를 생성합니다.
    point = Point(x, y)
    
    # 해당 Point를 포함하는 행을 찾습니다.
    contains_point = gdf[gdf.geometry.contains(point)]
    
    # 결과가 비어 있지 않은 경우 상권정보를 반환합니다.
    if not contains_point.empty:
        # 예제에서는 '상권정보'라는 컬럼 이름을 사용합니다. 실제로 사용하려는 파일의 컬럼 이름에 맞게 변경해 주세요.
        business_info = contains_point['TRDAR_SE_1'].iloc[0]
        business_code = contains_point['TRDAR_CD_N'].iloc[0]
        return business_info, business_code
    else:
        return None, None

# 주소정보를 x,y 좌표 값으로 변경
def find_biz_ara_info (address) :
    api_key = "d46f200eab5046fb4000daf50176699b"  # 여기에 발급받은 카카오 맵 API 키를 넣어주세요.
    print(api_key)
    lat, lon = get_lat_lon_from_address(address, api_key)
    if lat and lon:
        x, y = transform_to_epsg5181(lat, lon)
        # print(f"Coordinates in EPSG:5181 for {address} -> X: {x}, Y: {y}")

        # 데이터 파일 경로 (open API 대체)
        shp_path = 'C:/Users/PC/Desktop/특가상품추천/특가상품추천/seoul/TBGIS_TRDAR_RELM.shp'
        # x, y = float(input("Enter x: ")), float(input("Enter y: "))
        # x, y = float(197093), float(453418)
        result_info, result_code = find_area_containing_point(shp_path, x, y)

    else:
        print(f"변환가능한 주소정보를 찾을 수 없습니다. {address}")
        result_info = "알수없음 (잘못된 주소)"
        result_code = "알수없음 (잘못된 주소)"
    
    return result_info, result_code

