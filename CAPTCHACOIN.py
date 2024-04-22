## Timofei Babenko | tyb3@cornell.edu
## All rights reserved and whatnot

import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_descriptions = []
        self.current_guesses = []
        self.create_block(previous_hash='1', proof=100)

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'descriptions': self.current_descriptions,
            'guesses': self.current_guesses,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_descriptions = []
        self.current_guesses = []
        self.chain.append(block)
        return block

    def new_description(self, user, person_name, descriptions):
        self.current_descriptions.append({
            'user': user,
            'person_name': person_name,
            'descriptions': descriptions,
        })
        return self.last_block['index'] + 1

    def new_guess(self, user, person_name, guessed_description):
        self.current_guesses.append({
            'user': user,
            'person_name': person_name,
            'guessed_description': guessed_description,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Difficulty criterion

# Example usage:
# Create a blockchain instance
blockchain = Blockchain()

# Example user interactions with three initial descriptions
blockchain.new_description('User1', 'John', ['Friendly and outgoing', 'Introverted but kind', 'Enthusiastic and adventurous'])

# Example user guesses
blockchain.new_guess('User2', 'John', 'Friendly and outgoing')
blockchain.new_guess('User3', 'John', 'Introverted but kind')
blockchain.new_guess('User4', 'John', 'Enthusiastic and adventurous')

# Mine a new block
last_block = blockchain.last_block
last_proof = last_block['proof']
proof = blockchain.proof_of_work(last_proof)
previous_hash = blockchain.hash(last_block)
blockchain.create_block(proof, previous_hash)
