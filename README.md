# MON3D
O **MON3D** é um sistema com o objetivo de permitir o monitoramento remoto de impressoras 3D. Ele consiste em uma interface usuário-impressora que não só possibilita ao usuário:
* Enviar arquivos remotamente para a impressão diretamente a partir do seu celular ou computador;
* Monitorar e controlar a temperatura do cabeçote de impressão e da mesa aquecida;
* Monitorar e controlar a posição do cabeçote de impressão
* Acessar um streaming de vídeo ao vivo da impressão.

A espinha dorsal do sistema consiste em:
* Firebase: Armazenamento de dados a serem transmitidos da impressora ao usuário;
* SQLite: Controle de usuário;
* MediaMTX: Servidor utilizado para o streaming de vídeo;
* Flask: Utilizado para definição de rotas e funções do website;
* Debian: Sistema Operacional do servidor.

O diagrama do sistema a seguir apresenta uma ligação lógica entre todas as tecnologias utilizadas.

![Diagrama do sistema](https://github.com/Ianzani/MON3D/blob/main/web/app/static/home/diagrama.png)

**INSTALAÇÃO**

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

### Configurando Ambiente RPi:
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

**UTILIZAÇÃO**

Com o sistema configurado, você já pode começar a monitorar sua impressora remotamente!

Para isso, você primeiro precisa acessar o [Website Mon3D](http://mon3d.igbt.eesc.usp.br/).

Se for a sua *primeira vez* utilizando o Mon3D, você primeiro clicar em [Registrar-se](http://mon3d.igbt.eesc.usp.br/signup), no canto superior direito. Senão, basta clicar em [Entrar](http://mon3d.igbt.eesc.usp.br/login) e informar seu e-mail de registro e senha.

Após o login irá aparecer uma tela com todos os seus dispositivos já registrados.

Após o login você poderá acessar todos os seus dispositivos já registrados ou clicar no símbolo de "+" para *adicionar um novo dispositivo*. Ao adicionar um novo dispositivo, você poderá escolher um ícone e nome para o mesmo e deverá informar a ID (dada pelo endereço MAC da sua Raspberry Pi) e a taxa de transmissão utilizada, em bps.

Quando você *acessar um dispositivo*, irá aparecer uma dashboard. Nesta tela deé possível verificar todas as informações da sua impressora (como temperatura, posição do cabeçote e vídeo da impressão).

Os menus da *esquerda* permitem que você monitore e controle a temperatura do cabeçote de impressão e da mesa aquecida.

Os menus do *meio* permitem que você controle a posição do cabeçote em até 3 eixos, inicie ou pause uma impressão em andamento, além de permitir que você arquivos para impressão diretamente do seu dispositivo.

O menu da *direita* permite a visualização de um vídeo ao vivo e das configurações da impressão.
