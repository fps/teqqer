class Action(object):
    """Describes an action, and a way to revert that action"""
     
    def __init__(self, do, undo):
        """Both do and undo are in the form (function, [arg1, arg2, ...])."""
        self._do = do
        self._undo = undo

    def do(self):
        fun, args = self._do
        return fun(*args)

    def undo(self):
        fun, args = self._undo
        return fun(*args)


class History(object):
    "Maintains a list of actions that can be undone and redone."

    def __init__(self):
        self._actions = []
        self._last = -1

    def _push(self, action):
        if self._last < len(self._actions) - 1:
            # erase previously undone actions
            del self._actions[self._last + 1:]
        self._actions.append(action)
        self._last = self._last + 1
        
    def undo(self):
        if self._last < 0:
            return None
        else:
            action = self._actions[self._last]
            self._last = self._last - 1
            return action.undo()
            
    def redo(self):
        if self._last == len(self._actions) - 1:
            return None
        else:
            self._last = self._last + 1
            action = self._actions[self._last]
            return action.do()

    def add(self, do, undo):
        """Does an action and adds it to history.

        Both do and undo are in the form (function, [arg1, arg2, ...]).

        """
        action = Action(do, undo)
        self._push(action)
        return action.do()
