# coding: utf-8
#%save PokerMath.py 92

from deuces import Card
from deuces import Evaluator
from itertools import combinations
import random

class PokerMath():
    #Populate dict with card values to save processing time later
    #Also add all integers to a numpy array for quick processing
    def __init__(self):
        
        card = {}
        deck = []
        ranked_hands = []

        n = 0
        for i in ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']:
            for j in ['s', 'h', 'c', 'd']:
                card[i+j] = Card.new(i+j)
                deck.append(Card.new(i+j))
                n += 1

        for hand in combinations([card['As'], card['Ad'], card['Ac'], card['Ah']], 2):
            ranked_hands.append(set(hand))

        for hand in combinations([card['Ks'], card['Kd'], card['Kc'], card['Kh']], 2):
            ranked_hands.append(set(hand))

        for hand in combinations([card['Qs'], card['Qd'], card['Qc'], card['Qh']], 2):
            ranked_hands.append(set(hand))

        ranked_hands.append(set((card['As'], card['Ks'])))
        ranked_hands.append(set((card['Ad'], card['Kd'])))
        ranked_hands.append(set((card['Ac'], card['Kc'])))
        ranked_hands.append(set((card['Ah'], card['Kh'])))

        for hand in combinations([card['Js'], card['Jd'], card['Jc'], card['Jh']], 2):
            ranked_hands.append(set(hand))

        ranked_hands.append(set((card['As'], card['Qs'])))
        ranked_hands.append(set((card['Ad'], card['Qd'])))
        ranked_hands.append(set((card['Ac'], card['Qc'])))
        ranked_hands.append(set((card['Ah'], card['Qh'])))

        ranked_hands.append(set((card['Ks'], card['Qs'])))
        ranked_hands.append(set((card['Kd'], card['Qd'])))
        ranked_hands.append(set((card['Kc'], card['Qc'])))
        ranked_hands.append(set((card['Kh'], card['Qh'])))

        ranked_hands.append(set((card['As'], card['Js'])))
        ranked_hands.append(set((card['Ad'], card['Jd'])))
        ranked_hands.append(set((card['Ac'], card['Jc'])))
        ranked_hands.append(set((card['Ah'], card['Jh'])))


        ranked_hands.append(set((card['Ks'], card['Js'])))
        ranked_hands.append(set((card['Kd'], card['Jd'])))
        ranked_hands.append(set((card['Kc'], card['Jc'])))
        ranked_hands.append(set((card['Kh'], card['Jh'])))

        for hand in combinations([card['Ts'], card['Td'], card['Tc'], card['Th']], 2):
            ranked_hands.append(set(hand))

        self.ranked_hands = ranked_hands
        self.card_dict = card
        self.deck = deck
        self.evaluator = Evaluator()
        
    def is_best_hand(self, hole, other_hands, board): 
        #print board
        my_score = self.evaluator.evaluate(hole, board)
        for hand in other_hands:
            if my_score > self.evaluator.evaluate(hand, board): #greater number = worse hand
                return False
        return True
    def hand_strength(self, hole, board, num_players, trials = 1000, possible_hands = [], current=False):
        #convert cards to proper format
        temp_hole = []
        for card in hole:
            temp_hole.append(self.card_dict[card])
        hole = temp_hole
        
        temp_board = []
        for card in board:
            temp_board.append(self.card_dict[card])
        board = temp_board
        
        temp_possible_hands = []
        for hand in possible_hands:
            temp_possible_hands.append([self.card_dict[hand[0]], self.card_dict[hand[1]]])
        possible_hands = temp_possible_hands
            
                
        wins = 0.
        for i in range(trials):
            other_hands = []
            temp_deck = self.deck[:] #make a copy of the deck!

            #remove hole and board cards from deck
            for card in board + hole:
                temp_deck.remove(card)


            #shuffle the deck
            random.shuffle(temp_deck)

    
            #deal out cards to the other players
            if len(possible_hands) == 0:
                for i in range(num_players):   
                    other_hands.append([temp_deck.pop(),temp_deck.pop()])

            else:        
                hands = possible_hands[:]
                for i in range(num_players):   
                    rand_hand = random.choice(hands)
                    ''' 
                    Card.print_pretty_cards(hole)
                    Card.print_pretty_cards(rand_hand)
                    Card.print_pretty_cards(temp_board)
                    print '----------'
                    '''

                    
                    other_hands.append(rand_hand)
                    hands.remove(rand_hand)
                    temp_deck.remove(rand_hand[0])
                    temp_deck.remove(rand_hand[1])
                    
            #deal board cards
            
            if not current:
                temp_board = board[:]
                for i in range(0 , 5 - len(board)):
                    temp_board.append(temp_deck.pop())


            #check if we won
            if self.is_best_hand(hole, other_hands, temp_board):
                wins += 1

        return wins / trials


    
