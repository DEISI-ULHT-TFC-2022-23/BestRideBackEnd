# TFC BestRide Backend

## Correr o Projeto
1. Ir para a pasta onde pretende fazer o download do código, e abrir um terminal.
2. Clonar o repositório 
```
git clone https://github.com/diogocerqueira-22002160/BestRideBackend.git
```
3. Instalar o Python 3.11
4. Instalar dependências
```
pip install pipenv
pipenv install
```
5. Entrar no ambiente virtual
```
pipenv shell
```
6. Efetuar as migrações
```
python manage.py makemigrations
python manage.py migrate
```
7. Por fim basta correr o programa em si.
```
python manage.py runserver
```
Se tudo correu como esperado, o browser ira ter um link com a aplicação a correr localmente por exemplo no localhost:8000.
Recomendamos a utilização da ferramenta Postman para testar as rotas da API. 
Juntamente com este projeto está um ficheiro JSON com exemplos de requests para cada rota, que pode ser importado para o Postman.
[Clique aqui para vizualizar o ficheiro JSON do Postman](BestRide.postman_collection.json)