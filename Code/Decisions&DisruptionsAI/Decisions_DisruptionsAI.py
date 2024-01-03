import os
import numpy as np

class gamestate(object):
    def __init__(self, Agent):
        self.currentBudget = 100
        self.budgetIncrease = 100
        self.currentTurn = 1
        self.maxturns = 4
        self.Agent = Agent
        self.possible_Attacks = []
        self.available_attacks = []
        self.active_attacks = []
        self.active_defences = []
        self.available_defences = []
        self.possible_defences = []
        self.Realreward = np.array(
                    [["Scanning Kiddie",0,10],
                    ["DoSing Kiddie",0,5],
                    ["Hacking Kiddie",0,10,10],
                    ["Phishing Kiddie",0,20,10],
                    ["Mafia APT PC Offices",0,20,10,10],
                    ["Mafia APT Server Offices",0,30,10,10,10],
                    ["Mafia APT Server Plant",0,10,10,10],
                    ["Mafia Disruption Controller",0,10,10,10],
                    ["Nation State Intelligence",0,10,10,10],
                    ["Nation State Disruption",0,100]], dtype="object")
    #increment the turn
    def incrementturn(self):
        self.currentTurn += 1
        self.currentBudget += self.budgetIncrease
        totalattacks = len(self.active_attacks)
        for i in range(totalattacks):
            self.active_attacks[totalattacks-i-1].attack_check(self)
    #return the current budget
    def getbudget(self):
        return self.currentBudget
    #pay for defence
    def payment(self,price):
        self.currentBudget -= price
    #add defence to active defences
    def addDefence(self, name):
        self.active_defences.append(name)
        print(self.active_defences)
    #reset game for new episode
    def resetGame(self, currentBudget, budgetIncrease, availableAttacks, availableDefences):
        self.currentBudget = currentBudget
        self.budgetIncrease = budgetIncrease
        
        self.available_attacks = availableAttacks.copy()
        self.available_defences = availableDefences.copy()
        self.active_attacks = []
        self.active_defences = []
        self.currentTurn = 1
        for i in self.possible_Attacks:
            i.stage = 0
            i.prevstage = 0

                
    
class defences(object):
    def __init__(self, name, target, price, needAssetAudit):
        self.name = name
        #what component it defends
        self.target = target
        self.active = False
        self.price = price
        self.needAssetAudit = needAssetAudit
    #activates the defense
    def defense_activate(self, Game):
        if self.needAssetAudit == True:
            for i in Game.active_defences:
                if i == "Asset Audit":
                    if self.price < Game.getbudget():
                        self.active = True
                           
        elif self.price < Game.getbudget():
            self.active = True
        if self.active == True:
            Game.payment(self.price)
            Game.addDefence(self.name)
            Game.available_defences.remove(self)
            if self.name == "Asset Audit":
                for i in Game.possible_defences:
                    if i.needAssetAudit:
                        Game.available_defences.append(i)
        return Game    
        


class attacks(object):
    def __init__(self, name, counters, group,maxstage):
        self.name = name
        #what defences counter the attack
        self.counters = counters
        #what component does the attack effect
        #what reward will the reinforcement learning algorithm get
        self.group = group
        self.prevstage = 0
        self.stage = 0
        self.maxstage = maxstage
        

		# checks if a defense that counters an attack is already installed to see if the attack is succesful
    def attack_check(self, Game):
        passcheck = True
		#loops through defences that counter attack
        
        turncheck = 1
        
        
        stagestopped = -1
        #get list of names on the counters
        for i in self.counters[::2]:
            turncheck = 1
            #get the stages the defences counter them on
            
            for y in self.counters[turncheck]:
                
                #check if stage has changed this turn
                if self.prevstage != self.stage:
                    if y-1 in range(self.prevstage, self.stage):
                        #check if defence is installed
                        if i in Game.active_defences:
                            if y < stagestopped or stagestopped == -1:
                                stagestopped = y
                            passcheck = False;
                            break
                    if passcheck == False:
                            break
                else:
                    if y == self.stage:
                        if i in Game.active_defences:
                            if y < stagestopped or stagestopped == -1:
                                stagestopped = y
                            passcheck = False;
                            break
                        if passcheck == False:
                            break
                turncheck+= 2
        #deactivate attack if check has been triggered
        if passcheck == False:
            Game.active_attacks.remove(self)
            print(self.name + " disabled")
        Game.Agent.train(self.name, self.stage, stagestopped, self.prevstage)
        self.prevstage = self.stage
        return Game
    #activate attack
    def attack_activate(self, Game):
        self.stage += 1
        if self not in Game.active_attacks:
             Game.active_attacks.append(self)
        print(self.name + " chosen")
        #check if attack chain has finished
        if self.stage == self.maxstage:
            Game.available_attacks.remove(self)
            
            #check if scan has been completed resulting in Dos and Hacking being added
            if self.name == "Scanning Kiddie":
                check = 0
                for i in Game.possible_Attacks:
                    if i.name == "DoSing Kiddie":
                        Game.available_attacks.append(i)
                        check += 1
                    elif i.name == "Hacking Kiddie":
                        Game.available_attacks.append(i)
                        check += 1
                    if check == 2:
                        return Game
        return Game

