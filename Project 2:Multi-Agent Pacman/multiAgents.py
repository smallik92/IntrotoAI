# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util
#import searchAgents
from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (newFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    


    "*** YOUR CODE HERE ***"
    distance_to_food = []
    distance_to_ghosts = 0
    food_locations = currentGameState.getFood().asList()
    
    if action == 'Stop':
        return -float("inf")
    
    for ghostState in newGhostStates:
        if ghostState.getPosition() == tuple(newPos) and ghostState.scaredTimer is 0:
            return -float("inf")
        
    GhostPositions=[Ghost.getPosition() for Ghost in newGhostStates]
    
    if len(GhostPositions)==0:
        distance_to_ghosts = 0
    else:
        for g in range(len(GhostPositions)):
            distance_to_ghosts += manhattanDistance(newPos,GhostPositions[g])
        
    
    for food in food_locations:
        dist = manhattanDistance(newPos,food)
        score = 1/(dist+0.000000001)
        distance_to_food.append(score)
    
    return -1/(distance_to_ghosts+0.00000001)+ max(distance_to_food)

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    
    startIndex = 0
    currDepth = 0
    legalActions = gameState.getLegalActions(startIndex) 
    maxValue = -1*float("inf")
    maxAction = None
    
    for action in legalActions:
        
        if action == "Stop":
            continue
        else:
            val = self.MinValue(gameState.generateSuccessor(startIndex,action),1,currDepth)

        if val> maxValue:
            maxValue = val
            maxAction = action
            
    return maxAction

  def MaxValue(self,gameState,depth):
      v = -1*float("inf")
      if depth == self.depth:
          return self.evaluationFunction(gameState)
      
      if len(gameState.getLegalActions(0)) == 0:
          return self.evaluationFunction(gameState)
      
      for action in gameState.getLegalActions(0):
          if action == "Stop":
              continue
          else:
              v = max(v,self.MinValue(gameState.generateSuccessor(0,action),1,depth))
      return v
  #    return max([self.MinValue(gameState.generateSuccessor(0,action),1,depth) for action in gameState.getLegalActions(0)])
  
  def MinValue(self,gameState,AgentIndex,depth):
      v = float("inf")
      
      if len(gameState.getLegalActions(AgentIndex)) ==0:
          return self.evaluationFunction(gameState)
      
      if AgentIndex < gameState.getNumAgents()-1:
          for action in gameState.getLegalActions(AgentIndex):
              if action == 'Stop':
                  continue
              else:
                  v = min(v,self.MinValue(gameState.generateSuccessor(AgentIndex,action),AgentIndex+1,depth))
          
      else:
          for action in gameState.getLegalActions(AgentIndex):
              if action == 'Stop':
                  continue
              else:
                  v = min(v,self.MaxValue(gameState.generateSuccessor(AgentIndex,action),depth+1))
      return v
#          return min([self.MaxValue(gameState.generateSuccessor(AgentIndex,action),depth+1) for action in gameState.getLegalActions(AgentIndex)])
      
        
      
   #util.raiseNotDefined()
    

class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """

  def getAction(self, gameState):
      
      startIndex = 0
      curDepth = 0
      maxValue = -1*float("inf")
      maxAction = None
      alpha = -1*float("inf")
      beta = 1*float("inf")
      legalActions = gameState.getLegalActions(startIndex)
      
      
      for action in legalActions:
          if action == 'Stop':
              continue
          else:
              maxValue = self.MinValue(gameState.generateSuccessor(startIndex,action),1,curDepth, alpha, beta)
 #             print maxValue
              if maxValue>alpha:
                  alpha = maxValue
                  maxAction = action
      return maxAction
  
  def MinValue(self,gameState,AgentIndex,depth,alpha,beta):
      v = float("inf")
      
      if len(gameState.getLegalActions(AgentIndex))==0:
          return self.evaluationFunction(gameState)
      
      for action in gameState.getLegalActions(AgentIndex):
          if action == 'Stop':
              continue
          
          if AgentIndex < gameState.getNumAgents()-1:
              v = min(v,self.MinValue(gameState.generateSuccessor(AgentIndex,action),AgentIndex+1,depth,alpha,beta))
          else:
              v = min(v,self.MaxValue(gameState.generateSuccessor(AgentIndex,action),depth+1,alpha,beta))
        
          if v < alpha:
              return v
          beta = min(beta,v)
          
      return v
  
  def MaxValue(self,gameState,depth,alpha,beta):
      v = -1*float("inf")
      
      if depth == self.depth:
          return self.evaluationFunction(gameState)
      
      if len(gameState.getLegalActions(0)) == 1:
          return self.evaluationFunction(gameState)
      
      for action in gameState.getLegalActions(0):
          if action == 'Stop':
              continue
          else:
              v = max(v,self.MinValue(gameState.generateSuccessor(0,action),1,depth,alpha,beta))
        
          if v > beta:
              return v
          alpha = max(alpha,v)
          
      return v
              
        
             
#    """
#      Returns the minimax action using self.depth and self.evaluationFunction
#    """
#    "*** YOUR CODE HERE ***"
#    util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  def getAction(self, gameState):
      
      maxValue = -1*float("inf")
      maxAction = None
      startIndex = 0
      depth = 0
      
      for action in gameState.getLegalActions(startIndex):
          if action == 'Stop':
              continue
          else:
              val = self.ExpValue(gameState.generateSuccessor(startIndex,action),startIndex+1, depth)
              
              if val> maxValue:
                  maxValue = val
                  maxAction = action
      return maxAction
  
  def ExpValue(self,gameState,AgentIndex,depth):
      sumValues = 0
      numActions = 0
      v = 0
      
      if len(gameState.getLegalActions(AgentIndex)) == 0:
          return self.evaluationFunction(gameState)
      
      for action in gameState.getLegalActions(AgentIndex):
          if action == 'Stop':
              continue
          else:
              if AgentIndex < gameState.getNumAgents()-1:
                  sumValues += self.ExpValue(gameState.generateSuccessor(AgentIndex,action), AgentIndex+1, depth)
                  numActions +=1
              else:
                  sumValues += self.MaxValue(gameState.generateSuccessor(AgentIndex,action),depth+1)
                  numActions +=1
                  
              v = float(sumValues/numActions)
      return v
  
  def MaxValue(self,gameState,depth):
      v = -1*float("inf")
      
      if depth == self.depth:
          return self.evaluationFunction(gameState)
      
      if len(gameState.getLegalActions(0)) == 0:
          return self.evaluationFunction(gameState)
      
      for action in gameState.getLegalActions(0):
          if action == "Stop":
              continue
          else:
              v = max(v,self.ExpValue(gameState.generateSuccessor(0,action),1,depth))
      return v
            
      
        
#    """
#      Returns the expectimax action using self.depth and self.evaluationFunction
#
#      All ghosts should be modeled as choosing uniformly at random from their
#      legal moves.
#    """
#    "*** YOUR CODE HERE ***"
    #util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    
    score = 0
    distance_to_food = []
    distance_to_Ghosts = []
    distance_to_pellet = []
    
    #extract useful information from a current gamestate
    foodPos = currentGameState.getFood().asList()
    currPacmanPosition = currentGameState.getPacmanPosition()
    currGhostStates = currentGameState.getGhostStates()
    powerPellets = currentGameState.getCapsules()
    
            
    #evaluation function score based on food pellet positions
    cur_Food = currPacmanPosition
    for food in foodPos:
        food_dist = manhattanDistance(food,cur_Food)
        distance_to_food.append(food_dist)
    if len(distance_to_food)>1:
        score+= 1.0/(min(distance_to_food)+0.000000001)
        minIndex = distance_to_food.index(min(distance_to_food))
        cur_Food = foodPos[minIndex]
        foodPos.remove(cur_Food)
    else:
        score+= 1000.0
    
    #evaluation function score based on Ghost locations
    if currentGameState.getNumAgents()>1:
        for ghost in currGhostStates:                
            ghost_Dis = manhattanDistance(currPacmanPosition,ghost.getPosition())
            distance_to_Ghosts.append(ghost_Dis)
            if ghost_Dis<=0.5:
                return -100000
        score-=3.0/(min(distance_to_Ghosts)+0.00000001)
        
    #evaluation function based on power pellet locations
    cur_Pellet = currPacmanPosition
    for pellet in powerPellets:
        pellet_dist = manhattanDistance(pellet,cur_Pellet)
        distance_to_pellet.append(pellet_dist)
    if len(distance_to_pellet)>1:
        score+= 1.0/(min(distance_to_pellet)+0.000000001)
        minIndex = distance_to_pellet.index(min(distance_to_pellet))
        cur_Pellet = powerPellets[minIndex]
        powerPellets.remove(cur_Pellet)
    else:
        score += 1000.0
        
    #evaluation function based on number of food pellets remaining
    score -= len(foodPos) +len(powerPellets)
    
    return score

  

        
    
#  """
#    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
#    evaluation function (question 5).
#
#    DESCRIPTION: <write something here so we know what you did>
#Weighted sum of features such as distance from closest power pellet, closest food pellet (both contributing in favor), closest ghost 
# (penalized heavily if ghost found in a very small radius), number of food pellets and power pellets left (both contributing against)
#  """
#  "*** YOUR CODE HERE ***"
#  util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

