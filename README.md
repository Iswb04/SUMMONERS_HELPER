(ENG)
This project aims to retrieve and display detailed information about League of Legends champions, helping users quickly identify champions that have natural advantages or disadvantages against others, while also including their titles and roles within the game.
The main champion data is obtained through the Data Dragon (DDragon) API, which provides static information such as name, title, and role.
A custom API was developed using FastAPI to complement the data not available in DDragon, such as the advantage and counter relationships between champions.
The system uses SQLite for local storage and DBeaver for database visualization and management.
Finally, the project was converted into an executable (.exe) using PyInstaller, allowing the application to run without the need to install Python.

(PT/BR)
Este projeto tem como objetivo buscar e exibir informações detalhadas de campeões do League of Legends, ajudando a verificar rapidamente campeões que possuem vantagens ou desvantagens naturais contra outros campeões, 
incluindo também seus títulos e funções dentro do jogo. As informações principais dos campeões são obtidas por meio da API Data Dragon (DDragon), que fornece dados estáticos como nome, título e função. 
Foi desenvolvida uma API própria com FastAPI para complementar os dados que não estão disponíveis na DDragon, como as relações de vantagem (advantage) e desvantagem (counter) entre campeões. 
O sistema utiliza SQLite para armazenamento local e o DBeaver para visualização e gerenciamento do banco de dados.
Por fim, o projeto foi convertido em um executável (.exe) usando o PyInstaller, possibilitando que o aplicativo seja executado sem a necessidade de instalar o Python
