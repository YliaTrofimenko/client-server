import pickle

# сериализует сообщение и отправляет его вперемешку с данным клиентом
def send_serialized(client, obj_to_send, the_type='text'):
    client.send(pickle.dumps(obj_to_send))


# возвращается с десериализованным объектом
def get_serialized_message(client, data=None):
    if data is None:
        obj = pickle.loads(client.recv(1024))
        return obj
    return pickle.loads(data)
