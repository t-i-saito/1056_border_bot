import streamlit as st
import json
import requests
import pandas as pd
from datetime import datetime as dt

st.set_page_config(layout="wide")
userlist = ['よこまき', 'METEOR']

user_name = st.sidebar.selectbox("ユーザー選択", userlist)
#セレクトボックスのリストを作成
pagelist = ["シャニPカップ"]
#サイドバーのセレクトボックスを配置
selector=st.sidebar.radio( "コンテンツ選択",pagelist)
if selector=="シャニPカップ":
    # 各アイドル情報
    with open('shiny_colors_idol_dir_streamlit.json', 'r') as f_json:
        idol_dir = json.load(f_json)
    idol_list = []
    for key in idol_dir.keys():
        idol_list.append(key)

    selector_idol = st.sidebar.multiselect("アイドル選択", idol_list)
    # if st.sidebar.button('アイドル選択完了'):

    if len(selector_idol) != 0:
        border_summary = {}
        for border_idol in selector_idol:
            st.title(border_idol)
            col1, col2 = st.columns(2)
            # コンテキストマネージャとして使う
            with col1:
                my_rank = st.number_input(label='自分の順位', step=1,key=border_idol)
            with col2:
                border = st.number_input(label='目標ボーダー', step=1, key=border_idol)

            # my_rank = st.number_input(label='自分の順位', key=border_idol)
            # border = st.number_input(label='目標ボーダー', key=border_idol)
            border_summary[border_idol] = [str(my_rank), str(border)]
        if st.button('順位設定OK'):
            for border_idol in selector_idol:

                # border_data = "https://api.matsurihi.me/mltd/v1/events/241/rankings/logs/idolPoint/{}/{}".format(
                border_data="https://api.matsurihi.me/sc/v1/events/fanRanking/40009/rankings/logs/{}/{}".format(
                        int(idol_dir[border_idol][0]), int(border_summary[border_idol][1]))
                r = requests.get(border_data)
                border_json_data = r.json()
                # API実行(ユーザー)
                # user_data = "https://api.matsurihi.me/mltd/v1/events/241/rankings/logs/idolPoint/{}/{}".format(
                user_data = "https://api.matsurihi.me/sc/v1/events/fanRanking/40009/rankings/logs/{}/{}".format(
                    int(idol_dir[border_idol][0]), int(border_summary[border_idol][0]))
                r2 = requests.get(user_data)
                user_json_data = r2.json()

                # json整形
                lasted_border_data = border_json_data[0]['data'][-1]
                lasted_user_data = user_json_data[0]['data'][-1]

                lasted_border_data_f = format(lasted_border_data['score'], ',')
                lasted_user_data_f = format(lasted_user_data['score'], ',')

                # 計算諸々
                diff = format(abs(lasted_user_data['score'] - lasted_border_data['score']), ',')

                # ユーザの時速と日速
                if len(user_json_data[0]['data']) < 3:
                    user_1h_speed = format(abs(lasted_user_data['score']), ',')
                else:
                    before_1h_user_data = user_json_data[0]['data'][-3]
                    user_1h_speed = format(abs(before_1h_user_data['score'] - lasted_user_data['score']), ',')

                if len(user_json_data[0]['data']) < 49:
                    user_24h_speed = format(abs(lasted_user_data['score']), ',')
                else:
                    before_24h_user_data = user_json_data[0]['data'][-49]
                    user_24h_speed = format(abs(before_24h_user_data['score'] - lasted_user_data['score']), ',')

                # ボーダーの時速と日速
                if len(border_json_data[0]['data']) < 3:
                    before_1h_border_data = 0
                    border_1h_speed = format(abs(lasted_border_data['score']), ',')
                else:
                    before_1h_border_data = border_json_data[0]['data'][-3]
                    border_1h_speed = format(abs(before_1h_border_data['score'] - lasted_border_data['score']), ',')

                if len(border_json_data[0]['data']) < 49:
                    border_24h_speed = format(abs(lasted_border_data['score']), ',')
                else:
                    before_24h_border_data = border_json_data[0]['data'][-49]
                    border_24h_speed = format(abs(before_24h_border_data['score'] - lasted_border_data['score']), ',')
                # 文言諸々
                df = pd.DataFrame(index=[border_summary[border_idol][1] + '位', user_name + 'さん'],
                                  columns=['現在のポイント', '時速', '日速', border_summary[border_idol][1] + '位との差'])
                df.at[border_summary[border_idol][1] + '位', '現在のポイント'] = str(lasted_border_data_f)
                df.at[border_summary[border_idol][1] + '位', '時速'] = str(border_1h_speed)
                df.at[border_summary[border_idol][1] + '位', '日速'] = str(border_24h_speed)
                df.at[border_summary[border_idol][1] + '位', border_summary[border_idol][1] + '位との差'] = str(0)
                df.at[user_name + 'さん', '現在のポイント'] = str(lasted_user_data_f)
                df.at[user_name + 'さん', '時速'] = str(user_1h_speed)
                df.at[user_name + 'さん', '日速'] = str(user_24h_speed)
                df.at[user_name + 'さん', border_summary[border_idol][1] + '位との差'] = str(diff)

                # 時刻のdatetime型の出漁
                lasted_border_data_time = border_json_data[0]['data'][-1]['summaryTime']
                data = lasted_border_data_time.split('T')[0]
                time = lasted_border_data_time.split('T')[1].split('+')[0]
                tdatetime = dt.strptime(data + ' ' + time, '%Y-%m-%d %H:%M:%S')

                st.title(f"{user_name}さん({border_summary[border_idol][0]}位)の{border_idol}ボーダー")
                st.write(f"{data} {time}時点")
                st.dataframe(df)


                # 前回の履歴との比較
                if user_name in list(idol_dir[border_idol][1].keys()):

                    before_rank = idol_dir[border_idol][1][user_name]['rank']
                    before_score = idol_dir[border_idol][1][user_name]['score']
                    before_time = idol_dir[border_idol][1][user_name]['time']
                    data = before_time.split('T')[0]
                    time = before_time.split('T')[1].split('+')[0]
                    before_tdatetime = dt.strptime(data + ' ' + time, '%Y-%m-%d %H:%M:%S')

                    diff_score = lasted_user_data['score'] - int(float(before_score.replace(',', '')))

                    diff_time = tdatetime - before_tdatetime
                    diff_time_days = diff_time.days
                    diff_time_seconds = diff_time.seconds
                    diff_time_hour = diff_time_days * 24 + diff_time_seconds / 3600

                    st.title(f"{user_name}さんの{border_idol}ボーダー前回の検索時との比較")
                    st.write(f"前回検索時刻：{data} {time}")
                    st.write(f"経過時間：{str(diff_time_hour)}時間")


                    before_border_score = lasted_border_data['score']
                    for _data in border_json_data[0]['data']:
                        if _data['summaryTime'] == before_time:
                            before_border_score = _data['score']
                            break

                    diff_border_score = lasted_border_data['score'] - before_border_score
                    try:
                        user_average_hour = diff_score / diff_time_hour
                        border_average_hour = diff_border_score / diff_time_hour
                    except ZeroDivisionError:
                        user_average_hour = 0
                        border_average_hour = 0

                    coff = [
                        '前回検索からのポイント変動',
                        '前回検索から今までの平均時速',
                        '前回検索から今までの' + border_summary[border_idol][1] + '位ボーダーの平均時速',
                        border_summary[border_idol][1] + '位ボーダーとの時速差',

                    ]
                    df2 = pd.DataFrame(index=coff,
                                      columns=["各値"])

                    st.write(f"前回検索からの順位変動：{before_rank}→{border_summary[border_idol][0]}")

                    df2.at['前回検索からのポイント変動', '各値'] = format(diff_score, ',')
                    df2.at['前回検索から今までの平均時速', '各値'] = format(int(user_average_hour), ',')
                    df2.at['前回検索から今までの' + border_summary[border_idol][1] + '位ボーダーの平均時速', '各値'] = format(int(border_average_hour), ',')
                    df2.at[border_summary[border_idol][1] + '位ボーダーとの時速差', '各値'] = format(int(user_average_hour) - int(border_average_hour), ',')
                    st.dataframe(df2)

                else:
                    st.title(f"{user_name}さんの{border_idol}ボーダーの検索履歴はありません")
                    st.write(f"検索時刻：{data} {time}")

                idol_dir[border_idol][1][user_name] = {
                    'rank': border_summary[border_idol][0],
                    'score': lasted_user_data_f,
                    'time': border_json_data[0]['data'][-1]['summaryTime'],
                }

                with open('shiny_colors_idol_dir_streamlit.json', 'w') as f:
                    json.dump(idol_dir, f)


