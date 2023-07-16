import redis
import json

class RedisClient:
    N_MESSAGES = 3
    def __init__(self, host, port):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
    
    def add_user(self, user_id, character):
        '''Creates new user'''
        self.r.hset(user_id, mapping={
            'emotion': 'нейтральное',
            'messages': '[]',
            'character': character
        })
        
    def get_user(self, user_id):
        '''Returns user data in a dict'''
        return self.r.hgetall(user_id)
    
    def delete_user(self, user_id):
        '''Deletes user'''
        self.r.delete(user_id)
    
    def add_message(self, user_id, new_message):
        '''Adds new message to a user. Max amount of messages is set by N_MESSAGES'''
        msgs_serialized = self.r.hget(user_id, "messages")
        msgs = json.loads(msgs_serialized)
        msgs.append(new_message)
        if len(msgs) > self.N_MESSAGES:
            del msgs[0]
        msgs_serialized = json.dumps(msgs)
        self.r.hset(user_id, key="messages", value=msgs_serialized)
    
    def update_emotion(self, user_id, new_emotion):
        '''Updates emotion field of a user'''
        self.r.hset(user_id, key="emotion", value=new_emotion)
        
    def update_character(self, user_id, new_character):
        '''Updates character field of a user'''
        self.r.hset(user_id, key="character", value=new_character)
        
    
        
        