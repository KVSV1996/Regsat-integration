import socket
import os
import logging

outgoing_context = "test" # контекст для первого плича (исходящий вызов)
port = 12345 # порт для подключения
log_directory = "/var/log/regsat_integration"
 
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file_path = os.path.join(log_directory, "integration.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("Service has started\n")

def parse_details(details):
    detail_dict = {}
    for item in details.split('#'):
        if ':' in item:
            key, value = item.split(':', 1)
            detail_dict[key] = value.strip()
    return detail_dict

def handle_client(connection, address):
    try:
        logging.info(f"Connected by {address}\n")
        data = connection.recv(1024).decode('utf-8')
        if data:
            lines = data.split('\n')
            message_dict = {line.split(':', 1)[0]: line.split(':', 1)[1].strip() for line in lines if line}
            incoming_context = switch(message_dict.get('Message'))
            number_a = message_dict.get('NumberA')
            number_b_details = message_dict.get('NumberB')
            details = parse_details(number_b_details)
            guid = message_dict.get('Guid')
            log_information(data, incoming_context, number_a, details, guid)
            create_asterisk_call_file(number_a, incoming_context, details, guid)
    except Exception as e:
        logging.exception(f"Error handling connection from {address}: {e}")
    finally:
        connection.close()

def log_information(data, incoming_context, number_a, details, guid):
    logging.info(f"Received: \n{data}")
    logging.info(f"Context: {incoming_context}\n")
    logging.info("Variables:")
    logging.info(f"NumberA: {number_a}")
    logging.info(f"Color: {details.get('bron')}")
    logging.info(f"Car Plate: {details.get('carplate')}")
    logging.info(f"Time: {details.get('time')}")
    logging.info(f"Bill: {details.get('bill')}")
    logging.info(f"Car Mark: {details.get('carmark')}")
    logging.info(f"GUID: {guid}\n")

def switch(value):
    if value == "Originate":
        return "test2" # контекст для второго плеча. По аналогии можна добавить сколько угодно
    elif value == "ClientOpros":
        return "test3"
    elif value == "Conference":
        return "test1"

def create_asterisk_call_file(number_a, incoming_context, details, guid):
    fn = f"/var/spool/asterisk/outgoing/{number_a}.call"
    if not os.path.exists(fn):
        content = f"""Channel: Local/{number_a}@test
MaxRetries: 5
RetryTime: 10
WaitTime: 55
Context: {incoming_context}
Extension: {number_a}
Setvar: dialednumber={number_a}
Setvar: color={details.get('bron')}
Setvar: car_plate={details.get('carplate')}
Setvar: time={details.get('time')}
Setvar: bill={details.get('bill')}
Setvar: car_mark={details.get('carmark')}
Setvar: guid={guid}
Priority: 1
"""
        with open(fn, 'w') as file:
            file.write(content)
        logging.info("Файл вызова создан.\n---------------------------------------")
    else:
        logging.info("Файл уже существует.")

def main():
    host = '0.0.0.0'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")
        try:
            while True:
                conn, addr = server_socket.accept()
                handle_client(conn, addr)
        except KeyboardInterrupt:
            logging.info("Server is shutting down.")

if __name__ == '__main__':
    main()

