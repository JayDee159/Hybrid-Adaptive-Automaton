from collections import defaultdict, Counter
from copy import deepcopy
from typing import Hashable, Callable, Dict, Set, Tuple, Optional

class State:
    __slots__ = ("name", "is_terminal", "metadata", "visits")
    def __init__(self, name: Hashable, is_terminal=False, metadata=None):
        self.name = name
        self.is_terminal = is_terminal
        self.metadata = metadata or {}
        self.visits = 0

class Transition:
    __slots__ = ("source", "target", "predicate", "action", "hits")
    def __init__(self, source: Hashable, target: Hashable,
                 predicate: Callable[[Hashable, 'State'], bool],
                 action: Optional[Callable[[Hashable, 'State'], None]] = None):
        self.source = source
        self.target = target
        self.predicate = predicate
        self.action = action
        self.hits = 0

class HybridAutomaton:
    def __init__(self, start_state: Hashable):
        self.states: Dict[Hashable, State] = {start_state: State(start_state)}
        self.transitions: Set[Transition]  = set()
        self.start_state = start_state
        self.current     = self.states[start_state]
        
    def add_state(self, name: Hashable, **kwargs):
        if name not in self.states:
            self.states[name] = State(name, **kwargs)
    
    def add_transition(self, source, target, predicate, action=None):
        self.add_state(source)
        self.add_state(target)
        self.transitions.add(Transition(source, target, predicate, action))
    
    def step(self, symbol: Hashable):
        print(f"Processing symbol: '{symbol}' from state: '{self.current.name}'")
        self.current.visits += 1
        fired = False
        
        for tr in self.transitions:
            if tr.source == self.current.name and tr.predicate(symbol, self.current):
                fired = True
                tr.hits += 1
                print(f"  → Transition fired: {tr.source} → {tr.target}")
                if tr.action:
                    tr.action(symbol, self.current)
                self.current = self.states[tr.target]
                break
        
        if not fired:
            new_state_name = f"S{len(self.states)}"
            print(f"  → No transition found! Creating new state: {new_state_name}")
            self.add_transition(self.current.name,
                                new_state_name,
                                predicate=lambda s, _cs, sym=symbol: s == sym)
            self.current = self.states[new_state_name]
        
        print(f"  Current state now: '{self.current.name}'")
        return self.current
    
    def run(self, iterable):
        print(f"Starting execution from state: '{self.current.name}'")
        for sym in iterable:
            self.step(sym)
        final_result = self.current.is_terminal
        print(f"Final state: '{self.current.name}', Terminal: {final_result}")
        return final_result
    
    def prune(self, min_state_visits=2, min_tr_hits=2):
        remove_states = {k for k, st in self.states.items()
                         if st.visits < min_state_visits and k != self.start_state}
        self.states = {k: v for k, v in self.states.items() if k not in remove_states}
        self.transitions = {tr for tr in self.transitions
                            if tr.hits >= min_tr_hits and
                               tr.source not in remove_states and
                               tr.target not in remove_states}
    
    def simulate(self, inputs):
        sandbox = deepcopy(self)
        terminal = sandbox.run(inputs)
        return terminal, sandbox
    
    def link_ontology(self, state_name, concept_uri):
        self.states[state_name].metadata["concept"] = concept_uri
    
    def stats(self):
        return {
            "states": len(self.states),
            "transitions": len(self.transitions),
            "current_state": self.current.name,
            "current_is_terminal": self.current.is_terminal
        }
    
    def print_automaton_structure(self):
        print("\n=== AUTOMATON STRUCTURE ===")
        print("States:")
        for name, state in self.states.items():
            terminal_mark = " (TERMINAL)" if state.is_terminal else ""
            visits_info = f" [visits: {state.visits}]"
            print(f"  {name}{terminal_mark}{visits_info}")
        
        print("Transitions:")
        for tr in self.transitions:
            hits_info = f" [hits: {tr.hits}]"
            print(f"  {tr.source} → {tr.target}{hits_info}")
        print("=" * 30)

if __name__ == "__main__":
    print("HYBRID ADAPTIVE AUTOMATA – CODE + OUTPUT")
    print("=" * 60)

    HA = HybridAutomaton(start_state="START")

    # Initial rules
    HA.add_transition("START", "FEVER", 
                      predicate=lambda s, _st: s == "fever",
                      action=lambda s, st: print(f"    Action: Detected symptom '{s}'"))

    HA.add_transition("FEVER", "FLU", 
                      predicate=lambda s, _st: s == "cough",
                      action=lambda s, st: print(f"    Action: Confirming diagnosis with '{s}'"))

    HA.states["FLU"].is_terminal = True

    HA.print_automaton_structure()

    print("\n1) NORMAL DIAGNOSIS RUN:")
    print("Input: ['fever', 'cough']")
    result1 = HA.run(["fever", "cough"])
    print(f"Diagnosis: {'FLU' if result1 else 'Unknown'}")
    print("Stats:", HA.stats())

    print("\n2) ONLINE LEARNING RUN:")
    HA.current = HA.states[HA.start_state]
    print("Input: ['rash', 'sneeze', 'fever']")
    result2 = HA.run(["rash", "sneeze", "fever"])
    print(f"Terminal reached: {result2}")
    print("Stats after learning:", HA.stats())

    print("\n3) SANDBOX SIMULATION:")
    print("Testing: ['fever', 'headache']")
    terminal, sandbox = HA.simulate(["fever", "headache"])
    print("Sandbox terminal reached:", terminal)
    print("Original automaton current state:", HA.current.name)

    print("\n4) PRUNING UNDERUSED LOGIC:")
    HA.prune()
    print("Stats after pruning:", HA.stats())

    print("\nDone.")
