# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        iterations = self.iterations
        states = (self.mdp).getStates()
        for i in range(iterations):
            newValues = {}
            for s in states:
                bestAction = self.computeActionFromValues(s)
                newValues[s] = self.computeQValueFromValues(s, bestAction)
            self.values = newValues
        return

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        if action not in (self.mdp).getPossibleActions(state):
            return 0
        total = 0
        successors = (self.mdp).getTransitionStatesAndProbs(state, action)
        for s in successors:
            sState = s[0] # successor state
            sProb = s[1] # successor probability
            sReward = (self.mdp).getReward(state, action, sState)
            vStar = self.getValue(sState)
            q = sProb * (sReward + self.discount * vStar)
            total += q
        return total

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        if (self.mdp).isTerminal(state):
            return None
        legalActions = (self.mdp).getPossibleActions(state)
        actionValues = {}
        for action in legalActions:
            actionValues[action] = self.computeQValueFromValues(state, action)
        maxValue = max(actionValues.values())
        for k,v in actionValues.items():
            if v == maxValue:
                return k

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        iterations = self.iterations
        states = (self.mdp).getStates()
        for i in range(iterations):
            index = i % len(states)
            if not (self.mdp).isTerminal(states[index]):
                bestAction = self.computeActionFromValues(states[index])
                self.values[states[index]] = self.computeQValueFromValues(states[index], bestAction)
        return

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        predecessor = dict.fromkeys((self.mdp).getStates(), set())
        qDict = dict()
        for state in (self.mdp).getStates():
            # Compute predecessors of all states
            actions = (self.mdp).getPossibleActions(state)
            for a in actions:
                successor = (self.mdp).getTransitionStatesAndProbs(state, a)[0][0]
                predecessor[successor].add(state)
        pq = util.PriorityQueue()
        for state in (self.mdp).getStates():
            if not (self.mdp).isTerminal(state):
                actions = (self.mdp).getPossibleActions(state)
                qvalues = [self.computeQValueFromValues(state, a) for a in actions]
                diff = abs(self.getValue(state) - max(qvalues))
                qDict[state] = max(qvalues)
                pq.push(state, -diff)
        for i in range(self.iterations):
            if pq.isEmpty():
                # If the priority queue is empty, then terminate
                return
            s = pq.pop() # Pop a state s off the priority queue
            if not (self.mdp).isTerminal(s):
                # Update s's value (if it is not a terminal state) in self.values
                self.values[s] = qDict[s]
            for p in predecessor[s]:
                actions = (self.mdp).getPossibleActions(p)
                qvalues = [self.computeQValueFromValues(p, a) for a in actions]
                diff = abs(self.values[p] - max(qvalues))
                if diff > self.theta:
                    qDict[p] = max(qvalues)
                    pq.update(p, -diff)
