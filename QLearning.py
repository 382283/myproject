import random
import numpy as np

class QLearning:
    def __init__(self, num_questions, alpha = 0.1, gamma = 0.9, epsilon = 0.1):
        self.q_table = np.zeros(num_questions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def select_action(self):
        if random.random() < self.epsilon:
            return random.randint(0, len(self.q_table) - 1)
        else:
            return np.argmax(self.q_table)
        
    def update_q_value(self, action, reward, next_action):
        best_next_action = np.argmax(self.q_table)
        self.q_table[action] = self.q_table[action] + self.alpha * (reward + self.q_table[best_next_action] - self.q_table[action])

    def get_q_table(self):
        return self.q_table

