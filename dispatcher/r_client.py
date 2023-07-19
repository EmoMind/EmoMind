import redis
import json

class RedisClient:
    N_MESSAGES = 3
    def __init__(self, host, port):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        
    def user_exists(self, user_id):
        return self.r.exists(user_id)
    
    def add_user(self, user_id, character):
        '''Creates new user'''
        self.r.hset(user_id, mapping={
            'emotion': 'нейтральное',
            'messages': '[]',
            'character': character
        })
        
    def get_user(self, user_id):
        '''Returns user data in a dict'''
        user_data = self.r.hgetall(user_id)
        if self.r.hexists(user_id, "messages"):
            user_data["messages"] = json.loads(user_data["messages"])
        return user_data
    
    def delete_user(self, user_id):
        '''Deletes user'''
        self.r.delete(user_id)
    
    def add_message(self, user_id, new_message):
        '''Adds new message to a user. Max amount of messages is set by N_MESSAGES'''
        msgs = self.get_messages(user_id)
        msgs.append(new_message)
        if len(msgs) > self.N_MESSAGES:
            del msgs[0]
        msgs_serialized = json.dumps(msgs)
        self.r.hset(user_id, key="messages", value=msgs_serialized)
    
    def get_messages(self, user_id):
        msgs_serialized = self.r.hget(user_id, "messages")
        msgs = json.loads(msgs_serialized)
        return msgs
        
    def get_character(self, user_id):
        '''Gets character field of a user'''
        return self.r.hget(user_id, key="character")
    
    def get_emotion(self, user_id):
        '''Gets emotion field of a user'''
        return self.r.hget(user_id, key="emotion")
    
    def update_emotion(self, user_id, new_emotion):
        '''Updates emotion field of a user'''
        self.r.hset(user_id, key="emotion", value=new_emotion)
        
    def update_character(self, user_id, new_character):
        '''Updates character field of a user'''
        self.r.hset(user_id, key="character", value=new_character)
