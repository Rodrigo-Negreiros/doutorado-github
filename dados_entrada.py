import numpy as np

class Dados_Entrada:
    
    def __init__(self, num_steps, alpha, beta, gama, delta, epsilon, p, grau = 2, **kwargs):
        
        self.num_steps = num_steps
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.delta = delta 
        self.epsilon = epsilon
        self.p = p
        self.grau = grau
        
        self.t0 = 0
        self.pi = np.pi
        T = 4 * self.pi
        self.dt = T/self.num_steps
    
    def retorna_dados(self):
        return self.num_steps, self.alpha, self.beta, self.gama, self.delta, self.epsilon, self.p, self.grau, self.t0, self.pi
    
    def __repr__(self) -> str:
        return str(f"num_steps: {self.num_steps}, alpha: {self.alpha}, beta: {self.beta}, gama: {self.gama}, delta: {self.delta}, epsilon: {self.epsilon}, p: {self.p}, grau: {self.grau}")

if __name__ == "__main__":
    
    valores = {'num_steps' : 100, 
               'alpha' : 1, 
               'beta' : 0.25, 
               'gama' : 0.5, 
               'delta' : 0.002, 
               'epsilon': 1, 
               'p' : 4, 
               'grau':2
               }
    
    problema = Dados_Entrada(**valores)
    print(problema)