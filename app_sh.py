import requests
from flask import Flask, render_template

app = Flask(__name__)

# 외부API에서 여행지 가져오기
def get_tourist_place_details(content_id):
    # API service key
    service_key = "e1MMpT7St3EHSxcRRYM4EM%2BKpD%2BYa07ocfY%2BrKoJzauIJcoridA7C0dw2pacHyCGWAZ6NtZeFMNsGpY5fHYusw%3D%3D"
    URL = f"http://apis.data.go.kr/B551011/KorService1/detailCommon1?ServiceKey={service_key}&contentId={content_id}&MobileOS=ETC&MobileApp=SeoulViewer&defaultYN=Y&firstImageYN=Y&areacodeYN=Y&catcodeYN=Y&addrinfoYN=Y&mapinfoYN=Y&overviewYN=Y&_type=json"
    
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# id별로 다른 컨텐츠 가져오기
@app.route('/place/<int:content_id>')
def show_place_details(content_id=132215): 
    json_data = get_tourist_place_details(content_id)
    if json_data:
        item = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])[0]
        return render_template('detail.html', place=item)
    else:
        return "Details not found", 404
    

if __name__ == '__main__':
    app.run(debug=True)
