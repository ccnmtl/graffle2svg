class CascadingStyles(object):
    def __init__(self, defaults = None):
        if defaults is None:
            defaults = {}
        self.defaults = defaults
        self.scopes = []
        
        
    def appendScope(self,scope=None):
        """Add a new scope for styles"""
        if scope is None:
            scope = {}
        self.scopes.append(scope)
    
    def popScope(self):
        """remove the most recent scope of styles"""
        return self.scopes.pop(-1)
        
    def __getitem__(self, k):
        """get the current setting for the style"""
        for scope in self.scopes[::-1]:
            if scope.get(k) is not None:
                return scope[k]
                
        if self.defaults.get(k) is not None:
            return self.defaults[k]
        else:
            raise KeyError(str(k))
        
        
    def __setitem__(self, k, v):
        """Set a style in the current scope"""
        self.scopes[-1][k] = v
        
    def __str__(self):
        style = self.currentStyle()
        return ";".join(["%s:%s"%(k,v) for (k,v) in style.items()])
        
    def currentStyle(self):
        """return all styles applied at this point"""
        styles = {}
        for scope in self.scopes:
            styles.update(scope)
        
        for key,v in self.defaults.items():
            if styles.get(key,None) == v:
                del styles[key]
        return styles
        
    def scopeStyle(self):
        """return the styles of this scope only"""
        one_scope = CascadingStyles(defaults = self.defaults)
        one_scope.appendScope(self.scopes[-1])
        return one_scope