class Agent(object):
    def __init__(self):
        self.certainty = 0.9
        self.Perceivedreward = np.array([["Scanning Kiddie",0,10],
                    ["DoSing Kiddie",0,0],
                    ["Hacking Kiddie",0,0,0],
                    ["Phishing Kiddie",0,0,0],
                    ["Mafia APT PC Offices",0,0,0,0],
                    ["Mafia APT Server Offices",0,0,0,0,0],
                    ["Mafia APT Server Plant",0,0,0,0],
                    ["Mafia Disruption Controller",0,0,0,0],
                    ["Nation State Intelligence",0,0,0,0],
                    ["Nation State Disruption",0,10]], dtype="object")
        self.attackamount = np.array([[0],
                    [0],
                    [0,0],
                    [0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0],
                    [0,0,0],
                    [0,0,0],
                    [0]], dtype="object")
        self.totaluses = np.array([[0],
                    [0],
                    [0,0],
                    [0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0],
                    [0,0,0],
                    [0,0,0],
                    [0]], dtype="object")
    #choose what attack will be inputted based on current perceived rewards
    def calculateAttack(self, Game):
        options = []
        stages= []
        k = 0
        for i in Game.available_attacks:
            options.append(i.name)
            stages.append(i.stage)
        predictedincrease = []
        k = 0
        for i in options:
            predictedincrease.append(self.predict(i,stages[k]))
            k += 1
        #if randomly generated number is higher than current certainty return available attack stage with current highest perceived reward
        #if not return a different randomly selected attack
        if len(options) == 1:
            return options[0]
        elif np.random.random() > self.certainty:
            return options[np.argmax(predictedincrease)]
        else:
            options.remove(options[np.argmax(predictedincrease)])
            if k == 2:
                return options[0]
            else:
                p = np.random.randint(k-1)
                return options[p]
            
            
                
            
            

            #return current perceived reward of an attack
    def predict(self, Attackname,stage):
        for i in range(len(self.Perceivedreward)):
            if Attackname == self.Perceivedreward[i][0]:
                return self.Perceivedreward[i][stage+2]
                


    #update perceived rewards
    def train(self, Attackname, stage, stoppedstage, prevstage):
        for i in range(len(self.Perceivedreward)):
            if Attackname == self.Perceivedreward[i][0]:
                #check if the attack has been stopped
                if stoppedstage != -1:
                    for j in range(stage):
                        #update perceived reward
                        if j>prevstage-1:
                            
                            oldvalue = self.Perceivedreward[i][j+2] * self.totaluses[i][j]
                            newvalue = int(Game.Realreward[i][j+2]) + oldvalue
                            #if attack was stopped lower reward
                            if j >= stoppedstage-1:
                                newvalue = 0 + oldvalue
                            self.attackamount[i][j] += 1
                            self.totaluses[i][j] += 1
                            newvalue = newvalue/self.totaluses[i][j]
                            self.Perceivedreward[i][j+2] = newvalue
                        
                    break

                else:
                    for j in range(stage):
                        if j>prevstage-1:
                            oldvalue = self.Perceivedreward[i][j+2] * self.totaluses[i][j]
                            newvalue = int(Game.Realreward[i][j+2]) + oldvalue
                            self.totaluses[i][j] += 1
                            self.attackamount[i][j] += 1
                            newvalue = newvalue/self.totaluses[i][j]
                            self.Perceivedreward[i][j+2] = newvalue
                        
                    break
                

        return Game
    #print the current perceived rewards
    def printrewards(self):
        for i in range(len(self.Perceivedreward)):
            for j in range(len(self.Perceivedreward[i])):
                if j == 0:
                    print(str(self.Perceivedreward[i][j]), end = '')
                elif j>1:
                    print(", Stage: " + str(j - 1) + ", Reward: " + str(self.Perceivedreward[i][j]) + ", times used: " + str(self.totaluses[i][j-2]), end = '')
            print("")
            print("")
        
    def updatecertainty():
        if self.certainty > 0.1:
            self.certainty *= 0.999
                        
                    
                    



