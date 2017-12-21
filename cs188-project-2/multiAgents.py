# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

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
        pos = currentGameState.getPacmanPosition()
        newPos = successorGameState.getPacmanPosition()
        food = currentGameState.getFood()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        minDist = 9999
        for x in range(newFood.width):
            for y in range(newFood.height):
                if newFood[x][y]:
                    dist = util.manhattanDistance((x,y), newPos)
                    if dist < minDist: minDist = dist # returns distance to closest food, want to min
         # total distance from food, want to min
        newGhostPositions = successorGameState.getGhostPositions() # list of ghost positions
        disList = [util.manhattanDistance((x,y), newPos) for x,y in newGhostPositions]
        ghostHeuristic = min(disList) # returns distance from closest ghost, want to max

        handicap = 0
        if newScaredTimes[0] > ghostHeuristic + 1: # if ate pellet, chase ghost
            return newScaredTimes[0]-ghostHeuristic
        if newPos == pos:
            handicap = -40
        if food[newPos[0]][newPos[1]] == True:
            handicap += 60
        if ghostHeuristic > 4: # if far away from ghost
            return 10/(minDist) + handicap # - min **2
        return ghostHeuristic**2

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

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.isWin():
            Returns whether or not the game state is a winning state

          gameState.isLose():
            Returns whether or not the game state is a losing state
        """
        # add parameter for last move? how does terminal state know last action?
        maxDepth = self.depth
        numAgents = gameState.getNumAgents()
        def value(state, depth):
            if depth == maxDepth * numAgents or state.isLose() or state.isWin():
                return [self.evaluationFunction(state)]
            if depth % numAgents == 0:
                return maxValue(state, depth)
            else:
                return minValue(state, depth)

        def maxValue(state, depth):
            maxLeaf = -9999
            maxMove = None
            legalMoves = state.getLegalActions(depth % numAgents)
            for move in legalMoves:
                successor = value(state.generateSuccessor(depth % numAgents, move), depth + 1)
                if successor[0] > maxLeaf:
                    maxLeaf = successor[0]
                    maxMove = move
            return (maxLeaf, maxMove)
        def minValue(state, depth):
            minLeaf = 9999
            minMove = None
            legalMoves = state.getLegalActions(depth % numAgents)
            for move in legalMoves:
                successor = value(state.generateSuccessor(depth % numAgents, move), depth + 1)
                if successor[0] < minLeaf:
                    minMove = move
                    minLeaf = successor[0]
            return (minLeaf, minMove)
        return value(gameState, 0)[1]


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        maxDepth = self.depth
        numAgents = gameState.getNumAgents()
        def value(state, depth, alpha, beta):
            if depth == maxDepth * numAgents or state.isLose() or state.isWin():
                return [self.evaluationFunction(state)]
            if depth % numAgents == 0:
                return maxValue(state, depth, alpha, beta)
            else:
                return minValue(state, depth, alpha, beta)

        def maxValue(state, depth, alpha, beta):
            maxLeaf = -9999
            maxMove = None
            legalMoves = state.getLegalActions(depth % numAgents)
            for move in legalMoves:
                successor = value(state.generateSuccessor(depth % numAgents, move), depth + 1, alpha, beta)
                if successor[0] > maxLeaf:
                    maxLeaf = successor[0]
                    maxMove = move
                if maxLeaf > beta: return (maxLeaf, maxMove)
                alpha = max(alpha, maxLeaf)
            return (maxLeaf, maxMove)
        def minValue(state, depth, alpha, beta):
            minLeaf = 9999
            minMove = None
            legalMoves = state.getLegalActions(depth % numAgents)
            for move in legalMoves:
                successor = value(state.generateSuccessor(depth % numAgents, move), depth + 1, alpha, beta)
                if successor[0] < minLeaf:
                    minLeaf = successor[0]
                    minMove = move
                if minLeaf < alpha: return (minLeaf, minMove)
                beta = min(beta, minLeaf)
            return (minLeaf, minMove)
        return value(gameState, 0, -9999, 9999)[1]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        maxDepth = self.depth
        numAgents = gameState.getNumAgents()
        def value(state, depth):
            if depth == maxDepth * numAgents or state.isLose() or state.isWin():
                return [self.evaluationFunction(state)]
            if depth % numAgents == 0:
                return maxValue(state, depth)
            else:
                return expValue(state, depth)

        def maxValue(state, depth):
            maxLeaf = -9999
            maxMove = None
            legalMoves = state.getLegalActions(depth % numAgents)
            for move in legalMoves:
                successor = value(state.generateSuccessor(depth % numAgents, move), depth + 1)
                if successor[0] > maxLeaf:
                    maxLeaf = successor[0]
                    maxMove = move
            return (maxLeaf, maxMove)
        def expValue(state, depth):
            legalMoves = state.getLegalActions(depth % numAgents)
            n = float(len(legalMoves))
            total = 0.0
            for move in legalMoves:
                successor = value(state.generateSuccessor(depth % numAgents, move), depth + 1)
                total += successor[0]
            return [float(total)/n]
        return value(gameState, 0)[1]

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    pos = currentGameState.getPacmanPosition() # current position
    food = currentGameState.getFood() # food grid
    legalMoves = currentGameState.getLegalActions() # possible moves
    successors = [currentGameState.generatePacmanSuccessor(action) for action in legalMoves]
    successorPos = [currentGameState.generatePacmanSuccessor(action).getPacmanPosition() for action in legalMoves] # position of possible next state

    sFood = [s.getNumFood() for s in successors]
    if sFood:
        avgFood = currentGameState.getNumFood() - float(sum(sFood))/len(sFood)
    else:
        avgFood = 0

    numFood = 0
    for s in successorPos:
        if food[s[0]][s[1]]:
            numFood += 1
    # counts food pellets around current position

    pellets = currentGameState.getCapsules() # positions of power pellets
    if pellets:
        pelletDistance = [util.manhattanDistance(pos, d) for d in pellets]
        closestPellet = min(pelletDistance)
    else:
        closestPellet = 0

    minDist = 9999
    total = 0
    n = 0
    for x in range(food.width):
        for y in range(food.height):
            if food[x][y]:
                dist = util.manhattanDistance((x,y), pos)
                total += dist
                n += 1
                if dist < minDist: minDist = dist # returns distance to closest food, want to min
    if n != 0:
        avgDist = total/n
    else:
        avgDist = 0

    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    newGhostPositions = currentGameState.getGhostPositions() # list of ghost positions
    disList = [util.manhattanDistance((x,y), pos) for x,y in newGhostPositions]
    ghostHeuristic = min(disList) # returns distance from closest ghost, want to max

    score = currentGameState.getScore()
    numMoves = len(legalMoves) # number of available moves
    if currentGameState.getNumFood() == 0:
        return 999 + score
    if ghostHeuristic == 0:
        return -999
    if newScaredTimes[0] > ghostHeuristic + 1: # if ate pellet, chase ghost
        return score + newScaredTimes[0] - ghostHeuristic
    if ghostHeuristic > 4: # if far away from ghost
        return score + avgFood*20 + numMoves + numFood - minDist*4  - closestPellet/2 # 10/(minDist)
    return score + ghostHeuristic**2 + numMoves/2 + avgFood*10 + numFood/2 - minDist - closestPellet/4

# Abbreviation
better = betterEvaluationFunction
