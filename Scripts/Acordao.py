#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Acordao:

    def __init__( self, idAcordao, tribunal, relator, virtual):
        self.idAcordao = idAcordao
        self.tribunal = tribunal
        self.relator = relator
#        self.citacoes = citacoes
 #       self.similares = similares
        self.virtual = virtual

    def getId( self):
        return self.idAcordao

    def getTribunal( self):
        return self.tribunal

    def getRelator( self):
        return self.relator

  #  def getCitacoes( self):
   #     return self.citacoes

  #  def getSimilares( self):
   #     return self.similares
    
    def getVirtual( self):
        return self.virtual
