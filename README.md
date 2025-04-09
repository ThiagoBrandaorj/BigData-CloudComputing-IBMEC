# Projeto E-commerce IBMEC - Cloud Computing

API de e-commerce desenvolvida para a disciplina de Big Data e Cloud Computing do IBMEC.

## Grupo
- Guilherme Duran Duran Gea
- Pedro de Castro 
- Thiago Correa Brandão

## Arquitetura

A aplicação utiliza uma arquitetura híbrida de armazenamento:

- **MySQL** (Azure Database for MySQL): Armazena dados relacionais como usuários, endereços e cartões.
- **Azure Cosmos DB**: Armazena dados de produtos, aproveitando a escalabilidade e flexibilidade para catálogos de produtos.
- **Azure App Service**: Hospeda a API RESTful baseada em Flask que gerencia todas as operações.

## URL Base da API

```
https://ibmec-ecommerce-produtos-thpedu-hpgdamgyc3c4grgx.centralus-01.azurewebsites.net
```

## Endpoints da API

## Usuários

### Criar Usuário
- **Método**: POST
- **Endpoint**: `/usuario`
- **Corpo da Requisição**:
```json
{
    "nome": "João Silva",
    "email": "joao@exemplo.com",
    "dt_nascimento": "204-12-20",
    "cpf": "12345678900",
    "telefone": "11987654321"
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Usuário criado com sucesso",
    "usuario_id": 1
}
```

### Obter Usuário por Id
- **Método**: GET
- **Endpoint**: `/usuario/{id}`
- **Resposta de Sucesso**:
```json
{
    "id": 1,
    "nome": "João Silva",
    "email": "joao@exemplo.com",
    "cpf": "12345678900",
    "telefone": "11987654321"
}
```

### Obter Usuários
- **Método**: GET
- **Endpoint**: `/usuario`
- **Resposta de Sucesso**:
```json
{
    "id": 1,
    "nome": "João Silva",
    "email": "joao@exemplo.com",
    "cpf": "12345678900",
    "telefone": "11987654321"
},
{
    "id": 2,
    "nome": "Maria Silva",
    "email": "maria@exemplo.com",
    "cpf": "12345678900",
    "telefone": "11987654321"
}
```

### Atualizar Usuário
- **Método**: PUT
- **Endpoint**: `/usuario/{id}`
- **Corpo da Requisição**:
```json
{
    "nome": "João Silva Atualizado",
    "email": "joao.atualizado@exemplo.com",
    "telefone": "11999999999"
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Usuário atualizado com sucesso"
}
```

### Deletar Usuário
- **Método**: DELETE
- **Endpoint**: `/usuario/{id}`
- **Resposta de Sucesso**:
```json
{
    "message": "Usuário deletado com sucesso"
}
```

## Endereços

### Criar Endereço
- **Método**: POST
- **Endpoint**: `/endereco/usuario/{id_user}`
- **Corpo da Requisição**:
```json
{
    "logradouro": "Estrada dos Três Rios 1200",
    "complemento": "",
    "bairro": "Freguesia",
    "cidade": "Rio de Janeiro",
    "uf": "RJ",
    "cep": "22745003",
    "pais": "Brasil",
    "tipo": "Comercial"
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Endereço criado com sucesso",
    "endereco_id": 1
}
```

### Obter Endereços do Usuário
- **Método**: GET
- **Endpoint**: `/endereco/usuario/{id_user}`
- **Resposta de Sucesso**:
```json
[
    {
        "id": 1,
        "logradouro": "Rua Exemplo",
        "numero": "123",
        "complemento": "Apto 45",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234567"
    }
]
```

### Atualizar Endereço
- **Método**: PUT
- **Endpoint**: `/endereco/{id_endereco}`
- **Corpo da Requisição**:
```json
{
    "logradouro": "Avenida Atualizada",
    "bairro": "Novo Bairro",
    "cidade": "Rio de Janeiro",
    "estado": "RJ",
    "cep": "09876543"
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Endereço atualizado com sucesso"
}
```

### Deletar Endereço
- **Método**: DELETE
- **Endpoint**: `/endereco/{id_endereco}`
- **Resposta de Sucesso**:
```json
{
    "message": "Endereço deletado com sucesso"
}
```

## Cartões

### Criar Cartão
- **Método**: POST
- **Endpoint**: `/cartao/usuario/{id_user}`
- **Corpo da Requisição**:
```json
{
    "numero": "5555666677778888",
    "nome_impresso": "JOAO SILVA",
    "validade": "12/2026",
    "cvv": "123",
    "bandeira": "mastercard",
    "tipo": "credito",
    "saldo": 5000.00
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Cartão criado com sucesso",
    "cartao_id": 1
}
```

