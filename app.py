from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import random
from urllib.parse import parse_qsl
import os
from dotenv import load_dotenv

app = Flask(__name__)

# --- 啟動隱藏密碼載入器 ---
load_dotenv() 

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 研發所資料庫
drinks_data = {
    "50嵐": {
        "items": ["茉莉綠茶", "阿薩姆紅茶", "四季春青茶", "黃金烏龍", "檸檬綠", "梅の綠", "桔子綠", "8冰綠", "養樂多多綠", "旺來紅", "柚子紅", "鮮柚綠", "四季春+珍波椰", "波霸紅茶", "波霸綠茶", "波霸青茶", "波霸烏龍", "波霸奶茶", "波霸奶綠", "波霸烏龍奶茶", "珍珠紅茶", "珍珠綠茶", "珍珠青茶", "珍珠烏龍", "珍珠奶茶", "珍珠奶綠", "椰果奶茶", "布丁奶茶", "布丁奶綠", "布丁紅茶", "布丁綠茶", "布丁青茶", "布丁烏龍", "奶茶", "奶綠", "紅茶瑪奇朵", "烏龍瑪奇朵", "四季奶青", "黃金烏龍奶茶", "阿華田", "檸檬汁", "金桔檸檬", "檸檬梅汁", "檸檬養樂多", "8冰茶", "柚子茶", "鮮柚汁", "葡萄柚多多", "紅茶拿鐵", "綠茶拿鐵", "黃金烏龍拿鐵", "阿華田拿鐵", "冰淇淋紅茶", "芒果青", "荔枝烏龍"],
        "sugar": ["正常", "9分", "少糖", "半糖", "微糖", "無糖"],
        "ice": ["正常冰", "少冰", "去冰", "熱飲"]
    },
    "可不可": {
        "items": ["熟成紅茶", "麗春紅茶", "春芽綠茶", "胭脂紅茶", "雪花冷露", "熟成冷露", "春芽冷露", "胭脂冷露", "檸檬冷露", "熟檸紅茶", "春檸綠茶", "春梅冰茶", "太妃熟成", "金蜜熟成", "胭脂多多", "輕織穀奈茶", "穀奈冷露", "穀奈歐蕾", "金蜜檸檬", "熟成奶茶", "春芽奶茶", "胭脂奶茶", "白玉奶茶", "熟成歐蕾", "冷露歐蕾", "金蜜歐蕾", "胭脂歐蕾", "白玉歐蕾", "鴛鴦歐蕾", "熟成榛果歐蕾", "墨玉鴛鴦歐蕾", "雪藏紅茶", "雪藏奶茶", "珈琲雪藏胭脂"],
        "sugar": ["全糖", "少糖", "半糖", "微糖", "一分糖", "無糖"],
        "ice": ["正常冰", "少冰", "微冰", "去冰", "常溫", "溫", "熱"]
    },
    "迷客夏": {
        "items": ["桂香原片青", "桂香輕蕎麥", "桂香青檸粉粿", "娜杯桂香拿鐵", "靜岡焙茶鮮奶", "靜岡焙茶烏龍拿鐵", "香芋仙草綠茶拿鐵", "輕纖蕎麥茶", "輕纖蕎麥拿鐵", "焙香決明大麥", "焙香大麥拿鐵", "原鄉冬瓜茶", "冬瓜檸檬", "冬瓜麥茶", "水之森玄米抹茶", "娜杯紅茶", "伯爵紅茶", "大正紅茶", "原片初露青茶", "茉莉原淬綠茶", "琥珀高峰烏龍", "熟釀青梅綠", "熟釀青梅檸", "白甘蔗青茶", "冬瓜青茶", "柳丁綠茶", "柳丁青茶", "青檸香茶", "蜂蜜檸檬晶凍", "香柚綠茶", "養樂多綠", "冰萃柳丁", "娜杯紅茶拿鐵", "伯爵紅茶拿鐵", "大正紅茶拿鐵", "琥珀烏龍拿鐵", "茉香綠茶拿鐵", "原片青茶拿鐵", "珍珠伯爵紅茶拿鐵", "珍珠大正紅茶拿鐵", "珍珠娜杯紅茶拿鐵", "伯爵可可拿鐵", "芋頭鮮奶", "珍珠鮮奶", "手炒黑糖鮮奶", "嫩仙草凍奶", "玄米抹茶鮮奶", "法芙娜可可鮮奶"],
        "sugar": ["正常糖", "少糖", "半糖", "微糖", "無糖"],
        "ice": ["正常", "少冰", "微冰", "去冰", "溫", "熱"]
    },
    "麻古茶坊": {
        "items": ["酪梨草莓甘露", "芝芝草莓果粒", "草莓果粒波波", "金萱芋泥鮮奶", "芋泥波波鮮奶2.0", "濃厚芋泥鮮奶", "巨峰葡萄冰沙", "芝芝葡萄果粒", "葡萄果粒波波", "芒果甘露", "楊枝甘露2.0", "芝芝芒果果粒", "芒果果粒波波", "番茄梅蜜", "番茄梅蜜波波", "香橙果粒茶", "柳橙果粒茶", "葡萄柚果粒茶", "葡萄柚果粒蜜茶", "柳橙芒果果粒茶", "粉粿金萱", "紅芭烏龍", "高山金萱茶", "翡翠綠茶", "錫蘭紅茶", "文山青茶", "古早味紅茶", "紅芭雙Q", "金萱雙Q", "錫蘭奶茶", "鐵觀音奶茶", "波霸奶茶", "仙草凍奶茶", "玫瑰奶茶", "阿華田", "梅子冰茶", "梅子綠茶", "多多綠茶", "粉粿橙香紅萱", "橙香紅萱", "柚香紅萱", "百香雙Q果", "百香綠茶", "百香多多", "翡翠柳橙", "粉粿冰萃檸檬", "冰萃檸檬", "蜂蜜檸檬", "柚香翡翠", "芝芝金萱", "芝芝錫蘭紅茶", "芝芝金萱雙Q", "芝芝翡翠綠茶", "芝芝錫蘭奶茶", "芝芝阿華田", "蕎麥綠寶石", "粉粿紅茶拿鐵", "紅茶拿鐵", "鐵觀音拿鐵", "波霸紅茶拿鐵", "仙草凍紅茶拿鐵", "阿華田拿鐵", "玫瑰紅茶拿鐵"],
        "sugar": ["正常(100%)", "八分(80%)", "半糖(50%)", "二分(20%)", "一分(10%)", "無糖(0%)"],
        "ice": ["正常冰(100%)", "少冰(50%)", "微冰(30%)", "去冰(0%)"]
    }
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    if user_text in drinks_data:
        send_flex_recommendation(event.reply_token, user_text)
    else:
        # 初始選單也用Flex Message
        send_store_menu(event.reply_token)

def send_store_menu(reply_token):
    contents = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical", "contents": [
                {"type": "text", "text": "隨機飲研所", "weight": "bold", "color": "#FFFFFF", "size": "lg", "align": "center"}
            ], "backgroundColor": "#004040"
        },
        "body": {
            "type": "box", "layout": "vertical", "contents": [
                {"type": "text", "text": "請選擇實驗店家進行研究：", "size": "sm", "color": "#666666", "align": "center", "margin": "md"}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical", "spacing": "sm", "contents": [
                {"type": "button", "style": "secondary", "height": "sm", "action": {"type": "message", "label": store, "text": store}}
                for store in drinks_data.keys()
            ]
        }
    }
    line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text="開啟研究選單", contents=contents))

