# MON3D

Bem-vindo ao tutorial de instalação e configuração do sistema **MON3D** para controle e monitoramento remoto de impressoras 3D.
Antes de começar o processo, verifique a disponibilidade dos seguintes itens: 
* Computador com conexão internet;
* Cartão microSD de 8GB (mínimo) e dispositivo de leitura compatível;
* Placa Raspberry Pi (RPi) e fonte de alimentação apropriada; 
* Rede Wi-Fi ou cabo ethernet com conexão internet;
* Teclado USB + monitor de vídeo e cabo HDMI (opcional).

Inicialmente, o cartão microSD deve ser configurado como uma mídia de instalação (*[boot image](https://en.wikipedia.org/wiki/Boot_image)*) do sistema operacional Ubuntu Server. Para isso, baixe e instale o [Raspberry Pi Imager](https://www.raspberrypi.com/software/) e siga as instruções descritas em [How to install Ubuntu Server on your Raspberry Pi](https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi). Recomenda-se pular o item 5 (*install a desktop*) do tutorial porque o sistema **MON3D** não utiliza interface gráfica.

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
cd ~ && git clone https://github.com/LDFranck/MON3D-RPi
```
Uma vez finalizado o download, execute o script de configuração `mon3d_setup.sh` com o comando:
```
cd ~/MON3D-RPi/ && sudo chmod +x mon3d_setup.sh && sudo ./mon3d_setup.sh
```
✅ Pronto!

O sistema **MON3D** está instalado e pronto para uso. Na próxima vez que ligar sua placa Raspberry Pi ele será executado automaticamente. Fácil não? 😎

