import numpy as np

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
        return str(f"num_steps: {self.num_steps}, alpha: {self.alpha}, beta: {self.beta}, gama: {self.gama}, delta: {self.delta}, epsilon: {self.epsilon}, grau: {self.grau}")

if __name__ == "__main__":

    problema = Dados_Entrada(100, 1, 0.25, 0.5, 0.002, 1)
    print(problema)