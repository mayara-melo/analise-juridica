from scrapy.item import Item, Field

class StjItem(Item):
    acordaoId   = Field()
    localSigla  = Field()
 #   tipo        = Field()
    relator     = Field()
 #   orgaoJulg   = Field()
    dataJulg    = Field()
#    fontePublic = Field()
    dataPublic  = Field()
    ementa      = Field()
    decisao     = Field()
    citacoes    = Field()
    tribunal    = Field()
    notas       = Field()
    index       = Field()
#    sucessivos  = Field()
    legislacao  = Field()
#    observacao  = Field()
#    tudo        = Field()

class StjLawItem(Item):
    tipo   = Field()
    ano    = Field()
    numero = Field()
