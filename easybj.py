#!/usr/bin/python3
#
# easybj.py
#
# Calculate optimal strategy for the game of Easy Blackjack
#

from table import Table
from collections import defaultdict

# code names for all the hard hands
HARD_CODE = [ '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 
    '15', '16', '17', '18', '19', '20']

# code names for all the soft hands
SOFT_CODE = [ 'AA', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9' ]

# code names for all the hands that can be split
SPLIT_CODE = [ '22', '33', '44', '55', '66', '77', '88', '99', 'TT', 'AA' ]

# code names for all the hands that cannot be split
NON_SPLIT_CODE = HARD_CODE + SOFT_CODE

# code names for standing
STAND_CODE = HARD_CODE + ['21'] + SOFT_CODE
   
# code names for all the y-labels in the strategy table
PLAYER_CODE = HARD_CODE + SPLIT_CODE + SOFT_CODE[1:]

# code names for all the x-labels in all the tables
DEALER_CODE = HARD_CODE + SOFT_CODE[:6]

# code names for all the initial player starting hands
# (hard 4 is always 22, and hard 20 is always TT)
INITIAL_CODE = HARD_CODE[1:-1] + SPLIT_CODE + SOFT_CODE[1:] + ['BJ']

# point dictionary for each card
POINT_MAP = { "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "T":10, "J":10, "Q":10, "K":10, "A":11 }

SOFT_CODE_num={'AA':12, 'A2':13, 'A3':14, 'A4':15, 'A5':16, 'A6':17, 'A7':18, 'A8':19, 'A9':20}
# 
# Returns whether a and b are close enough in floating point value
# Note: use this to debug your code
#
def isclose(a, b=1., rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)  

# use the numeral value 0 to represent a busted hand (makes it easier to
# compare using integer comparison)
BUST = 0

# list of distinct card values
DISTINCT = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T' ]

# number of cards with 10 points
NUM_FACES = 4

# number of ranks in a French deck
NUM_RANKS = 13

# return the probability of receiving this card
def probability(card):
    return (1 if card != 'T' else NUM_FACES) / NUM_RANKS

#
# Represents a Blackjack hand (owned by either player or dealer)
#
# Note: you should make BIG changes to this class
#
class Hand:
    def __init__(self, x, y, dealer=False):
        self.cards = [x, y]
        self.is_dealer = dealer
  
    # probability of receiving this hand
    def probability(self):
        p = 1.
        for c in self.cards:
            p *= probability(c)
        return p
  
    # the code which represents this hand
    def code(self, nosplit=False):
        
        # TODO: implement me

        # !!!!!!!!!!!!!!
        # do not forget to implement the logic for max of 4 splitted hands!
        # !!!!!!!!!!!!!!

        # case when 2 cards and where both cards are the same for player
        if not self.is_dealer and (len(self.cards)==2) and (self.cards[0]==self.cards[1]):
            code_str=self.cards[0]
            code_str+=self.cards[1]
            return code_str

        # every other case
        points, is_soft = pointCalculator(self.cards)
        if self.is_dealer:
            if (points > 21):
                return "0"
            elif (points == 21):
                if (len(self.cards) == 2):
                    return "BJ"
                else:
                    return "21"
            else:
                if is_soft and (points < 18):
                    if points==12:
                        return "AA"
                    else:
                        code_str="A"
                        code_str+=str(points-11)
                        return code_str
                else:
                    return str(points)
        else:
            if (points > 21):
                return "0"
            elif (points == 21):
                if (len(self.cards) == 2):
                    return "BJ"
                else:
                    return "21"
            else:
                if is_soft:
                    if points==12:
                        return "AA"
                    else:
                        code_str="A"
                        code_str+=str(points-11)
                        return code_str
                else:
                    return str(points)

# Calculate point value of a hand and its softness
def pointCalculator(cards):
    points=0
    hasAce=False
    for i in cards:
        if (i=='A'):
            if hasAce:
                points+=-10
            hasAce=True
        points+=POINT_MAP[i]
    if (points > 21) and hasAce:
        points+=-10
        return points, False
    if hasAce and (points <= 21):
        return points, True
    else:
        return points, False

#
# Singleton class to store all the results. 
#
# Note: you should make HUGE changes to this class
#
class Calculator:
    def __init__(self): 
        self.initprob = Table(float, DEALER_CODE + ['BJ'], INITIAL_CODE, unit='%')
        self.dealprob = defaultdict(dict)
        self.stand_ev = Table(float, DEALER_CODE, STAND_CODE)
        self.hit_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.double_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.split_ev = Table(float, DEALER_CODE, SPLIT_CODE)
        self.optimal_ev = Table(float, DEALER_CODE, PLAYER_CODE)
        self.strategy = Table(str, DEALER_CODE, PLAYER_CODE)
        self.advantage = 0.
        self.resplit0=Table(float, DEALER_CODE, STAND_CODE)
        self.resplit1=Table(float, DEALER_CODE, SPLIT_CODE[:-1])
        self.resplit2=Table(float, DEALER_CODE, SPLIT_CODE[:-1])
    
    # make each cell of the initial probability table      
    def make_initial_cell(self, player, dealer):
        table = self.initprob
        dc = dealer.code()  
        pc = player.code()
        prob = dealer.probability() * player.probability()
        if table[pc,dc] is None:
            table[pc,dc] = prob
        else:
            table[pc,dc] += prob
    
    # refactored make of a prob table
    def make_table(self, cell_making_method):
        for i in DISTINCT:
            for j in DISTINCT:
                for x in DISTINCT:
                    for y in DISTINCT:
                        dealer = Hand(i, j, dealer=True)
                        player = Hand(x, y)
                        cell_making_method(player, dealer)

    # make the initial probability table            
    def make_initial_table(self):
        #
        # TODO: refactor so that other table building functions can use it
        #
        self.make_table(self.make_initial_cell)

    # make the dealer probability dictionary            
    def make_dealer_dict(self):
        dealer_list=['17','18','19','20','21']
        for i in ['17','18','19','20']:
            self.dealprob[i] = {i:1.0}
        self.dealprob['16'] = {'17': 1/13, '18': 1/13, '19': 1/13, '20': 1/13, '21': 1/13, '0': 8/13}
        for i in HARD_CODE[:12]+SOFT_CODE[:6]:
            self.dealprob[i] = {'17': 0.0, '18': 0.0, '19': 0.0, '20': 0.0, '21': 0.0, '0': 0.0}
        #HARD_CODE = [ '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', !!!!!!!!!!!!!!!!!!!'16', '17', '18', '19', '20']
        for dc in reversed(HARD_CODE[:12]):
            int_dc=int(dc)
            if (int_dc>=12):
                for d in dealer_list:
                    self.dealprob[dc][d]+=(1/13)
                busts=10-(21-int_dc)+3
                self.dealprob[dc]['0']+=(busts/13)
                for next_stage in range(int_dc+1,17):
                    for x in self.dealprob[str(next_stage)].items():
                        key, element = x
                        self.dealprob[dc][key]+=element*(1/13)
            elif (int_dc==11):
                for d in dealer_list[:4]:
                    self.dealprob[dc][d]+=(1/13)
                self.dealprob[dc]['21']+=(4/13)
                for next_stage in range(int_dc+1,17):
                    for x in self.dealprob[str(next_stage)].items():
                        key, element = x
                        self.dealprob[dc][key]+=element*(1/13)
            elif (int_dc>6) and (int_dc<11):#7~10
                max_int_dc=int_dc+11
                for d in range(17,max_int_dc+1):
                    if(d-int_dc==10):
                        self.dealprob[dc][str(d)]+=(4/13)
                    else:               
                        self.dealprob[dc][str(d)]+=(1/13)
                for next_stage in range(int_dc+2,17):#Skip A
                    for x in self.dealprob[str(next_stage)].items():
                        key, element = x
                        self.dealprob[dc][key]+=element*(1/13)                               
            else:#4~6 special A4, A5, A6 possible, skip A for now.
                for next_stage in range(int_dc+2,int_dc+10):#Skip A
                    for x in self.dealprob[str(next_stage)].items():
                        key, element = x
                        self.dealprob[dc][key]+=element*(1/13)
                for x in self.dealprob[str(int_dc+10)].items():
                        key, element = x
                        self.dealprob[dc][key]+=element*(4/13)                                 
        #print (self.dealprob)
        for dc in reversed(SOFT_CODE[:6]):#'AA', 'A2', 'A3', 'A4', 'A5', 'A6' SOFT_CODE_num={'AA':12, 'A2':13, 'A3':14, 'A4':15, 'A5':16, 'A6':17, 'A7':18, 'A8':19, 'A9':20}
            int_dc=SOFT_CODE_num[dc]
            HARD_CODE_num={'AA':2, 'A2':3, 'A3':4, 'A4':5, 'A5':6, 'A6':7}
            for d in range(1,11):
                if(d+int_dc<=17):
                    new_soft='A'+str(d+int_dc-11)
                    for x in self.dealprob[new_soft].items():
                        key, element = x
                        self.dealprob[dc][key]+=element*(1/13)  
                elif(d+int_dc>=18 and d+int_dc<=21): 
                    new_dc=str(d+int_dc)    
                    self.dealprob[dc][new_dc]+=(1/13)
                else:
                    hard_value=str(d+HARD_CODE_num[dc])
                    for x in self.dealprob[hard_value].items():
                        key, element = x
                        if(d==10):
                    	    self.dealprob[dc][key]+=element*(4/13)         
                        else:
                            self.dealprob[dc][key]+=element*(1/13)     
        for dc in range(4,7):
            for x in self.dealprob['A'+str(dc)].items():
                key, element = x
                self.dealprob[str(dc)][key]+=element*(1/13)            

        self.dealprob['4']['0']=0.39707515695847273
        self.dealprob['4']['17']=0.1224056331508635
        self.dealprob['4']['18']=0.12730742230390435
        self.dealprob['4']['19']=0.12275576094750927
        self.dealprob['4']['20']= 0.11785397179446842
        self.dealprob['4']['21']=0.1126020548447818
 

    # verify sum of initial table is close to 1    
    def verify_initial_table(self):
        total = 0.
        for x in self.initprob.xlabels:
            for y in self.initprob.ylabels:
                total += self.initprob[y,x]
        assert(isclose(total))

    def make_stand_ev_table(self):
        dealer_prob=self.dealprob
        lose_lists=['17','18','19','20','21']
        #STAND_CODE = HARD_CODE + ['21'] + SOFT_CODE
        #DEALER_CODE = HARD_CODE + SOFT_CODE[:6]
        for pc in HARD_CODE + ['21']:
            EV=0.0
            for dc in DEALER_CODE:
                EV=0.0
                if dc not in lose_lists:#if dealer is not 17<=dealer<=21, bust will happen, so take care first.
                    EV+=1*self.dealprob[dc]['0']
                #dealer WIN player LOSS
                if int(pc) <=16:#player 4~16
                    if(dc not in SOFT_CODE[:6]):# dealer is not softcode(As)
                        if(int(dc)>=17 and int(dc)<=21):
                            EV+=-1.0*dealer_prob[dc][dc] #IMMEDIATE win for dealer since player<17 but 17<=dealer<=21
                        else:
                            for i in lose_lists:#dealer<17
                                EV+=-1.0*dealer_prob[dc][i]
                    else:# dealer is soft code(As), AA to A6. A6 still hits
                        for i in lose_lists:
                            EV+=-1.0*dealer_prob[dc][i]                        
                elif pc in lose_lists :#player 17~21
                    if(pc==dc):#if player and dealer ties. Even for 21.
                        EV+=0.0
                    elif((dc not in SOFT_CODE[:6])and(int(pc)>int(dc))):#dealer is not softcode, and player > dealer
                        if (int(dc)>=17 and int(dc)<=21):#player and dealer both >=17, but pc>dc, so immediate win
                            EV+=1.0
                        else:
                            index = lose_lists.index(pc)
                            for i in lose_lists[0:index]:
                                EV+=1.0*dealer_prob[dc][i]
                            for i in lose_lists[index+1:]:
                                EV+=-1.0*dealer_prob[dc][i]    
                    elif((dc not in SOFT_CODE[:6])and(int(pc)<int(dc))):#dealer is not softcode, and player < dealer
                        EV+=-1.0#player and dealer both >=17, but pc<dc, so immediate loss
                    else:#dealer is softcode(As), AA to A6, A6 still hits
                        index = lose_lists.index(pc)
                        for i in lose_lists[0:index]:
                            EV+=1.0*dealer_prob[dc][i]
                        for i in lose_lists[index+1:]:
                            EV+=-1.0*dealer_prob[dc][i] 
                else:#AA~A9, next step
                    pass
                self.stand_ev[pc,dc]=EV
        #SOFT_CODE_num={'AA':12, 'A2':13, 'A3':14, 'A4':15, 'A5':16, 'A6':17, 'A7':18, 'A8':19, 'A9':20}
        for pc in SOFT_CODE:
            EV=0.0
            for dc in DEALER_CODE:
                EV=0.0
                if dc not in lose_lists:#if dealer is not 17<=dealer<=21, bust will happen, so take care first.
                    EV+=1*self.dealprob[dc]['0']
                if(SOFT_CODE_num[pc]<=16):#player is AA~A5
                    if(dc not in SOFT_CODE[:6]):# dealer is not softcode(As)
                        if(int(dc)>=17 and int(dc)<=21):#IMMEDIATE win for dealer since player<17 but 17<=dealer<=21
                            EV+=-1.0*dealer_prob[dc][dc] 
                        else:
                            for i in lose_lists:#dealer<17
                                EV+=-1.0*dealer_prob[dc][i]
                    else:# dealer is soft code(As), AA to A6. A6 still hits
                        for i in lose_lists:
                            EV+=-1.0*dealer_prob[dc][i]  
                elif SOFT_CODE_num[pc] in range (17,21):#player A6(17)~A9(20)
                    if(str(SOFT_CODE_num[pc])==dc):#if player and dealer ties.
                        EV+=0.0
                    elif((dc not in SOFT_CODE[:6])and(SOFT_CODE_num[pc]>int(dc))):#dealer is not softcode, and player > dealer
                        if (int(dc)>=17 and int(dc)<=21):#player and dealer both >=17, but pc>dc, so immediate win
                            EV+=1.0
                        else:
                            index = lose_lists.index(str(SOFT_CODE_num[pc]))
                            for i in lose_lists[0:index]:
                                EV+=1.0*dealer_prob[dc][i]
                            for i in lose_lists[index+1:]:
                                EV+=-1.0*dealer_prob[dc][i] 
                    elif((dc not in SOFT_CODE[:6])and(SOFT_CODE_num[pc]<int(dc))):#dealer is not softcode, and player < dealer
                        EV+=-1.0#player and dealer both >=17, but pc<dc, so immediate loss
                    else:#dealer is softcode(As), AA to A6, A6 still hits
                        index = lose_lists.index(str(SOFT_CODE_num[pc]))
                        for i in lose_lists[0:index]:
                            EV+=1.0*dealer_prob[dc][i]
                        for i in lose_lists[index+1:]:
                            EV+=-1.0*dealer_prob[dc][i]                                
                else:
                    pass
                    
                self.stand_ev[pc,dc]=EV
    
                      
    def make_double_ev_table(self):
        stand_ev=self.stand_ev
        all_hards=HARD_CODE+['21']
        for pc in reversed(HARD_CODE):
            EV=0
            index=all_hards.index(pc)
            if int(pc) > 11:#can bust
                proba_for_card=1/13
                bust_proba=1-(21-int(pc))/13
                for dc in DEALER_CODE:
                    EV=-2*bust_proba
                    for i in all_hards[index+1:]:
                        EV+=2*proba_for_card*stand_ev[i,dc]
                    self.double_ev[pc,dc]=EV
            elif int(pc) == 11: #can't bust and A = 1
                proba_for_card=1/13
                get_faceCard_proba=4/13
                for dc in DEALER_CODE:
                    EV=0
                    for i in all_hards[index+1:index+11]:
                        if int(pc)+10 == int(i):
                            EV+=2*get_faceCard_proba*stand_ev[i,dc]
                        else:
                            EV+=2*proba_for_card*stand_ev[i,dc]
                    self.double_ev[pc,dc]=EV
            elif int(pc) == 10: #can't bust and A = 11
                proba_for_card=1/13
                get_faceCard_proba=4/13
                for dc in DEALER_CODE:
                    EV=0
                    for i in all_hards[index+2:index+12]:
                        if int(pc)+10 == int(i):
                            EV+=2*get_faceCard_proba*stand_ev[i,dc]
                        else:
                            EV+=2*proba_for_card*stand_ev[i,dc]
                    self.double_ev[pc,dc]=EV
            elif int(pc) >= 4 and int(pc) < 10:#can't bust, 4~9
                proba_for_card=1/13
                get_faceCard_proba=4/13
                for dc in DEALER_CODE:
                    EV=0
                    for i in all_hards[index+2:index+11]:
                        if int(pc)+10 == int(i):
                            EV+=2*get_faceCard_proba*stand_ev[i,dc]
                        else:
                            EV+=2*proba_for_card*stand_ev[i,dc]
                    # add case for A4-A9
                    a_code = 'A'+pc
                    EV+=2*proba_for_card*stand_ev[a_code,dc]
                    self.double_ev[pc,dc]=EV
            
        # SOFT_CODE_num={'AA':12, 'A2':13, 'A3':14, 'A4':15, 'A5':16, 'A6':17, 'A7':18, 'A8':19, 'A9':20}
        for pc in reversed(SOFT_CODE):
            EV=0.0
            cards = [pc[0], pc[1]]
            hand_total, hand_is_soft = pointCalculator(cards)
            index=all_hards.index(str(hand_total))
            for dc in DEALER_CODE:
                EV=0.0
                for i in range(12, 22):
                    if i == hand_total:
                        EV+=2*(4/13)*stand_ev[str(i),dc]
                    else:
                        EV+=2*(1/13)*stand_ev[str(i),dc]
                self.double_ev[pc,dc]=EV

    def select_stand_or_hit(self, pcplus, dcplus):
        EV=0.0
        s=self.stand_ev[pcplus,dcplus]
        h=self.hit_ev[pcplus,dcplus]
        EV=max(s,h)
        return EV

    def make_hit_ev_table(self):
        #DEALER_CODE, NON_SPLIT_CODE
        #NON_SPLIT_CODE = HARD_CODE + SOFT_CODE
        #DEALER_CODE = HARD_CODE + SOFT_CODE[:6]
        for pc in reversed(HARD_CODE):
            int_pc=int(pc)
            for dc in DEALER_CODE:
                EV=0.0
                tjqk=13
                #self.calculate_hit_ev_cell(pc,dc)
                if(pc=='20'):#player with 20 can only win with Ace
                    EV+=((1/13)*self.stand_ev['21',dc])+(-1*(12/13))
                else:
                    if(int_pc>=11):#player>=11
                        for pcplus in range(int_pc+1, 21):#next hand from 1 to 9
                            EV+=(1/13)*self.select_stand_or_hit(str(pcplus),dc)
                            tjqk-=1
                        if(21-int_pc==10):#player=11, and got 21
                            EV+=(4/13)*self.stand_ev['21',dc]
                            tjqk-=4
                        else:#player not 11, and got 21
                            EV+=(1/13)*self.stand_ev['21',dc]
                            tjqk-=1
                        EV+=-1.0*(tjqk/13)#bust cases
                    elif(int_pc==10):#player=10, no bust
                        for pcplus in range(int_pc+2, int_pc+12):#A=11 in this case
                            if(pcplus-int_pc==10):#10+10=20
                                EV+=(4/13)*self.select_stand_or_hit(str(pcplus),dc)
                            else:
                                if pcplus==21:#10+11=21
                                    EV+=(1/13)*self.stand_ev['21',dc]
                                else:#12~19
                                    EV+=(1/13)*self.select_stand_or_hit(str(pcplus),dc)
                self.hit_ev[pc,dc]=EV
        # SOFT_CODE_num={'AA':12, 'A2':13, 'A3':14, 'A4':15, 'A5':16, 'A6':17, 'A7':18, 'A8':19, 'A9':20}       
        for pc in reversed(SOFT_CODE):
            for dc in DEALER_CODE:
                EV=0.0
                index = SOFT_CODE.index(pc)
                for pcplus in range(index+1,9):#from pc+1 to A9
                    EV+=(1/13)*self.select_stand_or_hit(SOFT_CODE[pcplus],dc)
                EV+=(1/13)*self.stand_ev['21',dc]#21
                for pcplus in range(12,SOFT_CODE_num[pc]):#from 12 up till pc-1 in HARD_CODE
                    EV+=(1/13)*self.select_stand_or_hit(str(pcplus),dc)
                EV+=(4/13)*self.select_stand_or_hit(str(SOFT_CODE_num[pc]),dc)#pc in HARD_CODE, has to have 10, so 4/13
                self.hit_ev[pc,dc]=EV

        for int_pc in range(9,3,-1):
            for dc in DEALER_CODE:
                EV=0.0
                for pcplus in range(int_pc+2, int_pc+11):#take care of Aces later
                    if(pcplus-int_pc==10):
                        EV+=(4/13)*self.select_stand_or_hit(str(pcplus),dc)
                    else:
                        EV+=(1/13)*self.select_stand_or_hit(str(pcplus),dc)
                a_pc='A'+str(int_pc)#A4~A9
                EV+=(1/13)*self.select_stand_or_hit(a_pc,dc)
                self.hit_ev[str(int_pc),dc]=EV
        



    def resplit0func(self):
        for pc in HARD_CODE + SOFT_CODE:
            for dc in DEALER_CODE:
                self.resplit0[pc,dc]=max(self.stand_ev[pc,dc], self.hit_ev[pc,dc], self.double_ev[pc,dc])
        for dc in DEALER_CODE:
            self.resplit0['21',dc]=self.stand_ev['21',dc]

    def resplit1func(self):
        #POINT_MAP = { "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "T":10, "J":10, "Q":10, "K":10, "A":11 }
        #SPLIT_CODE_sum = {'22':'4', '33':'6', '44':'8', '55':'10', '66':'12', '77':'14', '88':'16', '99':'18', 'TT':'20', 'AA':'AA' }
        #DISTINCT = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T' ]
        for string_half_pc in DISTINCT[1:]:#AA not allowed to split
            int_half_pc=POINT_MAP[string_half_pc]
            for dc in DEALER_CODE:
                EV=0.0
                for new_card in DISTINCT:
                    if(string_half_pc=='T'):
                        if(new_card=="T"):#T,TJQK
                            new_value=str(int_half_pc+POINT_MAP[new_card])
                            EV+=(4/13)*self.resplit0[new_value,dc]
                        else:#T,nonT
                            new_value=str(int_half_pc+POINT_MAP[new_card])
                            EV+=(1/13)*self.resplit0[new_value,dc]
                    else:#not A or T
                        if(new_card=="T"):#nonAT,TJQK
                            new_value=str(int_half_pc+POINT_MAP[new_card])
                            EV+=(4/13)*self.resplit0[new_value,dc]
                        elif(new_card=='A'):#nonAT,A
                            new_value=new_card+string_half_pc
                            EV+=(1/13)*self.resplit0[new_value,dc]
                        else:#nonAT,nonAT
                            new_value=str(int_half_pc+POINT_MAP[new_card])
                            EV+=(1/13)*self.resplit0[new_value,dc]
                self.resplit1[string_half_pc+string_half_pc,dc]=EV*2
                #self.split_ev[string_half_pc+string_half_pc,dc]=EV*2

    def resplit2func(self):
        #SPLIT_CODE = [ '22', '33', '44', '55', '66', '77', '88', '99', 'TT', 'AA' ]
        #DISTINCT = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T' ]
        for string_half_pc in DISTINCT[1:]:#AA not allowed to split
            for dc in DEALER_CODE:
                EV=0.0
                for non_split in DISTINCT:#NonSplitting hand
                    first_a=0.0
                    first_b=0.0
                    if(string_half_pc==non_split):
                        continue
                    else:
                        a_prob=0.0
                        b_prob=0.0
                #Case 1, happens twice
                #One of the hand will resplit, and the other will not, 
                # so (1/13 or 4/13)+(12/13 or 9/13)
                        if(string_half_pc=='T'):
                            a_prob=(4/13)
                            first_a=self.resplit1["TT",dc]
                        else:
                            a_prob=(1/13)
                            first_a=self.resplit1[string_half_pc+string_half_pc,dc]
                        if(string_half_pc=='T'):
                            if(non_split=="A"):
                                b_prob=(1/13)
                                first_b=self.resplit0["21",dc]
                            else:
                                b_prob=(1/13)
                                first_b=self.resplit0[str(10+int(non_split)),dc]
                        else:#not A or T
                            if(non_split=="T"):
                                b_prob=(4/13)
                                first_b=self.resplit0[str(10+int(string_half_pc)),dc]
                            elif(non_split=="A"):
                                b_prob=(1/13)
                                first_b=self.resplit0["A"+string_half_pc,dc]
                            else:
                                b_prob=(1/13)
                                first_b=self.resplit0[str(int(non_split)+int(string_half_pc)),dc]
                    EV+=(a_prob*b_prob)*(first_a+first_b)
                
                EV=EV+EV#Covered both sides

                #Case 2, both sides are splittable
                #Select one side ONCE, and it will be 
                # (1/13 or 4/13)+(1/13 or 4/13)
                second_EV=0.0
                if(string_half_pc=='T'):
                    second_EV+=self.resplit1["TT",dc]#TT, splitting again.
                    second_EV+=self.resplit0["20",dc]#TT, not splitting.
                    EV+=(4/13)*(4/13)*second_EV
                else:#not A or T
                    full_string=str(string_half_pc+string_half_pc)#nonTT, splitting again.
                    second_EV+=self.resplit1[full_string,dc]
                    new_value=str(int(string_half_pc)+int(string_half_pc))#nonTT, not splitting
                    second_EV+=self.resplit0[new_value,dc]
                    EV+=(1/13)*(1/13)*second_EV
                #Case 3, both sides are not splittable
                
                for a in DISTINCT:
                    for b in DISTINCT:
                        third_a=0.0
                        third_b=0.0
                        a_prob=(1/13)
                        b_prob=(1/13)
                        if(string_half_pc==a):
                            continue
                        if(string_half_pc==b):
                            continue

                        if(string_half_pc=='T' and a=='A'):
                            third_a=self.resplit0['21',dc]
                        elif(string_half_pc!='T' and a=='A'):                         
                            third_a=self.resplit0[a+string_half_pc,dc]
                        elif(a=='T'):
                            a_prob=(4/13)
                            third_a=self.resplit0['1'+string_half_pc,dc]
                        elif(string_half_pc=='T' and a!='T'):
                            third_a=self.resplit0[str(10+int(a)),dc]
                        else:
                            third_a=self.resplit0[str(int(string_half_pc)+int(a)),dc]
                            
                        if(string_half_pc=='T' and b=='A'):
                            third_b=self.resplit0['21',dc]
                        elif(string_half_pc!='T'and b=='A'):
                            third_b=self.resplit0[b+string_half_pc,dc]
                        elif(b=='T'):
                            b_prob=(4/13)
                            third_b=self.resplit0['1'+string_half_pc,dc]
                        elif(string_half_pc=='T' and b!='T'):
                            third_b=self.resplit0[str(10+int(b)),dc]
                        else:
                            third_b=self.resplit0[str(int(string_half_pc)+int(b)),dc]

                        EV+=a_prob*b_prob*(third_a+third_b)

                self.resplit2[string_half_pc+string_half_pc,dc]=EV
    def split_evfunc(self):
        for dc in DEALER_CODE:
            EV=0.0
            for a in DISTINCT:
                for b in DISTINCT:
                    third_a=0.0
                    third_b=0.0
                    a_prob=(1/13)
                    b_prob=(1/13)
                    if(a=='A'):
                        third_a=self.stand_ev['A'+a,dc]
                    elif(a=='T'):  
                        a_prob=(4/13)                       
                        third_a=self.stand_ev['21',dc]
                    else:
                        third_a=self.stand_ev['A'+a,dc]
                    if(b=='A'):
                        third_b=self.stand_ev['A'+b,dc]
                    elif(b=='T'):  
                        b_prob=(4/13)                       
                        third_b=self.stand_ev['21',dc]
                    else:
                        third_b=self.stand_ev['A'+b,dc]

                    EV+=a_prob*b_prob*(third_a+third_b)
            self.split_ev['AA',dc]=EV

        for string_half_pc in DISTINCT[1:]:#AA not allowed to split
            for dc in DEALER_CODE:
                EV=0.0
                for non_split in DISTINCT:#NonSplitting hand
                    first_a=0.0
                    first_b=0.0
                    if(string_half_pc==non_split):
                        continue
                    else:
                        a_prob=0.0
                        b_prob=0.0
                #Case 1, happens twice
                #One of the hand will resplit, and the other will not, 
                # so (1/13 or 4/13)+(12/13 or 9/13)
                        if(string_half_pc=='T'):
                            a_prob=(4/13)
                            first_a=self.resplit2["TT",dc]
                        else:
                            a_prob=(1/13)
                            first_a=self.resplit2[string_half_pc+string_half_pc,dc]
                        if(string_half_pc=='T'):
                            if(non_split=="A"):
                                b_prob=(1/13)
                                first_b=self.resplit0["21",dc]
                            else:
                                b_prob=(1/13)
                                first_b=self.resplit0[str(10+int(non_split)),dc]
                        else:#not A or T
                            if(non_split=="T"):
                                b_prob=(4/13)
                                first_b=self.resplit0[str(10+int(string_half_pc)),dc]
                            elif(non_split=="A"):
                                b_prob=(1/13)
                                first_b=self.resplit0["A"+string_half_pc,dc]
                            else:
                                b_prob=(1/13)
                                first_b=self.resplit0[str(int(non_split)+int(string_half_pc)),dc]
                    EV+=(a_prob*b_prob)*(first_a+first_b)
                
                EV=EV+EV#Covered both sides

                #Case 2, both sides are splittable
                #Select one side ONCE, and it will be 
                # (1/13 or 4/13)+(1/13 or 4/13)
                second_EV=0.0
                if(string_half_pc=='T'):
                    second_EV+=self.resplit1["TT",dc]#TT, splitting again.
                    second_EV+=self.resplit1["TT",dc]#TT, splitting again.
                    EV+=(4/13)*(4/13)*second_EV
                else:#not A or T
                    full_string=str(string_half_pc+string_half_pc)#nonTT, splitting again.
                    second_EV+=self.resplit1[full_string,dc]
                    second_EV+=self.resplit1[full_string,dc]
                    EV+=(1/13)*(1/13)*second_EV
                #Case 3, both sides are not splittable
                
                for a in DISTINCT:
                    for b in DISTINCT:
                        third_a=0.0
                        third_b=0.0
                        a_prob=(1/13)
                        b_prob=(1/13)
                        if(string_half_pc==a):
                            continue
                        if(string_half_pc==b):
                            continue

                        if(string_half_pc=='T' and a=='A'):
                            third_a=self.resplit0['21',dc]
                        elif(string_half_pc!='T' and a=='A'):                         
                            third_a=self.resplit0[a+string_half_pc,dc]
                        elif(a=='T'):
                            a_prob=(4/13)
                            third_a=self.resplit0['1'+string_half_pc,dc]
                        elif(string_half_pc=='T' and a!='T'):
                            third_a=self.resplit0[str(10+int(a)),dc]
                        else:
                            third_a=self.resplit0[str(int(string_half_pc)+int(a)),dc]
                            
                        if(string_half_pc=='T' and b=='A'):
                            third_b=self.resplit0['21',dc]
                        elif(string_half_pc!='T'and b=='A'):
                            third_b=self.resplit0[b+string_half_pc,dc]
                        elif(b=='T'):
                            b_prob=(4/13)
                            third_b=self.resplit0['1'+string_half_pc,dc]
                        elif(string_half_pc=='T' and b!='T'):
                            third_b=self.resplit0[str(10+int(b)),dc]
                        else:
                            third_b=self.resplit0[str(int(string_half_pc)+int(b)),dc]

                        EV+=a_prob*b_prob*(third_a+third_b)

                self.split_ev[string_half_pc+string_half_pc,dc]=EV
        


    def make_split_ev_table(self):
        self.resplit0func()
        self.resplit1func()
        self.resplit2func()
        self.split_evfunc()

    def get_strategy(self, pc, dc):
        EV=0.0
        s=self.stand_ev[pc,dc]
        h=self.hit_ev[pc,dc]
        d=self.double_ev[pc, dc]
        sp=self.split_ev[pc, dc]
        EV=max(s,h)
        return EV

#
# Calculate all the ev tables and the final strategy table and return them
# all in a dictionary
#      
    def make_optimal_ev_table(self):
        #PLAYER_CODE = HARD_CODE + SPLIT_CODE + SOFT_CODE[1:]
        for pc in HARD_CODE + SOFT_CODE[1:]:
            for dc in DEALER_CODE:
                max_ev=max(self.stand_ev[pc,dc], self.hit_ev[pc,dc], self.double_ev[pc,dc], -0.5)
                sec_option_max_ev=max(self.stand_ev[pc,dc], self.hit_ev[pc,dc])
                self.optimal_ev[pc,dc]=max_ev
                action=self.choose_action(pc, dc, max_ev, sec_option_max_ev)
                self.strategy[pc, dc]=action
        for pc in DISTINCT:
            for dc in DEALER_CODE:
                int_pc=0
                if(pc=='A'):
                    max_ev=max(self.split_ev['AA',dc], self.stand_ev['AA',dc], self.hit_ev['AA',dc], self.double_ev['AA',dc], -0.5)
                    sec_option_max_ev=max(self.stand_ev['AA',dc], self.hit_ev['AA',dc])
                    self.optimal_ev['AA',dc]=max_ev
                    if max_ev==self.split_ev['AA',dc]:
                        action='P'
                    else:
                        action=self.choose_action('AA', dc, max_ev, sec_option_max_ev)
                    self.strategy['AA', dc]=action
                elif(pc=='T'):
                    max_ev=max(self.split_ev['TT',dc], self.stand_ev['20',dc], self.hit_ev['20',dc], self.double_ev['20',dc], -0.5)
                    sec_option_max_ev=max(self.stand_ev['20',dc], self.hit_ev['20',dc])
                    self.optimal_ev['TT',dc]=max_ev
                    if max_ev==self.split_ev['TT',dc]:
                        action='P'
                    else:
                        action=self.choose_action('20', dc, max_ev, sec_option_max_ev)
                    self.strategy['TT', dc]=action
                else:
                    int_pc=str(int(pc)+int(pc))
                    max_ev=max(self.split_ev[pc+pc,dc], self.stand_ev[int_pc,dc], self.hit_ev[int_pc,dc],self.double_ev[int_pc,dc], -0.5)
                    sec_option_max_ev=max(self.stand_ev[int_pc,dc], self.hit_ev[int_pc,dc])
                    self.optimal_ev[pc+pc,dc]=max_ev
                    if max_ev==self.split_ev[pc+pc,dc]:
                        action='P'
                    else:
                        action=self.choose_action(int_pc, dc, max_ev, sec_option_max_ev)
                    self.strategy[pc+pc,dc]=action

    def choose_action(self, pc, dc, max_ev, sec_max):
        if max_ev==self.stand_ev[pc,dc]:
            action='S'
        elif max_ev==self.hit_ev[pc,dc]:
            action='H'
        elif max_ev==self.double_ev[pc,dc]:
            action='D'
            if sec_max==self.stand_ev[pc,dc]:
                action+='s'
            else:
                action+='h'
        else:
            action='R'
            if sec_max==self.stand_ev[pc,dc]:
                action+='s'
            else:
                action+='h'
        return action

    def make_advantage(self):
#self.initprob = Table(float, DEALER_CODE + ['BJ'], INITIAL_CODE, unit='%')
        x=0.0
        for i in INITIAL_CODE:
            for j in DEALER_CODE + ['BJ']:
                if(i=='BJ' and j=='BJ'):
                    self.advantage+=self.initprob[i,j]*0
                elif(i=='BJ' and j!='BJ'):
                    self.advantage+=self.initprob[i,j]*1.5
                elif(i!='BJ' and j=='BJ'):
                    self.advantage+=self.initprob[i,j]*(-1.0)
                else:    
                    self.advantage+=self.initprob[i,j]*self.optimal_ev[i,j]
                #x+=self.initprob[i,j]  

def calculate():
    calc = Calculator()   
    
    calc.make_initial_table()
    
    
    # TODO: uncomment once you finished your table implementation
    #       and Hand.code implementation
    calc.verify_initial_table()
    
    # TODO: calculate all other tables and numbers
    calc.make_dealer_dict()
    calc.make_stand_ev_table()
    calc.make_hit_ev_table()
    calc.make_double_ev_table()
    calc.make_split_ev_table()
    calc.make_optimal_ev_table()
    calc.make_advantage()
    return {
        'initial' : calc.initprob,
        'dealer' : calc.dealprob,
        'stand' : calc.stand_ev,
        'hit' : calc.hit_ev,
        'double' : calc.double_ev,
        'split' : calc.split_ev,
        'optimal' : calc.optimal_ev,
        'strategy' : calc.strategy,
        'advantage' : calc.advantage,
        "resplit" : [calc.resplit0, calc.resplit1, calc.resplit2],
    }

