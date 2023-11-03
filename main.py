# -*- coding: utf-8 -*-

import sys
import time
import struct
import socket
from sqlalchemy.exc import SQLAlchemyError

from models import Record
from database import session_scope


def parse(fmt, binary, offset=0):
    parsed = struct.unpack_from(fmt, binary, offset)
    return parsed[0] if len(parsed) == 1 else parsed


# TODO: написать функцию записи в БД
def sql_insert(point):
    try:
        with session_scope() as session:
            a = session.query()
            pass
    except SQLAlchemyError as e:
        print(f"Error saving Info data: {e}")
        raise


def parse_packet(packet):
    """
    Парсим без первых 4 байтов (размер пакета)
    """
    # TODO: написать вычисление размера пакета и проверку целостности последнего

    # create vars
    lat, lon, spd, an_1, an_2, an_3, an_4, pwr_ext = 0, 0, 0, 0, 0, 0, 0, 0

    msg = {
        'id': 0,
        'time': 0,
        'flags': 0,
        'params': {},
        'blocks': []
    }

    # parse packet info
    b = '\x00'.encode()  # равносильно b'\0'
    controller_id_size = packet.find(b)
    (msg['id'], msg['time'], msg['flags']) = parse('> %ds x i i' % controller_id_size, packet)
    # > big-endian x pad byte i-int
    # %ds % controller_id_size - if controller_id_size = 4, then %ds = 4s

    # get data block
    data_blocks = packet[controller_id_size + 1 + 4 + 4:]

    while len(data_blocks):
        # name offset in data block
        offset = 2 + 4 + 1 + 1
        name_size = data_blocks.find(b, offset) - offset
        (block_type, block_length, visible, data_type, name) = parse('> h i b b %ds' % name_size, data_blocks)

        # construct block info
        block = {
            'type': block_type,
            'length': block_length,
            'visibility': visible,
            'data_type': data_type,
            'name': name,
            'data_block': data_blocks[offset + name_size + 1:block_length * 1 + 6]
        }

        # get block data

        v = {}
        if block['data_type'] == 1:
            # text
            # TODO
            pass
        elif block['data_type'] == 2:
            # binary
            if block['name'] == b'posinfo':
                v = {'lat': 0, 'lon': 0, 'h': 0, 's': 0, 'c': 0, 'sc': 0}
                (v['lon'], v['lat'], v['h']) = parse('< d d d', block['data_block'])
                (v['s'], v['c'], v['sc']) = parse('> h h b', block['data_block'], 24)
                lat = v['lat']
                lon = v['lon']
                spd = v['s']
        elif block['data_type'] == 3:
            # integer
            v = parse('> i', block['data_block'])
        elif block['data_type'] == 4:
            # float
            v = parse('d', block['data_block'])
        elif block['data_type'] == 5:
            # long
            v = parse('> q', block['data_block'])
        # add param to message
        msg['params'][name] = v

        # data blocks parse information
        msg['blocks'].append(block)

        # delete parsed info
        data_blocks = data_blocks[block_length + 6:]

    point_time = time.strftime("%d-%m-%Y %H:%M:%S",
                               time.localtime(msg['time']))  # время точки  # обычно там UTC а не local.
    # datetime.utcfromtimestamp().replace(tzinfo=timezone.utc)
    parameters = msg['params']
    try:
        an_1 = parameters.get(b'rs485_fls02', 0)
    except Exception:
        pass
    try:
        an_2 = parameters.get(b'rs485_fls12', 0)
    except Exception:
        pass
    try:
        an_3 = parameters.get(b'rs485_fls22', 0)
    except Exception:
        pass
    try:
        an_4 = parameters.get(b'rs485_fls32', 0)
    except Exception:
        pass
    try:
        pwr_ext = parameters.get(b'pwr_ext', 0)
    except Exception:
        pass

    rid = 8081
    rec_type = 1
    power = 0
    d1, d2, d3, d4, d5, d6 = 1, 1, 1, 1, 1, 1
    id_obj = msg['id'].decode('ascii')
    print(type(msg['id']))
    point = (id_obj, point_time, rid, rec_type, lat, lon, spd, power,
             d1, d2, d3, d4, d5, d6, an_1, an_2, an_3, an_4, pwr_ext)

    return msg


def init_socket(host, port):
    # Создаем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Привязываем сокет к адресу
    server_address = (host, port)
    print(f'Starting up on {server_address[0]} port {server_address[1]}')
    server_socket.bind(server_address)

    # Начинаем слушать запросы
    server_socket.listen(5)
    print('Listening for incoming connections...')

    return server_socket


def validate_packet_size(packet):
    # Первые 4 байта хранят размер пакета
    packet_size = struct.unpack('!I', packet[:4])[0]

    if len(packet) != packet_size:
        raise ValueError(f'Invalid packet size. Expected: {packet_size}, got: {len(packet)}')

    return packet_size


if __name__ == '__main__':

    # port = int(sys.argv[1])
    port = 8081

    # Задаем адрес сервера
    SERVER_ADDRESS = ('localhost', port)

    # Настраиваем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(1)

    print('server is running')

    # Слушаем запросы
    while True:
        connection, address = server_socket.accept()
        print(f"new connection from {address}")

        data = connection.recv(2048)
        print('packet send')

        data = bytearray(data)
        header = data[:4]  # хранит в себе размер пакета
        body = data[4:]  # остальные данные
        print('body checked')

        parse_packet(body)

        print('parser work is done')

        connection.close()
        print('connection close')