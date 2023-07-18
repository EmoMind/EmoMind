import logging

filename = 'server.log'

logging.basicConfig(filename=filename,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def log(user, message):
    logging.info(f'User: {user}, message: {message}')

#log('id_123421', 'Hello!!')
