import requests
import folium

# AQICN APIトークン
AQICN_API_TOKEN = "37bbe035573c5ac80111c2f99c5239edd9399d43"

def get_air_quality(city: str, token: str):
    """
    AQICN APIを使用して指定された都市の空気質指数（AQI）を取得する。
    """
    url = f"https://api.waqi.info/feed/{city}/?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok":
            return data["data"]
    return None

def get_aqi_color(aqi: int):
    """
    AQIの値に応じてマーカーの色を決定する。
    """
    if aqi <= 50:
        return "green"
    elif aqi <= 100:
        return "yellow"
    else:
        return "red"

def assess_risk(aqi: int, age: int, pregnant: bool, nationality: str):
    """
    ユーザー属性を考慮してリスク評価を行う。
    """
    risk_level = 0  # 0=低, 1=中, 2=高, 3=非常に高い

    # 基本のAQIリスク
    if aqi <= 50:
        risk_level = 0  # 低リスク
    elif aqi <= 100:
        risk_level = 1  # 中リスク
    else:
        risk_level = 2  # 高リスク

    # 年齢・妊娠の影響
    if age <= 12 or age >= 60 or pregnant:
        risk_level += 1  # 1段階リスク増加

    # 国籍の影響
    if nationality.lower() == "thai":  # タイ人は慣れている
        risk_level -= 1
    elif nationality.lower() == "japanese":  # 日本人などは影響を受けやすい
        risk_level += 1

    # 最小0, 最大3に制限
    risk_level = max(0, min(3, risk_level))

    risk_messages = ["低リスク ✅", "中リスク ⚠️", "高リスク 🔴", "非常に高リスク ❗❗"]
    return risk_messages[risk_level]

def create_map(lat: float, lon: float, aqi: int, risk: str):
    """
    Foliumを使ってAQICNのリアルタイム空気質タイルレイヤーを追加し、地図を作成する。
    """
    # 地図を作成
    m = folium.Map(location=[lat, lon], zoom_start=10)

    # AQICNのタイルレイヤーを追加
    folium.TileLayer(
        tiles=f"https://tiles.waqi.info/tiles/{'{z}/{x}/{y}'}.png?token={AQICN_API_TOKEN}",
        attr="Air Quality Data © 2024 WAQI",
        name="Real-time AQI",
    ).add_to(m)

    # AQIの数値をマーカーで表示
    color = get_aqi_color(aqi)
    folium.CircleMarker(
        location=[lat, lon],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=f"AQI: {aqi}\nリスク: {risk}"
    ).add_to(m)

    # AQI数値とリスクをテキスト表示
    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(
            html=f'<div style="font-size: 12pt; color: {color}; font-weight: bold;">AQI: {aqi}<br>リスク: {risk}</div>'
        )
    ).add_to(m)

    # 地図を保存
    m.save("map/air_quality_map.html")
    print("Map generated: air_quality_map.html")

if __name__ == "__main__":
    city = "Bangkok"  # バンコクのデータを取得
    result = get_air_quality(city, AQICN_API_TOKEN)

    if result:
        lat, lon = result["city"]["geo"]
        aqi = result["aqi"]

        # **ユーザーの属性（テスト用に仮のデータを設定）**
        age = 65  # 年齢（60歳以上は高リスク）
        pregnant = False  # 妊娠の有無
        nationality = "Japanese"  # 国籍（日本人）

        # リスク評価
        risk = assess_risk(aqi, age, pregnant, nationality)

        # 結果を表示
        print(f"Bangkok AQI: {aqi}")
        print(f"リスク評価: {risk}")

        # 地図を生成
        create_map(lat, lon, aqi, risk)
    else:
        print("Failed to retrieve air quality data.")
