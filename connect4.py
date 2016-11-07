#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import copy
import argparse
import numpy as np


class Jogo(object):
    
    def __init__(self, niveis=2, debug=False, demo=False):
        self.tabuleiro = Tabuleiro()
        self.vencedor = 0 # -1: jogador humano, 1: jogador ia
        self.turno_ia = False # começa com o jogador humano
        self.niveis = niveis
        self.debug = debug
        self.demo = demo
        
    def reiniciar(self):
        self.tabuleiro = Tabuleiro()
        self.vencedor = 0
        self.turno_ia = False
        self.iniciar()
    
    def iniciar(self):
        print '\n### Connect-4 ###'
        while self.vencedor == 0:
            if self.turno_ia:
                self.realizar_jogada()
            else:
                self.receber_jogada()
            
            self.avaliar_vencedor(Avaliacao(self.tabuleiro, jogador_ia=self.turno_ia))
            if self.turno_ia and self.demo: 
                self.mostrar_tabuleiro()
                break
            self.turno_ia = not self.turno_ia

                
    def receber_jogada(self):
        self.mostrar_tabuleiro()
        
        coluna = self.perguntar_coluna()
        
        while not self.tabuleiro.realizar_jogada(coluna, False):
            print '\nJogada inválida. Digite o número de uma coluna com posições vazias.'
            coluna = self.perguntar_coluna()
    
    def avaliar_vencedor(self, avaliacao):
        self.vencedor = avaliacao.vencedor
        
        if self.encerrado():
            self.mostrar_tabuleiro()
            
            if self.vencedor == -1:
                print '\nParabéns, você venceu!'
            elif self.vencedor == 1:
                print '\nVocê perdeu. Tente novamente!'
            else:
                print '\nA partida acabou empatada.'
            
            raw_input('\nPressione enter para iniciar um novo jogo...')
            self.reiniciar()
            
    def encerrado(self):
        return self.vencedor != 0 or self.tabuleiro.cheio()
    
    def realizar_jogada(self):
        colunas, _, _ = Minimax(self.niveis, self.debug).executar(self.tabuleiro)
        self.tabuleiro.realizar_jogada(colunas[0], True)
    
    def mostrar_tabuleiro(self):
        print ''
        for i in xrange(6): # linhas
            print '%d|' % (i+1),
            for j in xrange(7): # colunas
                peca = self.tabuleiro.get_peca(i, j)
                if peca == 1: print 'x',
                elif peca == -1: print 'o',
                else: print '_',
                
                if j == 6: print '|'
                
        print '   1 2 3 4 5 6 7'
                
    def perguntar_coluna(self):
        while True:
            try:
                coluna = input('\nEm qual coluna você deseja realizar sua jogada? ') - 1
                if coluna < 0 or coluna > 6:
                    raise Exception()
                
                return coluna
            except Exception:
                print '\nJogada inválida. Digite um número 1 até 7.'
                
class Avaliacao(object):
    
    PESOS = np.array([1, 50, 5000, 500000])
    
    def __init__(self, tabuleiro, jogador_ia=True, ultimo_nivel_impar=False):
        self.ultimo_nivel_impar = ultimo_nivel_impar
        self.tabuleiro = tabuleiro
        self.resultado = self.avaliar(jogador_ia)
        self.vencedor = 0
        if self.resultado > self.PESOS[3] - self.PESOS[2]*7:
            self.vencedor = 1 if jogador_ia else -1


    def contar_ameacas(self, jogador, adversario, ameacas, quadrupla):
        if adversario not in quadrupla:
            index_ameaca = int(np.sum(quadrupla == jogador)) - 1
            if index_ameaca >= 0:
                ameacas[index_ameaca] += 1
        elif jogador not in quadrupla:
            index_ameaca = int(np.sum(quadrupla == adversario)) - 1
            if index_ameaca >= 0:
                index_ameaca += 1 if self.ultimo_nivel_impar else 0
                index_ameaca = min(index_ameaca, 3)
                ameacas[index_ameaca] -= 1

    def avaliar(self, jogador_ia=True):
        adversario = -1 if jogador_ia else 1
        jogador = -adversario
        ameacas = np.zeros(4)
        
        for i in xrange(3):
            for j in xrange(4):
                
                window = self.tabuleiro.estado[i:i+4, j:j+4]
                diagonal_principal = window.diagonal()
                diagonal_secundaria = np.fliplr(window).diagonal()
                
                self.contar_ameacas(jogador, adversario, ameacas, diagonal_principal)
                self.contar_ameacas(jogador, adversario, ameacas, diagonal_secundaria)
                
                for k in xrange(4):
                    linha = window[k,:]
                    coluna = window[:,k]
                    self.contar_ameacas(jogador, adversario, ameacas, linha)
                    self.contar_ameacas(jogador, adversario, ameacas, coluna)
                    
        return np.sum(ameacas * self.PESOS)
        