if __name__ == '__main__':
    
   #setting up Agent and gamespace objects
    Attacker = Agent()
    Game = gamestate(Attacker)
    #seting up defence objects
    sectraining = defences("security training","everything",30,False)
    firewallPlant = defences("Firewall (Plant)","plant",30,False)
    firewallOffice = defences("Firewall (Office)","office",30,False)
    cctvPlant = defences("CCTV (Plant)","plant",50,False)
    cctvOffice = defences("CCTV (Office)","office",50,False)
    netMonPlant = defences("Network Monitoring (Plant)","plant",50,False)
    netMonOffice = defences("Network Monitoring (Office)","office",50,False)
    antiVirus = defences("Anti Virus","everything",30,False)
    assetAudit = defences("Asset Audit","everything",30,False)
    threatAssesment = defences("Threat Assesment","everything",20,False)
    servUp = defences("Server Upgrade","server",30,True)
    pcEnc = defences("PC Encryption","pcs",20,True)
    dbEnc = defences("Database Encryption","database",20,True)
    contUp = defences("Controller Upgrade","Scata controller",30,True)
    pcUp = defences("Pc Upgrade","pcs",30,True)
    #set up attack objects
    SK = attacks("Scanning Kiddie",["Firewall (Office)",[1]],0,1)

    DK = attacks("DoSing Kiddie",["Firewall (Office)",[1]],0,1)

    HK = attacks("Hacking Kiddie",["Server Upgrade",[1], "Network Monitoring (Office)",[2],"Database Encryption",[2] ],0,2)

    PK = attacks("Phishing Kiddie",["security training",[1], "Anti Virus",[1,2],"Pc Upgrade",[1,2]],0,2)
    
    MAPTPC = attacks("Mafia APT PC Offices",["security training",[1], "Anti Virus",[1,2,3],"Network Monitoring (Office)",[2,3],"PC Encryption",[3] ],1,3)

    MAPTPSO = attacks("Mafia APT Server Offices",["security training",[1], "Network Monitoring (Office)",[2,3,4],"PC Encryption",[3,4] ],1,4)

    MAPTPSP = attacks("Mafia APT Server Plant",["Asset Audit",[1], "Server Upgrade",[2],"Network Monitoring (Plant)",[2,3],"Database Encryption",[3] ],1,3)

    MDC = attacks("Mafia Disruption Controller",["Firewall (Plant)",[1,2],"Controller Upgrade",[2,3]],1,3)

    NSI = attacks("Nation State Intelligence",["CCTV (Plant)",[1],"Network Monitoring (Plant)",[2,3]],2,3)

    NSD = attacks("Nation State Disruption",["CCTV (Plant)",[1]],2,1)
    possibleAttacks = [SK, DK, HK, PK, MAPTPC, MAPTPC, MAPTPC, MAPTPSO, MAPTPSP, MDC, NSI, NSD]
    availableAttacks = [SK, PK, MAPTPC, MAPTPSO, MAPTPSP, MDC, NSI, NSD]
    availableDefences = [sectraining, firewallPlant, firewallOffice, cctvPlant, cctvOffice, netMonPlant, netMonOffice, antiVirus, assetAudit, threatAssesment]
    possibleDefences = [sectraining, firewallPlant, firewallOffice, cctvPlant, cctvOffice, netMonPlant, netMonOffice, antiVirus, assetAudit, threatAssesment, servUp, pcEnc, dbEnc, contUp, pcUp]
   
    
    
    Game.possible_Attacks = possibleAttacks
    Game.possible_defences = possibleDefences
    numofepisodes = 2500
    defencechoice = 0
    print("Enter 1 for defences to be entered randomly or 2 to enter defences manually")
    while defencechoice != "1" and defencechoice != "2":
        defencechoice = input()
    for episode in range(numofepisodes):
        #reset gamestate for new epispode
        Game.resetGame(100, 100, availableAttacks, availableDefences)
        while Game.currentTurn-1 < Game.maxturns:
            choice = ''
            while choice != '2':
                print("current Money is " + str(Game.currentBudget))
                if defencechoice == "2":
                    print("Enter 1 to enter a defence, Enter 2 to End the turn, Enter 3 to print the current perceived reward, Enter 4 to manually enter an attack if debugging is needed")
                    choice = input()
                elif defencechoice == "1":
                    #choose randome defences
                    for i in range(2):
                        defenceindex = np.random.randint(len(Game.available_defences))
                        Game.available_defences[defenceindex].defense_activate(Game)
                    choice = "2"
                #clear console
                os.system('cls')
                print("episode number " + str(episode + 1))
                print("turn number is " +str(Game.currentTurn))
                if choice == '1':
                    for i in range(len(Game.available_defences)):
                        print ("Enter " + str(i + 1) + " for " + Game.available_defences[i].name)
                    i = input()
                    if i.isnumeric():
                        Game.available_defences[int(i)-1].defense_activate(Game)
                elif choice == '2':
                    for i in range(3):
                        if len(availableAttacks) != 0:
                            attack = str(Attacker.calculateAttack(Game))
                            for i in Game.possible_Attacks:
                                if attack == i.name:
                                    Game = i.attack_activate(Game)
                                    break
                    Game.incrementturn();
                elif choice == '3':
                    Game.Agent.printrewards()
                   
                elif choice == '4':
                    attackname = input()
                    for i in Game.possible_Attacks:
                        if i.name == attackname:
                            Game = i.attack_activate(Game)
                            break
                
                
                
        Game.Agent.updatecertainty;
    Game.Agent.printrewards()
