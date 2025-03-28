import uuid

class Produto:
    def __init__(self, produtoCategoria, nome, preco, urlImagem, descricao):
        self.id = str(uuid.uuid4())  # Sempre gera um novo UUID
        self.produtoCategoria = produtoCategoria  # Partition Key
        self.nome = nome
        self.preco = preco
        self.urlImagem = urlImagem
        self.descricao = descricao

    def to_dict(self):
        """Converte o objeto para um dicionário JSON para salvar no CosmosDB."""
        return {
            "id": self.id,
            "produtoCategoria": self.produtoCategoria,  # Partition Key
            "nome": self.nome,
            "preco": self.preco,
            "urlImagem": self.urlImagem,
            "descricao": self.descricao
        }

    @staticmethod
    def from_dict(data):
        """Cria um objeto Produto a partir de um dicionário JSON."""
        return Produto(
            produtoCategoria=data["produtoCategoria"],
            nome=data["nome"],
            preco=data["preco"],
            urlImagem=data["urlImagem"],
            descricao=data["descricao"],
        )