class Tabuleiro(object):
    
    def __init__(self):
        self.estado = np.zeros((6, 7))
        
    def get_peca(self, i, j):
        return self.estado[i, j]
    
    def realizar_jogada(self, coluna, jogador_ia=True):
        if not self.jogada_valida(coluna): 
            return False
        
        linha = max(np.where(self.estado[:,coluna] == 0)[0])
        self.estado[linha, coluna] = 1 if jogador_ia else -1
        return True
    
    def jogada_valida(self, coluna):
        return coluna is not None and coluna >= 0 and coluna <= 6 and self.estado[0, coluna] == 0
    
    def cheio(self):
        return self.estado[0,:].all()
    
    def copia(self):
        t = Tabuleiro()
        t.estado = self.estado.copy()
        return t
        
        
class Minimax(object):
    
    def __init__(self, niveis=2, debug=False):
        self.niveis = niveis
        self.debug = debug
    
    def executar(self, tabuleiro, alpha=float("-inf"), beta=float("inf"), jogador_ia=True, colunas=[], nivel=0):
        if nivel == 0:
            avaliacao = Avaliacao(tabuleiro, jogador_ia=jogador_ia)
        else:
            avaliacao = Avaliacao(tabuleiro, jogador_ia=True, ultimo_nivel_impar=nivel==self.niveis and nivel % 2 != 0)
        
        if nivel == self.niveis or avaliacao.vencedor != 0:
            return copy.copy(colunas), tabuleiro, avaliacao.resultado / float(nivel+1)

        
        jogadas = self.gerar_jogadas(tabuleiro, jogador_ia)
        
        c, t = colunas, tabuleiro
        if jogador_ia:
            for col, tab in jogadas:
                cols = copy.copy(colunas) + [col]
                cs, tb, score = self.executar(tab, alpha, beta, not jogador_ia, cols, nivel=nivel+1)
                if self.debug: print ' ' * nivel, 'MAX:', cs, '\n', ' ' * nivel, tb.estado, score
                if score > alpha: 
                    alpha = score
                    c = cs
                    t = tb
                if alpha >= beta:
                    if self.debug: print ' ' * nivel, 'PODOU MAX (alpha, beta):', alpha, beta
                    break
            
            if self.debug: print ' ' * nivel, 'ESCOLHIDO MAX:', c, '\n', ' ' * nivel, t.estado, alpha
            return c, t, alpha
        else:
            for col, tab in jogadas:
                cols = copy.copy(colunas) + [col]
                cs, tb, score = self.executar(tab, alpha, beta, not jogador_ia, cols, nivel=nivel+1)
                if self.debug: print' ' * nivel,  'MIN:', cs, '\n', ' ' * nivel, tb.estado, score
                if score < beta: 
                    beta = score
                    c = cs
                    t = tb
                if alpha >= beta: 
                    if self.debug: print ' ' * nivel, 'PODOU MIN (alpha, beta):', alpha, beta
                    break
            
            if self.debug: print ' ' * nivel, 'ESCOLHIDO MIN:', c, '\n', ' ' * nivel, t.estado, beta
            return c, t, beta
        
        
    def gerar_jogadas(self, tabuleiro, jogador_ia=True):
        colunas = np.where(tabuleiro.estado[0,:] == 0)[0]
        jogadas = []
        for i in xrange(len(colunas)):
            t = tabuleiro.copia()
            t.realizar_jogada(colunas[i], jogador_ia=jogador_ia)
            jogadas.append((colunas[i], t))
            
        return jogadas
        

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--niveis' , nargs='?', default=2, type=int)
        parser.add_argument('-d', '--debug', action='store_true', default=False)
        args = parser.parse_args()
        Jogo(niveis=args.niveis, debug=args.debug).iniciar()
    except KeyboardInterrupt:
        print "\nSaindo..."
        sys.exit(0)

