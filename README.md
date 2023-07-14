# MON3D

O **MON3D** é um sistema de monitoramento remoto com o objetivo de permitir o controle de impressoras 3D por meio da Internet. Ele consiste em uma interface usuário-impressora que possibilita ao usuário:

* Monitorar e controlar a temperatura e o status de sua impressora;
* Movimentar os eixos e realizar o *homing* dos mesmos;
* Enviar arquivos e controlar a impressão dos mesmos;
* Monitorar remotamento o funcionamento de sua impressora por meio de uma transmissão ao vivo de vídeo.
<br>

## INSTALAÇÃO

Bem-vindo ao tutorial de instalação e configuração do sistema **MON3D** para controle e monitoramento remoto de impressoras 3D.
Antes de começar o processo, verifique a disponibilidade dos seguintes itens: 
* Computador com conexão internet;
* Cartão microSD de 8GB (mínimo) e dispositivo de leitura compatível;
* Placa Raspberry Pi (RPi) e fonte de alimentação apropriada; 
* Rede Wi-Fi ou cabo ethernet com conexão internet;
* Teclado USB + monitor de vídeo e cabo HDMI (opcional).

Inicialmente, o cartão microSD deve ser configurado como uma mídia de instalação (*[boot image](https://en.wikipedia.org/wiki/Boot_image)*) do sistema operacional Ubuntu Server. Para isso, baixe e instale o [Raspberry Pi Imager](https://www.raspberrypi.com/software/) e siga as instruções descritas em [How to install Ubuntu Server on your Raspberry Pi](https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi). Recomenda-se pular o item 5 (*install a desktop*) do tutorial já que o sistema **MON3D** não utiliza interface gráfica.

Finalizada a configuração, o cartão microSD deve ser inserido no slot da Raspberry Pi e a placa energizada com a fonte de alimentação. Com o sistema ligado, conecte-se ao terminal de controle do Ubuntu Server remotamente através de SSH (vide tutorial), ou fisicamente com o teclado USB + monitor de vídeo e cabo HDMI. Será necessário fazer login com o usuário previamente criado no Raspberry Pi Imager.

> **:warning: Atenção:**\
> Espere algum tempo após a primeira inicialização para que o sistema operacional crie os arquivos de usuário. Caso você não tenha configurado um usuário, o Ubuntu Server utiliza como padrão o `user: ubuntu` e `password: ubuntu` no primeiro login, solicitando a criação de uma nova senha no processo.

**Configurando Ambiente RPi:**
Antes de começar a configuração do ambiente RPi, verifique a conexão da placa com a internet usando o comando `ping -c 1 google.com`. Caso você não tenha configurado a rede Wi-Fi no Raspberry Pi Imager, conecte um cabo ethernet com conexão internet temporariamente para executar esses primeiros procedimentos. Posteriormente a rede Wi-Fi poderá ser adicionada pelo sistema **MON3D**.

Uma vez conectado ao terminal do Ubuntu Server, execute o seguinte comando para atualizar os arquivos e pacotes do sistema para a última versão disponível. Será solicitado a senha do usuário para prosseguir a atualização, e uma confirmação `[Y/n]` na qual basta pressionar a tecla `Enter` do teclado.
```
sudo apt update && sudo apt upgrade
```
Dependendo dos pacotes instalados, será solicitada a reinicialização de alguns módulos do sistema. Para prosseguir, pressione a tecla `Enter` do teclado quando o menu de seleção abrir para reiniciar os serviços e aplicar as atualizações.

Agora vamos verificar a ordem de inicialização do dispositivo para garantir um boot prioritário pelo cartão microSD. Aguarde a finalização da etapa anterior e insira o seguinte comando no terminal: 
```
sudo -E rpi-eeprom-config --edit
```
Utilizando o editor nativo do Ubuntu Server, altere a opção `BOOT_ORDER` para `BOOT_ORDER=0xf41`. Pressione `Ctrl+S` para salvar e `Ctrl+X` para sair do editor. Caso o seu arquivo já esteja com essa configuração ou `BOOT_ORDER` vazio, nenhuma alteração precisa ser feita e você pode sair do editor. Para aplicar as alterações, reinicie a placa RPi com o comando `sudo reboot` e volte ao terminal assim que o processo for finalizado.

Agora utilize o seguinte comando para instalar o gerenciador de versões Git:
```
sudo apt install git
```
Na sequência, use o comando abaixo para baixar os arquivos do sistema **MON3D** para sua placa RPi:
```
cd ~ && git clone https://github.com/Ianzani/MON3D
```
Uma vez finalizado o download, execute o script de configuração `mon3d_setup.sh` com o comando:
```
cd ~/MON3D/hardware/rpi_setup/ && sudo chmod +x mon3d_setup.sh && sudo ./mon3d_setup.sh
```
✅ Pronto!

O sistema **MON3D** está instalado e pronto para uso. Na próxima vez que ligar sua placa Raspberry Pi ele será executado automaticamente. Fácil não? 😎

<br>

## PRIMEIROS PASSOS

Após instalar e configurar o sistema **MON3D** em sua placa Raspberry Pi, deve-se seguir alguns passos iniciais para o cadastramento de sua impressora, sendo eles: conectar sua placa à Internet, criar uma conta no site [MON3D](http://mon3d.igbt.eesc.usp.br/), e cadastrar sua impressora.

**Conectando sua placa à Internet:**

Para conectar sua placa RPi à Internet, basta conectar qualquer dispositivo à rede MON3D, a qual está sendo roteada pela RPi, utilizando a senha **12345678** e acessar o endereço **10.42.0.1**. Acessada a página, deve-se preencher os campos com o nome da sua rede WiFi e sua respectiva senha, seguindo as instruções apresentadas na página. Vale ressaltar que é de **extrema importância copiar o ID de sua Raspberry Pi**, pois este é o único momento em que você terá acesso à ele. Enviada as informações, basta observar se o LED presente em sua placa sairá do modo intermitente para o modo ligado, indicando que a sua placa RPi foi conectada com sucesso em sua rede WiFi. Caso o LED volte ao modo intermitente, repita novamente o processo e, caso o problema persista, entre em contato com o nosso suporte técnico.

**Criando sua conta:**

Conectada a placa à Internet, é necessário a criação de uma conta em nosso site. Para isso, acesse o endereço [http://mon3d.igbt.eesc.usp.br/](http://mon3d.igbt.eesc.usp.br/) e resgistre uma nova conta no canto superior direito da página. Caso já possua uma conta MON3D, ignore este passso e prossiga para o próximo tópico.

**Cadastrando sua impressora:**

Possuindo uma conta MON3D, basta entrar no site utilizando suas credenciais e acessar a aba **DISPOSITIVOS**, caso não tenha sido redirecionado para ela. Como você não possui nenhum dispositivo cadastrado, a página apresentará apenas um botão para o cadastramento de um novo dispositivo. Assim, clique no botão e preencha as informações necessárias corretamente, prestando atenção ao ID da impressora, o qual foi apresentado ao conectar sua placa RPi à Internet, e à taxa de transmissão, a qual deve coincidir com a taxa de transmissão suportada por sua impressora. Caso o ID informado estiver correto, parabéns, você possui sua impressora cadastrada corretamente em nosso sistema, pronta para ser utilizada.

<br>

## NAVEGANDO PELA PLATAFORMA

Acessado o site com sua conta MON3D, você terá acesso a todas as funções disponíveis para o controle de sua conta e de seus dispositivos.

**Acessando o painel de usuário:**

Caso deseja alterar o nome ou senha de sua conta, você poderá acessar o painel de usuário clicando no canto superior direito em seu nome de usuário. Além de poder alterar os dados de sua conta, você poderá também observar o endereço de email utilizado para o cadastro da mesma.

**Acessando o painel da impressora:**

Cadastrado um dispositivo, você poderá acessar o painel de controle do mesmo. Lá você encontrara um painel interativo dividido em 3 colunas principais. Na primeira coluna, você encontrará os botões responsáveis por conectar e desconctar o módulo à sua impressora, o status atual de sua impressora e um monitor de temperatura, o qual mostrará as temperaturas atuais de sua impressora, a referência de temperatura atual de sua impressora e duas caixas de definição de nova referência de temperatura.

Partindo para a segunda coluna, lá você encontrará os botões responsáveis por movimentar o cabeçote e a mesa de sua impressora, podendo também selecionar o passo desses movimentos; os botões de *homing*, tanto o *homing* de todos os eixos como para os eixos únicos; o botão de desenergizar os motores; e os botões de controle de impressão, sendo eles: Iniciar/Retomar, Pausar, Parar, Enviar Arquivo, Carregar Arquivo.

Já para a terceira coluna, você encontrará o monitoramento de vídeo de sua impressora e a aba de configuração de seu dispositivo. Nesta aba de configuração, você poderá alterar o nome dado ao seu dispositivo e a taxa de transmissão configurada no cadastramento de sua impressora. Ademais, você encontrará um botão de remoção de dispositivo, o qual descadastrará a sua impressora de sua conta e tornará possível o recadastro dela na mesma ou em outra conta. **Ressaltamos que é de suma importância anotar o ID de sua impressora, pois você não terá novamente acesso à ele**.

<br>

## SOBRE O PROJETO

Este projeto baseou-se em dois principais núcleos, o da Raspberry Pi e o do servidor. No que tange o da Raspberry Pi, foi utilizado o sistema operacional Ubuntu, devido à sua compatibilidade com as ferramentas do projeto, e foi utilizado a linguagem Python para a programação, devido a sua versatilidade. As principais ferramentas utilizadas neste núcleo foram: FFmpeg, responsável pelo envio do *streaming*; Firebase Admin SDK, biblioteca python utilizada para a comunicação da RPi com o servidor Firebase; e USART, comunicação serial utilizada entre a impressora e a placa RPi. Vale ressaltar que, para a automatização dos processos da RPi, foram criados códigos em *BASH*, permitindo, assim, o início dos códigos sem a necessidade de acessar a Raspberry Pi.

Já para o núcleo do servidor, foi utilizado o servidor fornecido pela Universidade de São Paulo (USP) para hospedar o Flask, framework python responsável tanto pelo *backend* quando pelo *frontend* do nosso site, e o MediaMTX, servidor de mídia responsável por receber e transmitir o *streaming* da impressora. As principais ferramentas utilizadas neste núcleo foram: Firebase Admin SDK; SQLite, banco de dados utilizado para o controle de usuários; Firebase Firestore e Storage, responsável pelo controle dos dispositivos; CSS, HTML, JavaScript e Jinja, responsáveis pela construção do site. No que tange o Flask, foram utilizadas as bibliotecas FlaskLogin, para a autenticação de usuário; FlaskMigrate, responsável pela atualização do banco de dados; FlaskSQLAlchemy, responsável por controlar o banco de dados SQLite; e WTForms, responsável pela criação de *forms* para as páginas, junto aos *forms* HTML.

Na imagem abaixo é possível observar a estrutura resumida do nosso projeto, a qual também está disponível em nosso site [MON3D](http://mon3d.igbt.eesc.usp.br/).

<br>
<div align="center">
  <img src="https://github.com/Ianzani/MON3D/blob/main/web/app/static/home/diagrama2.png" width="700px"/>
</div>
