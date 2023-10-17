class Dados_Entrada:
    
    def __init__(self, num_steps, alpha, beta, gama, delta, epsilon, grau = 2):
        
        self.num_steps = num_steps
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.delta = delta 
        self.epsilon = epsilon
        self.grau = grau

        self.t0 = 0
        pi = np.pi
        T = 4 * pi
        self.dt = T/self.num_steps
    
    def __repr__(self) ->str:
        return str(self.num_steps)