# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class InferenceAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        
        CaptureAgent.registerInitialState(self, gameState)
        
        #Details of the board, useful to determine in which zone agent is
        self.midWidth = gameState.data.layout.width/2
        self.midHeight = gameState.data.layout.height/2
        
        #Get legalpositions
        self.legalPositions = [p for p in gameState.getWalls().asList(False)]
        
        # Get Indices of my Team
        self.teams = self.getTeam(gameState)
        self.opponents = self.getOpponents(gameState)
        
        # choose random action with epsilon
        self.epsilon = 0.001
#        self.alpha = 0.1
#        self.Qval = util.Counter()
        
#    def getQValue(self,gameState,state,action):
#        return self.evaluate(gameState,action)
#    
#    def getValue(self,gameState,state):
#        legalActions = gameState.getLegalActions(self.index)
#        
#        if not legalActions:
#            return 0.0
#        
#        value = -1*float('inf')
#        for action in legalActions:
#            value = max(value,self.getQValue(gameState,state,action))
#            
#        return value
#          
#    def getPolicy(self,gameState,state):
#        policy = util.Counter()
#        legalActions = gameState.getLegalActions(self.index)
#        if not legalActions:
#            return None
#        for action in legalActions:
#            policy[action] = self.getQValue(gameState, state, action)
#        return policy.argMax()
#    
#    def update(self,gameState,state,action):
        
               
    def chooseAction(self,gameState):
        
        #base choose action function; chooses score maximizing action
        
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        if util.flipCoin(self.epsilon):
            return_action = random.choice(actions)
        else:
            return_action = random.choice(bestActions)

        return return_action
                
    def evaluate(self, gameState, actions):
        features = self.getFeatures(gameState, actions)
        weights = self.getWeights(gameState, actions)
        
        return features*weights
    
    def getFeatures(self,gameState,actions):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features
    
    def getWeights(self,gameState, actions):
        return {'successorScore': 1.0}
    
    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor
        
    
class OffensiveReflexAgent(InferenceAgent):
    
    #This is an offensive agent that aims to eat food pellets but hides (or attempts to)
    #when it finds a ghost nearby. When it is almost near the end and quite close to its own territory
    # it employs a retreating strategy and hovers around the center of the board
    
    def registerInitialState(self, gameState):
        InferenceAgent.registerInitialState(self, gameState)
        self.retreating = False   #flag to indicate whether or not retreating

    def getFeatures(self, gameState, action):
        
        feature = util.Counter()
        
        scaredTimes = [gameState.getAgentState(opponent).scaredTimer for opponent in self.opponents]
        curScore = self.getScore(gameState)
        
        feature['current score'] = curScore
        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentPosition(self.index)
        
        successorScore = self.getScore(successor)
        feature['successor score'] = successorScore
        
        foodPos = self.getFood(successor).asList() #target food pellets
        
        if self.red:
            targetCapsule = successor.getBlueCapsules()
        else:
            targetCapsule = successor.getRedCapsules()
        
        #feature that pulls the Pacman closer to food pellets
        cur_Food = myPos
        distance_to_food = []
        for food in foodPos:
            food_dist = self.getMazeDistance(food, cur_Food)
            distance_to_food.append(food_dist)
            
        if len(distance_to_food) == 0:
            feature['min food dist'] = 0
        else:
            feature['min food dist'] = min(distance_to_food)
            
        
        #feature that finds nearest power pellet     
        curCapsule = myPos    
        distance_to_Capsule = []
        for capsule in targetCapsule:
            distance_to_Capsule.append(self.getMazeDistance(curCapsule, capsule))
        
        if len(distance_to_Capsule) == 0:
            feature['min capsule dist'] = 0
        else:
            feature['min capsule dist'] = min(distance_to_Capsule)
            
        #features calculating the items on board left
        feature['num food left'] = len(foodPos)
        feature['num capsule left'] = len(targetCapsule)
        
        #feature that takes into account if opponent agent is ghost, if ghosts are nearby and if ghosts are scared
        ghostDis = []
        for opponent in self.opponents:
            if not successor.getAgentState(opponent).isPacman and successor.getAgentPosition(opponent) is not None:
                ghostDis.append(self.getMazeDistance(myPos,successor.getAgentPosition(opponent)))
        if len(ghostDis)>0:
            if min(scaredTimes)>2:
                feature['min ghostDist'] = 20
            else:
                if min(ghostDis) <= 0.25:
                    feature['min ghostDist'] = -10
                else:
                    feature['min ghostDist'] = min(ghostDis)
        else:
            feature['min ghostDist'] = 0
            
        
        #calculate how far you are from own territory
        distanceFromStart = min([self.distancer.getDistance(myPos, (self.midWidth, i)) for i in range(gameState.data.layout.height) if (self.midWidth, i) in self.legalPositions])
    
        feature['distance from center'] = distanceFromStart    
            
        if len(ghostDis)>0:
            if (len(foodPos)<=3 and distanceFromStart <= 2) or (min(ghostDis)<=0.25 and distanceFromStart <= 2):
                self.retreating = True
            else:
                self.retreating = False
            
        
        
        return feature
        
    def getWeights(self, gameState, action):
        weights = util.Counter()
        feature = self.getFeatures(gameState,action)
        if not self.retreating:
            weights['num food left'] = -15
            
            if feature['num food left'] <=3 and feature['num capsule left']>0:
                weights['num capsule left'] = -15
                weights['min capsule dist'] = -5
            else:
                weights['num capsule left'] = -5   
                weights['min capsule dist'] = -1
            weights['min food dist'] = -5
            weights['current score'] = 1
            weights['successor score'] = 100
            weights['min ghostDist'] = 5
            weights['distance from center'] = 0
        else:
            weights['num food left'] = -1
            weights['num capsule left'] = 0
            weights['min capsule dist'] = 0
            weights['min food dist'] = -1
            weights['current score'] = 0
            weights['successor score'] = 150
            weights['min ghostDist'] = 15
            weights['distance from center'] = -10
        
        return weights
        

        
class DefensiveReflexAgent(InferenceAgent):
  # this is a defensive reflex agent that uses all the features from baseline
  # plus more, namely: prefers to have more food and power pellets uneaten by opponent

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1
    
    if self.red:
        Capsules_to_defend = successor.getRedCapsules()
    else:
        Capsules_to_defend = successor.getBlueCapsules()
        
    features['power pellet'] = len(Capsules_to_defend)
    
    features['food pellet'] = len(self.getFoodYouAreDefending(successor).asList())
                

    return features

  def getWeights(self, gameState, action):
      
    weights = util.Counter()
    weights['numInvaders'] = -1500
    weights['onDefense'] = 100
    weights['invaderDistance'] = -20
    weights['stop'] = -100
    weights['reverse'] = -2
    weights['power pellet'] = 10
    weights['food pellet'] = 200
    
    return weights

    
        
                    
        
        
                
        
    
                
        
        
        
        
    
        
        
        
        
        