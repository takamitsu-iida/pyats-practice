#!/usr/bin/env python

import os

from datetime import datetime

#
# tinydb
#
from tinydb import TinyDB, Query #, where

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.json')


def db_test1():

    # テスト用

    db_path = os.path.join(os.path.dirname(__file__), 'test.db')

    with TinyDB(db_path) as db:
        db.insert_multiple([
        {
            'date': datetime( year=2022, month=1, day=5  ).timestamp()
        },
        {
            'date': datetime( year=2022, month=1, day=15 ).timestamp()
        }
        ])

        q = Query()

        print(db.search(
        (q.date < datetime( year=2022, month=1, day=10 ).timestamp())
        &
        (q.date > datetime( year=2022, month=1, day=4  ).timestamp())
        ))

        timestamps = [doc['date'] for doc in db]
        print(timestamps)

        ids = [doc.doc_id for doc in db]
        print(ids)


def insert_intf_info(device_name:str, intf_info:dict, timestamp:float, max_history=2):
    """
    学習したインタフェース情報をデータベースに保存する。

    格納するドキュメントの形式はこの通り
    {
       'timestamp': xxx,
       'device_name': xxx,
       'intf_info': 学習した情報
    }

    Args:
        device_name (str): 学習した装置の名前
        intf_info (dict): 学習したインタフェース情報
        timestamp (float): 実行した時点のタイムスタンプ
        max_history (int, optional): 何個まで保存するか Defaults to 2.
    """

    # 格納するドキュメント
    doc = {}

    # デバイス名を付与
    doc['device_name'] = device_name

    # タイムスタンプを付与
    doc['timestamp'] = timestamp

    # インタフェース情報を付与
    doc['intf_info'] = intf_info

    # dbに格納
    with TinyDB(DB_PATH) as db:
        db.insert(doc)

    # この装置の古いものを削除
    delete_old(device_name, max_history)


def get_intf_info_by_name(device_name:str):
    """
    名前で検索し、タイムスタンプでソートして返却

    Args:
        device_name (str): 検索対象のキーdevice_nameの値

    Returns:
        list: 見つかったドキュメントのリスト
    """
    q = Query()

    with TinyDB(DB_PATH) as db:
        datas = db.search(q.device_name == device_name)

    if datas:
        return sorted(datas, key=lambda d: d['timestamp'])

    return []


def get_stored_dates(device_name:str):

    # 名前でドキュメントを取り出す
    docs = get_intf_info_by_name(device_name)

    # timestampキーの一覧を取り出す
    timestamps = [doc['timestamp'] for doc in docs]

    # datetimeオブジェクトに変換
    datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]

    # 分かりやすく日付の文字列に変換
    dates = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetimes]

    return dates


def delete_old(device_name:str, max_history:int):
    q = Query()

    with TinyDB(DB_PATH) as db:
        # device_nameが一致するドキュメントからtimestampキーの一覧を取り出す
        timestamps = [doc['timestamp'] for doc in db if doc['device_name'] == device_name]

        # 新しい順（降順）にソート
        timestamps.sort(reverse=True)

        # max_histを超えたものは削除
        if len(timestamps) > max_history:
            should_be_deleted = timestamps[max_history:]
            for ts in should_be_deleted:
                # db.remove(where('timestamp') == ts)
                db.remove( (q.device_name == device_name) & (q.timestamp == ts) )


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='../lab.yml')
    args, _ = parser.parse_known_args()

    #
    # pyATS
    #
    from genie.testbed import load
    from genie.ops.utils import get_ops

    def _get_intf_info(testbed):

        testbed = load(args.testbed)

        uut = testbed.devices['uut']

        # connect
        uut.connect(via='console')

        # learn all interfaces
        Interface = get_ops('interface', uut)
        intf = Interface(device=uut)
        intf.learn()

        # disconnect
        if uut.is_connected():
            uut.disconnect()

        # 学習した結果の辞書型はinfoキーで入手可能
        # pprint(intf.info)
        #
        # {'GigabitEthernet1': {},
        #  'GigabitEthernet2': {},
        #  'GigabitEthernet3': {},

        return uut.name, intf.info

    # 全装置で共通の実行時のタイムスタンプ、
    timestamp = datetime.now().timestamp()

    # インタフェースを学習
    device_name, intf_info = _get_intf_info(args.testbed)

    # dbに格納
    insert_intf_info(device_name, intf_info, timestamp, max_history=2)

    # タイムスタンプの一覧を日付に変換して取得
    dates = get_stored_dates(device_name)

    # 表示
    print(f'stored dates for {device_name} = {dates}')

    # デバイスに関する情報を取り出す
    datas = get_intf_info_by_name(device_name)

    for d in datas:
        print(d['timestamp'])