### Autorizar Transação
- **Método**: POST
- **Endpoint**: `/cartao/authorize/usuario/{id_user}`
- **Corpo da Requisição**:
```json
{
    "numero": "5555666677778888",
    "cvv": "123",
    "dt_expiracao": "12/2026",
    "valor": 159.90
}
```
- **Resposta de Sucesso**:
```json
{
    "status": "AUTHORIZED",
    "codigo_autorizacao": "8f9d2a3b-6c87-4f1d-9a5b-2e7d1c8a6b3f",
    "dt_transacao": "2025-03-30T23:45:12.345Z",
    "message": "Compra autorizada"
}
```

### Atualizar Saldo do Cartão
- **Método**: PUT
- **Endpoint**: `/cartao/saldo/{id_cartao}`
- **Corpo da Requisição**:
```json
{
    "saldo": 3500.00
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Saldo atualizado com sucesso",
    "cartao_id": 1,
    "saldo": 3500.00
}
```

### Deletar Cartão
- **Método**: DELETE
- **Endpoint**: `/cartao/{id_cartao}`
- **Resposta de Sucesso**:
```json
{
    "message": "Cartão deletado com sucesso"
}
```

## Produtos

### Criar Produto
- **Método**: POST
- **Endpoint**: `/produto`
- **Corpo da Requisição**:
```json
{
    "produtoCategoria": "eletronicos",
    "nome": "Smartphone Galaxy S21",
    "preco": 3999.99,
    "urlImagem": "https://exemplo.com/imagens/galaxy-s21.jpg",
    "descricao": "Smartphone Samsung Galaxy S21 com 128GB de armazenamento e 8GB de RAM"
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Produto criado com sucesso",
    "produto_id": "8f9d2a3b-6c87-4f1d-9a5b-2e7d1c8a6b3f"
}
```

### Obter Produto por ID
- **Método**: GET
- **Endpoint**: `/produto/{id}`
- **Resposta de Sucesso**:
```json
{
    "id": "8f9d2a3b-6c87-4f1d-9a5b-2e7d1c8a6b3f",
    "produtoCategoria": "eletronicos",
    "nome": "Smartphone Galaxy S21",
    "preco": 3999.99,
    "urlImagem": "https://exemplo.com/imagens/galaxy-s21.jpg",
    "descricao": "Smartphone Samsung Galaxy S21 com 128GB de armazenamento e 8GB de RAM"
}
```

### Obter Produtos 
- **Método**: GET
- **Endpoint**: `/produto`
- **Resposta de Sucesso**:
```json
[
    {
        "id": "8f9d2a3b-6c87-4f1d-9a5b-2e7d1c8a6b3f",
        "produtoCategoria": "eletronicos",
        "nome": "Smartphone Galaxy S21",
        "preco": 3999.99,
        "urlImagem": "https://exemplo.com/imagens/galaxy-s21.jpg",
        "descricao": "Smartphone Samsung Galaxy S21 com 128GB de armazenamento e 8GB de RAM"
    },
    {
        "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
        "produtoCategoria": "eletronicos",
        "nome": "iPhone 13",
        "preco": 4999.99,
        "urlImagem": "https://exemplo.com/imagens/iphone-13.jpg",
        "descricao": "iPhone 13 com 256GB de armazenamento"
    }
]
```

### Atualizar Produto
- **Método**: PUT
- **Endpoint**: `/produto/{id}`
- **Corpo da Requisição**:
```json
{
    "nome": "Smartphone Galaxy S21 Ultra",
    "preco": 4499.99,
    "descricao": "Smartphone Samsung Galaxy S21 Ultra com 256GB de armazenamento e 12GB de RAM"
}
```
- **Resposta de Sucesso**:
```json
{
    "message": "Produto atualizado com sucesso"
}
```

### Deletar Produto
- **Método**: DELETE
- **Endpoint**: `/produto/{id}`
- **Resposta de Sucesso**:
```json
{
    "message": "Produto deletado com sucesso"
}
```

## Configuração do Ambiente de Desenvolvimento

1. Clone o repositório
2. Instale as dependências:
```
pip install -r requirements.txt
```
3. Configure as variáveis de ambiente:
   - `DATABASE_URL`: URL de conexão com o MySQL
   - `AZURE_COSMOS_URI`: URI do Azure Cosmos DB
   - `AZURE_COSMOS_KEY`: Chave de acesso do Azure Cosmos DB
   - `AZURE_COSMOS_DATABASE`: Nome do banco de dados no Cosmos DB

4. Execute a aplicação:
```
python run.py
```

## Estrutura do Projeto

- `app/`: Pacote principal da aplicação
  - `models/`: Modelos de dados
  - `controllers/`: Controladores de rotas
  - `request/`: Objetos de requisição para validação de dados
  - `response/`: Objetos de resposta
  - `config.py`: Configurações da aplicação
  - `database.py`: Configuração do banco de dados SQL
  - `cosmosdb.py`: Configuração do Azure Cosmos DB 
