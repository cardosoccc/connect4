#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import heapq
import argparse
import numpy as np


class Jogo(object):
    
    def __init__(self):
        self.tabuleiro = Tabuleiro()
        self.vencedor = 0 # -1: jogador humano, 1: jogador ia
        self.turno_ia = False # começa com o jogador humano
        
    def reiniciar(self):
        self.__init__()
        self.iniciar()
    
    def iniciar(self):
        print '\n### Connect-4 ###'
        while self.vencedor == 0:
            if self.turno_ia:
                self.realizar_jogada()
            else:
                self.receber_jogada()
            
            self.avaliar_vencedor(Avaliacao(self.tabuleiro, jogador_ia=self.turno_ia))
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
            
            raw_input('\nPressione enter para inicar um novo jogo...')
            self.reiniciar()
            
    def encerrado(self):
        return self.vencedor != 0 or self.tabuleiro.cheio()
    
    def realizar_jogada(self):
        coluna = np.random.choice(np.where(self.tabuleiro.estado[0,:] == 0)[0])
        self.tabuleiro.realizar_jogada(coluna, True)
    
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
    
    def __init__(self, tabuleiro, jogador_ia=True):
        self.tabuleiro = tabuleiro
        self.resultado = self.avaliar(jogador_ia)
        self.vencedor = 0
        if self.resultado > self.PESOS[3]:
            self.vencedor = 1 if jogador_ia else -1
        
    def avaliar(self, jogador_ia=True):
        adversario = -1 if jogador_ia else 1
        ameacas = np.zeros(4)
        for i in xrange(3):
            for j in xrange(4):
                
                window = self.tabuleiro.estado[i:i+4, j:j+4]
                
                for k in xrange(4):
                    linha = window[k,:]
                    coluna = window[:,k]
                    diagonal_principal = window.diagonal()
                    diagonal_secundaria = np.fliplr(window).diagonal()
                    
                    if adversario not in linha:
                        index_ameaca = int(np.sum(linha == -adversario)) - 1
                        if index_ameaca >= 0:
                            ameacas[index_ameaca] += 1
                    
                    if adversario not in coluna:
                        index_ameaca = int(np.sum(coluna == -adversario)) - 1
                        if index_ameaca >= 0:
                            ameacas[index_ameaca] += 1
                    
                if adversario not in diagonal_principal:
                    index_ameaca = int(np.sum(diagonal_principal == -adversario)) - 1
                    if index_ameaca >= 0:
                        ameacas[index_ameaca] += 1
                        
                if adversario not in diagonal_secundaria:
                    index_ameaca = int(np.sum(diagonal_secundaria == -adversario)) - 1
                    if index_ameaca >= 0:
                        ameacas[index_ameaca] += 1
        
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
        

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        args = parser.parse_args()
        Jogo().iniciar()
    except KeyboardInterrupt:
        print "\nSaindo..."
        sys.exit(0)