def send_flex_recommendation(reply_token, store_name):
    # 隨機抽取品項、糖量、冰量
    store_info = drinks_data[store_name]
    drink = random.choice(store_info["items"])
    sugar = random.choice(store_info["sugar"])
    ice = random.choice(store_info["ice"])

    # 設計實驗報告卡片 (Flex Message)
    flex_contents = {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {"type": "text", "text": f"🧪 {store_name} 研發報告", "weight": "bold", "color": "#008080", "size": "sm"},
          {"type": "text", "text": drink, "weight": "bold", "size": "xl", "margin": "md", "wrap": True},
          {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "sm", "contents": [
              {"type": "box", "layout": "baseline", "spacing": "sm", "contents": [
                  {"type": "text", "text": "建議糖量", "color": "#aaaaaa", "size": "sm", "flex": 2},
                  {"type": "text", "text": sugar, "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
              ]},
              {"type": "box", "layout": "baseline", "spacing": "sm", "contents": [
                  {"type": "text", "text": "建議溫度", "color": "#aaaaaa", "size": "sm", "flex": 2},
                  {"type": "text", "text": ice, "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
              ]}
          ]},
          {"type": "text", "text": "這項實驗結果符合您的胃口嗎？", "size": "xs", "color": "#cccccc", "margin": "xxl", "wrap": True}
        ]
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": [
          {
            "type": "button", "style": "primary", "color": "#008080",
            "action": {"type": "message", "label": "完美，就喝這杯！", "text": "紀錄實驗結果：這杯好喝！"}
          },
          {
            "type": "button", "style": "link", "color": "#008080",
            "action": {"type": "postback", "label": "重啟實驗 (再抽一次)", "data": f"store={store_name}"}
          }
        ]
      }
    }

    line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text="研發報告出爐", contents=flex_contents))

@handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))
    store_name = data.get('store')
    if store_name:
        send_flex_recommendation(event.reply_token, store_name)

if __name__ == "__main__":
    app.run(port=5000)