import requests
group_id = "1946019624600478072"
api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLljYHkuIMiLCJVc2VyTmFtZSI6IuWNgeS4gyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTQ2MDE5NjI0NjA4ODY2NjgwIiwiUGhvbmUiOiIxMzY5NDQwNjk4NyIsIkdyb3VwSUQiOiIxOTQ2MDE5NjI0NjAwNDc4MDcyIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDctMjMgMTY6Mjc6MjgiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.lbUPCtM7eUBlxb0UbalnXopl2JYSqwkZWBht3Z_aD3k9x6UNeHJun-MHig_Q2jtW1ZmQzFC84hFgNA67QouTe6cCX9ot5s53oXNkJ4wTR0EwnqFVnUsaqKAAYT-9Qeyxw_1AO86sG0JK5bqHG9ZL4jqa8ErQh6majLelHdb_OnoDRMB9wQTJQLX34DiV6I8u_sowCrCBeYqaU56LKm6V8pXg0Vhw5tQnQqCdSt3aKAy1UPzntBU03rBK7ypIn2Dkz7a9GpLmbFC3DZDQnNqba5DgLpQXkgW2aIcL5yWugMADz38cBHEOwRxYBQ04a5hi6GksoTPTGSky7hXNkSOWXw"
url = f"https://api.minimaxi.com/v1/text/chatcompletion_pro?GroupId={group_id}"
headers = {"Authorization":f"Bearer {api_key}", "Content-Type":"application/json"}
# tokens_to_generate/bot_setting/reply_constraints可自行修改
request_body = payload = {
  "model":"MiniMax-Text-01",
  "tokens_to_generate":8192,
  "reply_constraints":{"sender_type":"BOT", "sender_name":"MM智能助理"},
  "messages":[],
  "bot_setting":[
    {
      "bot_name":"MM智能助理",
      "content":"MM智能助理是一款由MiniMax自研的，没有调用其他产品的接口的大型语言模型。MiniMax是一家中国科技公司，一直致力于进行大模型相关的研究。",
    }
  ],
}
# 添加循环完成多轮交互
while True:
  # 下面的输入获取是基于python终端环境，请根据您的场景替换成对应的用户输入获取代码
  line = input("发言:")
  # 将当次输入内容作为用户的一轮对话添加到messages
  request_body["messages"].append( {"sender_type":"USER", "sender_name":"小明", "text":line} )
  response = requests.post(url, headers=headers, json=request_body)
  reply = response.json()["reply"]
  print(f"reply: {reply}")
  # 将当次的ai回复内容加入messages
  request_body["messages"].extend(response.json()["choices"][0]["messages"])
