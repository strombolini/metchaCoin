## Timofei Babenko | tyb3@cornell.edu
## All rights reserved and whatnot

import hashlib
import json
import csv
from time import time
from collections import Counter

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

def read_user_names():
    try:
        with open('user_names.csv', mode='r') as file:
            reader = csv.reader(file)
            user_names = {row[0]: float(row[1]) for row in reader}
            return user_names
    except FileNotFoundError:
        return {}

def write_user_name(user_name, trust_score=0.5):
    with open('user_names.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_name, trust_score])

def read_descriptions():
    try:
        with open('descriptions.csv', mode='r') as file:
            reader = csv.reader(file)
            descriptions = {row[0]: eval(row[1]) for row in reader}
            return descriptions
    except FileNotFoundError:
        return {}

def write_description(person_name, descriptions):
    with open('descriptions.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([person_name, descriptions])

def update_description_weights(person_name, chosen_index):
    descriptions = read_descriptions()
    weights = Counter(descriptions[person_name]['weights'])
    weights[chosen_index] += 1
    total_votes = sum(weights.values())
    new_weights = {index: count / total_votes for index, count in weights.items()}
    descriptions[person_name]['weights'] = new_weights
    write_description(person_name, descriptions)

def update_user_trust_score(user_name, trust_change):
    user_names = read_user_names()
    user_names[user_name] += trust_change
    if user_names[user_name] > 1.0:
        user_names[user_name] = 1.0
    elif user_names[user_name] < 0.0:
        user_names[user_name] = 0.0
    write_user_name(user_name, user_names[user_name])

# Example usage:
# Read existing user names or initialize an empty dictionary
existing_user_names = read_user_names()

# Print existing user names (for testing purposes)
print("Existing user names:", existing_user_names)

# Prompt user to enter a new name
new_user_name = input("Enter your name: ")

# Check if the new user already exists
if new_user_name not in existing_user_names:
    # If not, add it and initialize with a trust score of 0.5
    existing_user_names[new_user_name] = 0.5
    write_user_name(new_user_name)
else:
    print("Welcome back,", new_user_name)

# Print updated user names (for testing purposes)
print("Updated user names:", existing_user_names)

# Check if the user already has a description
if new_user_name not in read_descriptions():
    # If not, prompt the user to enter their own description
    own_description = input("Enter your own description: ")
    write_description(new_user_name, {'descriptions': [own_description], 'weights': {1: 1.0}})
else:
    print("Your description is already recorded.")

# Read existing descriptions or initialize an empty dictionary
existing_descriptions = read_descriptions()

# Prompt user to enter a friend's name
friend_name = input("Enter your friend's name: ")

# Check if there are existing descriptions for the friend
if friend_name in existing_descriptions:
    print("Existing descriptions found for", friend_name)
    friend_descriptions = existing_descriptions[friend_name]['descriptions']
    weights = existing_descriptions[friend_name]['weights']
    print("Choose the correct description for", friend_name, "from the options below:")
    for i, description in enumerate(friend_descriptions, start=1):
        print(f"{i}. {description} (Weight: {weights[i]})")
    vote = input(f"Enter your vote (1-{len(friend_descriptions)}): ")
    if vote.isdigit() and 1 <= int(vote) <= len(friend_descriptions):
        chosen_index = int(vote)
        print("You voted for:", friend_descriptions[chosen_index - 1])
        update_description_weights(friend_name, chosen_index)
        # Update user trust score based on their vote
        trust_change = 0.1 if chosen_index == 1 else -0.05  # Example change in trust score
        update_user_trust_score(new_user_name, trust_change)
    else:
        print("Invalid vote! Please enter a number between 1")

else:
    print("No existing descriptions found for", friend_name)
    new_description = input("Enter a description for " + friend_name + ": ")
    write_description(friend_name, {'descriptions': [new_description], 'weights': {1: 1.0}})

